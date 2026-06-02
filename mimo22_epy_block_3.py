"""
Embedded Python Block: RX 信宿 (数据链路层)

DLL 帧格式:
  access_code(8B) + packet_len(2B,仅payload长度) + SN(2B) + payload

SN=0  → test 模式: 把 payload 数据打印到终端
SN>0  → transfer 模式: 收集各帧 payload，全部到齐后写入文件

ACCESS_CODE = [0xac, 0xdd, 0xa4, 0xe2, 0xf2, 0x8c, 0x20, 0xfc]
"""

import numpy as np
from gnuradio import gr
import struct
import os
import random as _random
import collections as _coll
import pmt

ACCESS_CODE      = bytes([0xac, 0xdd, 0xa4, 0xe2, 0xf2, 0x8c, 0x20, 0xfc])
AC_LEN           = len(ACCESS_CODE)   # 8
HEADER_LEN       = AC_LEN + 2 + 2     # access_code + packet_len + SN = 12
MAX_PAYLOAD      = 488                # 最大有效载荷长度（字节）
SAVE_AFTER_CYCLES = 5                 # 累积 5 轮完整文件后投票保存

_rng = _random.Random(0xDEADBEEF)
_SCRAMBLE_KEY = bytes([_rng.randint(0, 255) for _ in range(MAX_PAYLOAD)])
del _rng


def _descramble(payload):
    key = _SCRAMBLE_KEY[:len(payload)]
    return bytes([b ^ k for b, k in zip(payload, key)])


