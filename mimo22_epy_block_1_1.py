"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt


class blk(gr.sync_block):
    """Correlation Estimator - 使用归一化互相关检测导频序列并标记起始位置

    参数:
        symbols: 导频序列（复数列表）
        sps: 每符号采样数
        threshold: 归一化相关阈值 (0~1)
        tag_name: 检测到导频时输出的 tag 名称
    """

    def __init__(self, symbols=[], sps=1, threshold=0.7, tag_name="corr_start"):
        gr.sync_block.__init__(
            self,
            name='Correlation Estimator',
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )

        self.sps = int(sps)
        self.threshold = float(threshold)
        self.tag_name = str(tag_name)

        # 生成参考序列（支持升采样）
        symbols_arr = np.array(symbols, dtype=np.complex64)
        if self.sps > 1:
            self.ref = np.repeat(symbols_arr, self.sps)
        else:
            self.ref = symbols_arr.copy()

        self.ref_len = len(self.ref)
        if self.ref_len == 0:
            self.ref = np.array([1 + 0j], dtype=np.complex64)
            self.ref_len = 1

        self.ref_conj = np.conj(self.ref)  # 用于直接点积计算
        self.ref_energy = float(np.sum(np.abs(self.ref) ** 2))

        # 设置 history 以支持缓冲区边界处的相关计算
        self.set_history(self.ref_len)

        # 最小检测间距 (防止同一导频序列产生多次检测)
        self.last_tag_abs = -(self.ref_len * 10)

    def set_threshold(self, threshold):
        """运行时更新阈值"""
        self.threshold = float(threshold)

    def work(self, input_items, output_items):
        inp = input_items[0]  # 长度 = nout + ref_len - 1 (包含 history)
        out = output_items[0]
        nout = len(out)

        # 直通数据（跳过 history 部分）
        out[:] = inp[self.ref_len - 1: self.ref_len - 1 + nout]

        if nout == 0:
            return nout

        nread = self.nitems_read(0)
        total_inp = nout + self.ref_len - 1

        # np.correlate(x, h, 'valid')[i] = sum_k x[i+k] * conj(h[k])
        # numpy 会自动对第二个参数取共轭，所以传入 self.ref 而非 self.ref_conj
        corr_abs = np.abs(np.correlate(inp[:total_inp], self.ref, mode='valid'))

        # ========== 滑窗能量归一化 ==========
        inp_sq = np.abs(inp[:total_inp]).astype(np.float64) ** 2
        cumsum = np.cumsum(inp_sq)

        win_energy = np.empty(nout, dtype=np.float64)
        win_energy[0] = cumsum[self.ref_len - 1]
        if nout > 1:
            win_energy[1:] = (cumsum[self.ref_len: self.ref_len + nout - 1]
                              - cumsum[: nout - 1])

        # 归一化: rho = |corr| / sqrt(E_window * E_ref)
        denom = np.sqrt(np.maximum(win_energy * self.ref_energy, 1e-30))
        norm_corr = corr_abs[:nout] / denom

        # ========== 峰值检测 ==========
        above_mask = norm_corr > self.threshold
        if not np.any(above_mask):
            return nout

        above_indices = np.where(above_mask)[0]

        # 将连续超阈值区域分组，在每组中找峰值
        breaks = np.where(np.diff(above_indices) > 1)[0] + 1
        groups = np.split(above_indices, breaks)

        min_distance = self.ref_len

        for group in groups:
            if len(group) == 0:
                continue

            # 在组内找最大归一化相关值的位置
            peak_idx = group[np.argmax(norm_corr[group])]

            # 只处理能映射到有效输出位置的峰值
            # correlation at index i => ZC starts at inp[i]
            # inp[i] 的绝对位置 = nread - (ref_len - 1) + i
            # 要使 tag 落在当前输出范围内: i >= ref_len - 1
            if peak_idx < self.ref_len - 1:
                continue

            # ZC 序列开始的绝对流位置
            zc_start_abs = nread + (peak_idx - (self.ref_len - 1))

            # 距上次检测的去重检查
            if zc_start_abs - self.last_tag_abs < min_distance:
                continue

            # 添加 tag 标记导频起始位置
            self.add_item_tag(
                0,
                zc_start_abs,
                pmt.intern(self.tag_name),
                pmt.from_double(float(norm_corr[peak_idx]))
            )
            self.last_tag_abs = zc_start_abs

        return nout