"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt

# h11表示 tx1 到 rx1 的信道，h21 表示 tx2 到 rx1 的信道，h12 表示 tx1 到 rx2 的信道，h22 表示 tx2 到 rx2 的信道
#
#
#

class blk(gr.basic_block):  # 使用 basic_block 实现灵活的帧处理
    """2x2 MIMO 检测块，使用 ZF (迫零) 算法"""

    def __init__(self, frame_len=1008):  # frame_len = 应用层总帧长(QPSK符号数)
        """函数参数会在 GRC 中显示为块的参数"""
        gr.basic_block.__init__(
            self,
            name='MIMO_Detection',   # 将在 GRC 中显示为块名称
            in_sig=[np.complex64, np.complex64],
            out_sig=[np.complex64, np.complex64]
        )
        
        #debug
        self.message_port_register_out(pmt.intern("message_out"))#注册输出端口

        # 参数设置
        self.sps = 1  # 升采样因子
        self.zero_len = 32 * self.sps  # 零序列长度
        self.zc_len = 61 * self.sps  # ZC 序列长度
        # frame_len 直接就是每路 QPSK 符号数（即 RF 数据区长度）
        self.data_len = frame_len * self.sps
        # 前导结构: zero(32) + zc1(61) + zero(32) + zc2(61) + zero(32) = 218
        self.preamble_len = self.zero_len + self.zc_len + self.zero_len + self.zc_len + self.zero_len
        self.frame_len = self.preamble_len + self.data_len  # 总帧长度 = 218 + 1000 = 1218

        # ZC 序列生成
        self.zc1 = np.array([complex(np.exp(-1j * np.pi * 25 * n * (n + 1) / 61)) for n in range(61)])  # ZC1 序列
        self.zc2 = np.array([complex(np.exp(-1j * np.pi * 34 * n * (n + 1) / 61)) for n in range(61)])  # ZC2 序列
        self.zc1_up = np.repeat(self.zc1, self.sps)  # ZC1 升采样
        self.zc2_up = np.repeat(self.zc2, self.sps)  # ZC2 升采样

        # ZC 在帧内的预期位置
        self.zc1_pos = self.zero_len  # = 32
        self.zc2_pos = self.zero_len + self.zc_len + self.zero_len  # = 32 + 61 + 32 = 125

        # 状态变量
        self.frame_start_idx = -1  # 帧起始的相对索引，-1 表示未找到

        # 诊断计数器
        self._diag_calls = 0
        self._diag_tag_found = 0
        self._diag_tag_missing = 0
        self._diag_frames_out = 0
        self._diag_last_print = 0
        import time as _time
        self._diag_t0 = _time.time()

    def general_work(self, input_items, output_items):
        """执行 MIMO 检测，使用 ZF 算法的帧处理模式

        关键点：以 RX1 为基准同步
        """
        rx1 = input_items[0]  # 接收端 1 的输入
        rx2 = input_items[1]  # 接收端 2 的输入
        out_rx1 = output_items[0]  # 接收端 1 的输出
        out_rx2 = output_items[1]  # 接收端 2 的输出

        nin0 = len(rx1)
        nin1 = len(rx2)
        nin = min(nin0, nin1)

        # 如果没有输入数据，直接返回
        if nin == 0:
            return 0

        # 诊断：每5秒打印一次统计
        import time as _time
        self._diag_calls += 1
        now = _time.time()
        if now - self._diag_last_print >= 5.0:
            elapsed = now - self._diag_t0
            print(f"[EPY2 DIAG] t={elapsed:.0f}s calls={self._diag_calls} "
                  f"tag_found={self._diag_tag_found} tag_miss={self._diag_tag_missing} "
                  f"frames_out={self._diag_frames_out} nin={nin}")
            self._diag_last_print = now

        # 获取当前输入块的绝对位置范围（分别对应两个端口）
        abs_start0 = self.nitems_read(0)
        abs_end0 = abs_start0 + nin0
        abs_start1 = self.nitems_read(1)
        abs_end1 = abs_start1 + nin1

        # 第一步：以 RX1 为基准，寻找帧起始标记
        if self.frame_start_idx < 0:
            # 使用 get_tags_in_range（绝对偏移）获取 RX1 上的帧起始标记
            h11_tags = self.get_tags_in_range(0, abs_start0, abs_end0, pmt.intern("h11_corr_start"))
            if h11_tags:
                self._diag_tag_found += 1
                # 找到帧起始，保存其相对于当前输入块的索引
                # 标签在 ZC1 起始处，所以帧起始是标签位置减去 zero_len
                tag_rel = h11_tags[0].offset - abs_start0
                self.frame_start_idx = tag_rel - self.zero_len
                if self.frame_start_idx < 0:
                    # 帧起始在当前缓冲区之前（ZC 标签偏移 < zero_len）
                    # 跳过当前帧的剩余部分（跳到帧末尾），让下次能找到下一帧
                    skip = self.frame_len + self.frame_start_idx  # = frame_len - |offset|
                    if skip <= 0:
                        skip = 1
                    safe = min(skip, nin)  # 两路消耗相同量，保持Δ不变
                    self.consume(0, safe)
                    self.consume(1, safe)
                    self.frame_start_idx = -1
                    return 0
            else:
                self._diag_tag_missing += 1
                # 尚未找到帧起始，消费大部分数据以避免死循环
                skip = max(1, nin - self.frame_len)
                self.consume(0, skip)
                self.consume(1, skip)
                return 0

        # 若帧起始偏移 > 0，先消耗偏移前数据，让调度器下次能提供足够数据
        if self.frame_start_idx > 0:
            skip = self.frame_start_idx
            safe = min(skip, nin)  # 两路消耗相同量，保持Δ不变
            self.consume(0, safe)
            self.consume(1, safe)
            self.frame_start_idx -= safe  # 减去已消耗量；=0时进入帧处理
            return 0

        # 检查是否有足够数据处理完整帧 (frame_start_idx 此时为 0)
        if self.frame_len > nin0 or self.frame_len > nin1:
            return 0

        # 检查输出缓冲区是否足够
        if len(out_rx1) < self.data_len or len(out_rx2) < self.data_len:
            return 0

        # 数据足够，从当前输入块中提取完整帧
        frame_rx1 = rx1[self.frame_start_idx : self.frame_start_idx + self.frame_len]
        frame_rx2 = rx2[self.frame_start_idx : self.frame_start_idx + self.frame_len]

        # 帧的绝对位置范围
        frame_abs_start0 = abs_start0 + self.frame_start_idx
        frame_abs_end0 = frame_abs_start0 + self.frame_len
        frame_abs_start1 = abs_start1 + self.frame_start_idx
        frame_abs_end1 = frame_abs_start1 + self.frame_len

        # 第二步：在完整帧范围内获取各信道的标签
        # 端口 0 (rx1): h11_corr_start, h21_corr_start
        h11_tags = self.get_tags_in_range(0, frame_abs_start0, frame_abs_end0, pmt.intern("h11_corr_start"))
        h21_tags = self.get_tags_in_range(0, frame_abs_start0, frame_abs_end0, pmt.intern("h21_corr_start"))
        # 端口 1 (rx2): h22_corr_start, h12_corr_start
        h22_tags = self.get_tags_in_range(1, frame_abs_start1, frame_abs_end1, pmt.intern("h22_corr_start"))
        h12_tags = self.get_tags_in_range(1, frame_abs_start1, frame_abs_end1, pmt.intern("h12_corr_start"))

        def get_tag_offset_p0(tags, default_pos):
            """获取端口0标签相对帧起始的偏移，若未找到则使用默认位置"""
            return (tags[0].offset - frame_abs_start0) if tags else default_pos

        def get_tag_offset_p1(tags, default_pos):
            """获取端口1标签相对帧起始的偏移，若未找到则使用默认位置"""
            return (tags[0].offset - frame_abs_start1) if tags else default_pos

        if not h11_tags and not h21_tags:
            # 未找到 RX1 上的必要标签，跳过并继续搜索
            self.consume(0, 1)
            self.consume(1, 1)
            self.frame_start_idx = -1
            return 0

        # 第三步：信道估计
        h11_offset = get_tag_offset_p0(h11_tags, self.zc1_pos)
        h21_offset = get_tag_offset_p0(h21_tags, self.zc2_pos)
        # 使用端口0的偏移(基于Δ=0同步假设)，避免端口1标签误检导致h22/h12估计错误
        h22_offset = h21_offset
        h12_offset = h11_offset

        # 确保偏移在有效范围内
        h11_offset = max(0, min(h11_offset, self.frame_len - self.zc_len))
        h21_offset = max(0, min(h21_offset, self.frame_len - self.zc_len))
        h22_offset = max(0, min(h22_offset, self.frame_len - self.zc_len))
        h12_offset = max(0, min(h12_offset, self.frame_len - self.zc_len))

        # 提取 ZC 部分并估计信道
        y11 = frame_rx1[h11_offset : h11_offset + self.zc_len]  # rx1 接收的 tx1 信号
        h11 = np.mean(y11 / self.zc1_up) if len(y11) == self.zc_len else 0  # h11 信道估计

        y21 = frame_rx1[h21_offset : h21_offset + self.zc_len]  # rx1 接收的 tx2 信号
        h21 = np.mean(y21 / self.zc2_up) if len(y21) == self.zc_len else 0  # h21 信道估计

        y22 = frame_rx2[h22_offset : h22_offset + self.zc_len]  # rx2 接收的 tx2 信号
        h22 = np.mean(y22 / self.zc2_up) if len(y22) == self.zc_len else 0  # h22 信道估计

        y12 = frame_rx2[h12_offset : h12_offset + self.zc_len]  # rx2 接收的 tx1 信号
        h12 = np.mean(y12 / self.zc1_up) if len(y12) == self.zc_len else 0  # h12 信道估计

        # 数据起始位置（前导之后）
        data_start = self.preamble_len

        # 提取数据部分
        y1_data = frame_rx1[data_start : data_start + self.data_len]  # rx1 接收的数据
        y2_data = frame_rx2[data_start : data_start + self.data_len]  # rx2 接收的数据

        # ZF (迫零) 检测
        # 信道模型: y1 = h11*x1 + h21*x2, y2 = h12*x1 + h22*x2
        # H^-1 = (1/det) * [[h22, -h21], [-h12, h11]], det = h11*h22 - h21*h12
        det = h11 * h22 - h21 * h12  # 采用 ZF 算法计算检测矩阵行列式
        if abs(det) > 1e-10:
            x1_est = (h22 * y1_data - h21 * y2_data) / det  # 估计的 tx1 数据
            x2_est = (h11 * y2_data - h12 * y1_data) / det  # 估计的 tx2 数据
            if self._diag_frames_out < 20 or self._diag_frames_out % 50 == 0:
                delta = abs_start1 - abs_start0
                print(f"[ZF #{self._diag_frames_out}] h11={h11:.3f} h22={h22:.3f} det={det:.3e} "
                      f"Δ={delta} h22off={h22_offset} x1_abs={float(np.mean(np.abs(x1_est))):.3f}")
        else:
            # 矩阵奇异，直接输出接收数据
            x1_est = y1_data
            x2_est = y2_data
            delta = abs_start1 - abs_start0
            print(f"[ZF #{self._diag_frames_out}] SINGULAR h11={h11:.3f} h22={h22:.3f} det={det:.3e} "
                  f"Δ={delta} h22off={h22_offset}")

        # 输出检测结果
        n_out = min(len(x1_est), len(x2_est), len(out_rx1), len(out_rx2))
        out_rx1[:n_out] = x1_est[:n_out].astype(np.complex64)
        out_rx2[:n_out] = x2_est[:n_out].astype(np.complex64)

        # 添加数据包长度标签
        self.add_item_tag(0, self.nitems_written(0), pmt.intern("rx1_packet_len"), pmt.from_long(n_out))
        self.add_item_tag(1, self.nitems_written(1), pmt.intern("rx2_packet_len"), pmt.from_long(n_out))

        # 消费已处理的帧数据，重置状态以寻找下一帧
        consumed = self.frame_start_idx + self.frame_len
        self.consume(0, consumed)
        self.consume(1, consumed)
        self.frame_start_idx = -1  # 重置帧起始标记
        self._diag_frames_out += 1

        return n_out