class blk(gr.sync_block):
    """RX 信宿：在字节流中搜索 access code，解析 DLL 帧"""

    def __init__(self, file_path="./receive_a.jpg"):
        gr.sync_block.__init__(
            self,
            name='RX Sink',
            in_sig=[np.uint8],
            out_sig=[]
        )
        self.file_path = file_path

        self.message_port_register_in(pmt.intern('auto'))
        self.set_msg_handler(pmt.intern('auto'), self._handle_auto_msg)

        self._buf = bytearray()
        self._total_in = 0
        self._logged_raw = False
        self._after_auto = False
        self._after_auto_bytes = 0
        self._after_auto_ac = 0
        self._after_auto_next_report = 50000

        # test 统计
        self._test_cnt = 0

        # transfer 收集
        self._frames = {}         # sn -> 最新 payload
        self._frames_votes = {}   # sn -> 多轮 payload 列表
        self._max_sn = 0          # 目前收到过的最大 SN
        self._transfer_active = False
        self._zero_after_transfer = 0
        self._got_last_frame = False
        self._cycle_count = 0
        self._transfer_done = False

    def _handle_auto_msg(self, msg):
        self._after_auto = True
        self._after_auto_bytes = 0
        self._after_auto_ac = 0
        self._after_auto_next_report = 50000
        print("[RX] 开始统计 AUTO 后字节和 AC 命中")

    # ---------------------------------------------------------------- work
    def work(self, input_items, output_items):
        data = input_items[0]
        self._buf.extend(data.tobytes())
        self._total_in += len(data)

        if not self._logged_raw and self._total_in >= 20:
            raw = bytes(self._buf[:min(24, len(self._buf))])
            print(f"[RX] 首批字节: {raw.hex(' ')}")
            self._logged_raw = True

        if self._after_auto:
            self._after_auto_bytes += len(data)
            chunk = bytes(data)
            pos = 0
            while True:
                idx = chunk.find(ACCESS_CODE, pos)
                if idx < 0:
                    break
                self._after_auto_ac += 1
                pos = idx + 1
            while self._after_auto_bytes >= self._after_auto_next_report:
                print(f"[RX DIAG] AUTO后收到 {self._after_auto_bytes} 字节, "
                      f"AC命中 {self._after_auto_ac} 次, "
                      f"buf_len={len(self._buf)}")
                self._after_auto_next_report += 50000

        self._parse()
        return len(data)

    # ---------------------------------------------------------------- parse
    def _parse(self):
        """在缓冲中搜索 access code，逐帧解析"""
        while True:
            # 在缓冲中搜索 access code
            idx = self._buf.find(ACCESS_CODE)
            if idx < 0:
                # 没找到；保留最后 AC_LEN-1 字节防止跨块
                keep = AC_LEN - 1
                if len(self._buf) > keep:
                    del self._buf[:len(self._buf) - keep]
                return

            # 找到 access code 但 header 数据不够
            if len(self._buf) < idx + HEADER_LEN:
                # 丢弃 access code 之前的数据，等待更多
                if idx > 0:
                    del self._buf[:idx]
                return

            # 读取 header
            pkt_len = struct.unpack_from('>H', self._buf, idx + AC_LEN)[0]
            sn      = struct.unpack_from('>H', self._buf, idx + AC_LEN + 2)[0]

            # 合法性检查
            if pkt_len == 0 or pkt_len > MAX_PAYLOAD:
                # 非法，跳过这一个 access code 字节继续搜索
                del self._buf[:idx + 1]
                continue

            # 检查 payload 是否到齐
            frame_end = idx + HEADER_LEN + pkt_len
            if len(self._buf) < frame_end:
                # payload 还没到
                if idx > 0:
                    del self._buf[:idx]
                return

            # 提取 payload 并解扰
            payload = _descramble(bytes(self._buf[idx + HEADER_LEN: frame_end]))
            del self._buf[:frame_end]

            # 分发处理
            if sn == 0:
                self._handle_test(payload)
            else:
                self._handle_transfer(sn, payload)

    # ---------------------------------------------------------------- test
    def _handle_test(self, payload):
        """SN=0 test 帧"""
        # 如果刚完成 transfer，检查是否连续收到几个 test 帧就可以保存文件
        if self._transfer_active:
            self._zero_after_transfer += 1
            if self._zero_after_transfer >= 2:
                if not self._transfer_done:
                    self._save_file()
                    self._transfer_done = True
                self._transfer_active = False
                self._zero_after_transfer = 0
        else:
            self._zero_after_transfer = 0

        self._test_cnt += 1
        if self._test_cnt <= 20 or self._test_cnt % 100 == 0:
            vals = list(payload[:40])
            print(f"[TEST #{self._test_cnt}] len={len(payload)} "
                  f"vals={vals}{'...' if len(payload) > 40 else ''}")

    # ---------------------------------------------------------------- transfer
    def _handle_transfer(self, sn, payload):
        """SN>0 transfer 帧，存入字典等待拼装"""
        if self._transfer_done:
            return

        if not self._transfer_active:
            print(f"[TRANSFER] 开始接收，首帧 SN={sn}")
            self._transfer_active = True
            self._zero_after_transfer = 0

        self._frames[sn] = payload
        self._frames_votes.setdefault(sn, []).append(payload)
        if sn > self._max_sn:
            self._max_sn = sn
        if len(payload) < MAX_PAYLOAD:
            self._got_last_frame = True

        n_recv = len(self._frames)
        if n_recv <= 5 or n_recv % 10 == 0:
            print(f"[TRANSFER] 已收 {n_recv} 帧 (max_sn={self._max_sn})")

        if self._got_last_frame and self._max_sn > 0 and len(self._frames) == self._max_sn:
            self._cycle_count += 1
            print(f"[TRANSFER] 第{self._cycle_count}次全部{self._max_sn}帧到齐")
            if self._cycle_count >= SAVE_AFTER_CYCLES:
                print(f"[TRANSFER] 已积累{self._cycle_count}轮，开始投票保存")
                self._save_file()
                self._transfer_active = False
                self._transfer_done = True
            self._got_last_frame = False

    def _vote_payload(self, votes):
        length_mode = _coll.Counter(len(v) for v in votes).most_common(1)[0][0]
        valid_votes = [v for v in votes if len(v) == length_mode]
        return bytes([
            _coll.Counter(v[i] for v in valid_votes).most_common(1)[0][0]
            for i in range(length_mode)
        ])

    # ---------------------------------------------------------------- save
    def _save_file(self):
        """按 SN 顺序拼装并写入文件，使用逐字节多数投票"""
        if not self._frames_votes:
            print("[TRANSFER] 无数据帧，跳过保存")
            return

        max_sn = self._max_sn
        present = sorted(self._frames_votes.keys())
        total_bytes = 0

        d = os.path.dirname(self.file_path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(self.file_path, 'wb') as f:
            for sn in range(1, max_sn + 1):
                votes = self._frames_votes.get(sn)
                if not votes:
                    print(f"[TRANSFER] 警告: SN={sn} 丢失")
                    continue
                payload = self._vote_payload(votes)
                f.write(payload)
                total_bytes += len(payload)

        avg_votes = sum(len(votes) for votes in self._frames_votes.values()) / max(len(self._frames_votes), 1)
        print(f"[TRANSFER] 文件保存完成: {self.file_path} "
              f"({total_bytes} 字节, 收到 {len(present)}/{max_sn} 帧, 平均{avg_votes:.1f}票/帧)")

        # 重置
        self._frames.clear()
        self._frames_votes.clear()
        self._max_sn = 0
        self._got_last_frame = False
        self._cycle_count = 0

    # ---------------------------------------------------------------- stop
    def stop(self):
        """flowgraph 停止时，如有未完成的 transfer 也保存"""
        if self._transfer_active and self._frames_votes and not self._transfer_done:
            print("[RX] flowgraph 停止，保存当前投票结果")
            self._save_file()
        return True
