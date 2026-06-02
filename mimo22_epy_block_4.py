"""
Embedded Python Block: TX 信源 (数据链路层)

DLL 帧格式:
  access_code(8B) + packet_len(2B,仅payload长度) + SN(2B) + payload

SN=0  → test 模式: payload = 0..50 循环整数
SN>0  → transfer 模式: payload = 目标文件分片 (SN从1开始递增)

ACCESS_CODE = [0xac, 0xdd, 0xa4, 0xe2, 0xf2, 0x8c, 0x20, 0xfc]
"""

import numpy as np
from gnuradio import gr
import pmt
import struct
import threading
import random as _random

ACCESS_CODE = bytes([0xac, 0xdd, 0xa4, 0xe2, 0xf2, 0x8c, 0x20, 0xfc])
MAX_PAYLOAD = 488   # 每DLL帧最大payload字节数
N_LOOPS     = 50    # 文件循环重发次数

_rng = _random.Random(0xDEADBEEF)
_SCRAMBLE_KEY = bytes([_rng.randint(0, 255) for _ in range(MAX_PAYLOAD)])
del _rng


def _scramble(payload):
    key = _SCRAMBLE_KEY[:len(payload)]
    return bytes([b ^ k for b, k in zip(payload, key)])


class blk(gr.sync_block):
    """TX 信源：通过消息切换 test/transfer 模式，输出DLL帧字节流"""

    def __init__(self, file_path="/home/adminx/mytest/a.jpg", payload_data_len=488):
        gr.sync_block.__init__(
            self,
            name='TX Source',
            in_sig=None,
            out_sig=[np.uint8]
        )
        self.message_port_register_in(pmt.intern('test/transfer'))
        self.set_msg_handler(pmt.intern('test/transfer'), self._handle_msg)

        self.file_path = file_path
        self.payload_data_len = MAX_PAYLOAD  # 忽略外部传入，用内部常量

        self._mode = 0          # 0=test, 1=transfer
        self._buf = bytearray()
        self._lock = threading.Lock()

        self._test_ctr = 0      # test 数据计数器 (0-50 循环)
        self._file_data = b''
        self._file_offset = 0
        self._sn = 0            # 当前 transfer SN (从1开始)
        self._transfer_done = False
        self._loop_count = 0
        self._n_frames = 0

    # ---------------------------------------------------------------- message
    def _handle_msg(self, msg):
        """接收切换消息"""
        try:
            if pmt.is_pair(msg):
                mode = int(pmt.to_long(pmt.cdr(msg)))
            elif pmt.is_integer(msg):
                mode = int(pmt.to_long(msg))
            else:
                return
        except Exception:
            return

        with self._lock:
            if mode == 1 and self._mode == 0:
                try:
                    with open(self.file_path, 'rb') as f:
                        self._file_data = f.read()
                    self._file_offset = 0
                    self._sn = 1
                    self._transfer_done = False
                    self._loop_count = 0
                    self._n_frames = (len(self._file_data) + MAX_PAYLOAD - 1) // MAX_PAYLOAD
                    print(f"[TX] 开始传输: {self.file_path} "
                          f"({len(self._file_data)} 字节, {self._n_frames} DLL帧, 循环 {N_LOOPS} 次)")
                except Exception as e:
                    print(f"[TX] 文件读取失败: {e}")
                    return
                self._mode = 1
            elif mode == 0:
                print("[TX] 切换到 test 模式")
                self._mode = 0

    # ---------------------------------------------------------------- frame builders
    def _make_test_frame(self):
        """SN=0, payload=0..50循环，加扰后发送"""
        payload = bytes([self._test_ctr % 51 for _ in range(MAX_PAYLOAD)])
        self._test_ctr = (self._test_ctr + MAX_PAYLOAD) % 51
        return ACCESS_CODE + struct.pack('>HH', MAX_PAYLOAD, 0) + _scramble(payload)

    def _make_transfer_frame(self):
        """SN=递增, payload=文件分片; 每轮结束后按 N_LOOPS 重发"""
        remaining = len(self._file_data) - self._file_offset
        if remaining <= 0:
            self._loop_count += 1
            if self._loop_count >= N_LOOPS:
                self._transfer_done = True
                self._mode = 0
                print(f"[TX] 传输完成，共循环 {self._loop_count} 次 "
                      f"({self._n_frames} 帧/轮)，返回 test 模式")
                return self._make_test_frame()

            self._file_offset = 0
            self._sn = 1
            if self._loop_count <= 3 or self._loop_count % 10 == 0:
                print(f"[TX] 第 {self._loop_count}/{N_LOOPS} 轮完成，重新发送")
            remaining = len(self._file_data)

        chunk = self._file_data[self._file_offset:self._file_offset + MAX_PAYLOAD]
        pkt_len = len(chunk)
        frame = ACCESS_CODE + struct.pack('>HH', pkt_len, self._sn) + _scramble(chunk)
        self._file_offset += pkt_len
        if self._loop_count == 0 and (self._sn <= 3 or self._sn % 10 == 0):
            print(f"[TX] transfer SN={self._sn} pkt_len={pkt_len} "
                  f"offset={self._file_offset}/{len(self._file_data)}")
        self._sn += 1
        return frame

    # ---------------------------------------------------------------- work
    def work(self, input_items, output_items):
        out = output_items[0]
        n = len(out)
        produced = 0

        with self._lock:
            # 先消耗缓冲中的残余
            if self._buf:
                to_copy = min(n, len(self._buf))
                out[:to_copy] = np.frombuffer(bytes(self._buf[:to_copy]),
                                              dtype=np.uint8)
                del self._buf[:to_copy]
                produced = to_copy

            # 生成新帧填充剩余输出
            while produced < n:
                if self._mode == 1 and not self._transfer_done:
                    frame = self._make_transfer_frame()
                else:
                    frame = self._make_test_frame()

                can_copy = min(n - produced, len(frame))
                out[produced:produced + can_copy] = np.frombuffer(
                    frame[:can_copy], dtype=np.uint8)
                if can_copy < len(frame):
                    self._buf.extend(frame[can_copy:])
                produced += can_copy

        return produced
