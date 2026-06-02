#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: mimo22
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import mimo22_epy_block_1 as epy_block_1  # embedded python block
import mimo22_epy_block_1_0 as epy_block_1_0  # embedded python block
import mimo22_epy_block_1_1 as epy_block_1_1  # embedded python block
import mimo22_epy_block_1_1_0 as epy_block_1_1_0  # embedded python block
import mimo22_epy_block_2 as epy_block_2  # embedded python block
import mimo22_epy_block_3 as epy_block_3  # embedded python block
import mimo22_epy_block_4 as epy_block_4  # embedded python block
import mimo22_vr as vr  # embedded python module
import numpy as np
import sip



class mimo22(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "mimo22", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("mimo22")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "mimo22")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.zc2 = zc2 = [complex(np.exp(-1j * np.pi * 34 * n * (n + 1) / 61)) for n in range(61)]
        self.zc1 = zc1 = [complex(np.exp(-1j * np.pi * 25 * n * (n + 1) / 61)) for n in range(61)]
        self.sample_rate = sample_rate = 4
        self.nfilts = nfilts = 32
        self.zc_modulator = zc_modulator = digital.constellation_rect([-0.707-0.707j, -0.707+0.707j, 0.707+0.707j, 0.707-0.707j], [0, 1, 3, 2],
        4, 2, 2, 1, 1).base()
        self.zc2_rrced = zc2_rrced = vr.rrc_interpolation_filter(zc2, 4, 1, 0.35, 11*sample_rate)
        self.zc1_rrced = zc1_rrced = vr.rrc_interpolation_filter(zc1, 4, 1, 0.35, 11*sample_rate)
        self.tx2_preamble = tx2_preamble = [0]*32 + [0]*61 +[0]*32 + zc2 + [0]*32
        self.tx1_preamble = tx1_preamble = [0]*32 + zc1 + [0]*32 + [0]*61 + [0]*32
        self.threshold = threshold = 0.5
        self.samp_rate = samp_rate = 32000
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(nfilts, nfilts*sample_rate,1, 0.35, (11*sample_rate*nfilts))
        self.gain = gain = 35
        self.file_path = file_path = "/home/adminx/mytest2/a.jpg"
        self.data_modulator = data_modulator = digital.constellation_rect([-0.707-0.707j, -0.707+0.707j, 0.707+0.707j, 0.707-0.707j], [0, 1, 3, 2],
        4, 2, 2, 1, 1).base()
        self.data_len = data_len = 496
        self.center_freq = center_freq = 2e9
        self.button_msg = button_msg = 0

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,2)),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_source_0.set_center_freq(int(center_freq), 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0.set_gain(gain, 0)

        self.uhd_usrp_source_0.set_center_freq(int(center_freq), 1)
        self.uhd_usrp_source_0.set_antenna("RX2", 1)
        self.uhd_usrp_source_0.set_gain(gain, 1)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,2)),
            ),
            "",
        )
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_sink_0.set_center_freq(int(center_freq), 0)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_sink_0.set_gain(gain, 0)

        self.uhd_usrp_sink_0.set_center_freq(int(center_freq), 1)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 1)
        self.uhd_usrp_sink_0.set_gain(gain, 1)
        self.root_raised_cosine_filter_0_0 = filter.interp_fir_filter_ccf(
            4,
            firdes.root_raised_cosine(
                4,
                sample_rate,
                1.0,
                0.35,
                (11*sample_rate)))
        self.root_raised_cosine_filter_0 = filter.interp_fir_filter_ccf(
            4,
            firdes.root_raised_cosine(
                4,
                sample_rate,
                1.0,
                0.35,
                (11*sample_rate)))
        self.qtgui_time_sink_x_0_0_1_1_1_4_0 = qtgui.time_sink_c(
            8192, #size
            samp_rate, #samp_rate
            "in2", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_y_axis(-2, 2)

        self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_1_1_1_4_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_1_1_1_4_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_1_1_1_4_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0_1_1_1_4_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_1_1_1_4_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_1_1_1_4_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_1_1_1_4_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_1_1_1_4_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_1_1_1_4_0_win)
        self.qtgui_time_sink_x_0_0_1_1_1_4 = qtgui.time_sink_c(
            8192, #size
            samp_rate, #samp_rate
            "out2", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0_1_1_1_4.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_1_1_1_4.set_y_axis(-2, 2)

        self.qtgui_time_sink_x_0_0_1_1_1_4.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_1_1_1_4.enable_tags(True)
        self.qtgui_time_sink_x_0_0_1_1_1_4.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_1_1_1_4.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_1_1_1_4.enable_grid(False)
        self.qtgui_time_sink_x_0_0_1_1_1_4.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_1_1_1_4.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_1_1_1_4.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_1_1_1_4.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_1_1_1_4.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_1_1_1_4.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_1_1_1_4.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_1_1_1_4.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_1_1_1_4.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_1_1_1_4.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_1_1_1_4.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_1_1_1_4_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_1_1_1_4.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_1_1_1_4_win)
        self.qtgui_time_sink_x_0_0_1_1_1_0 = qtgui.time_sink_c(
            8192, #size
            samp_rate, #samp_rate
            "in1", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0_1_1_1_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_1_1_1_0.set_y_axis(-2, 2)

        self.qtgui_time_sink_x_0_0_1_1_1_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_1_1_1_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0_1_1_1_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_1_1_1_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_1_1_1_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0_1_1_1_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_1_1_1_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_1_1_1_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_1_1_1_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_1_1_1_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_1_1_1_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_1_1_1_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_1_1_1_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_1_1_1_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_1_1_1_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_1_1_1_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_1_1_1_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_1_1_1_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_1_1_1_0_win)
        self.qtgui_time_sink_x_0_0_1_1_1 = qtgui.time_sink_c(
            8192, #size
            samp_rate, #samp_rate
            "out1", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0_1_1_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_1_1_1.set_y_axis(-2, 2)

        self.qtgui_time_sink_x_0_0_1_1_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_1_1_1.enable_tags(True)
        self.qtgui_time_sink_x_0_0_1_1_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0_1_1_1.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_1_1_1.enable_grid(False)
        self.qtgui_time_sink_x_0_0_1_1_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_1_1_1.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_1_1_1.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_1_1_1.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_1_1_1.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_1_1_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_1_1_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_1_1_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_1_1_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_1_1_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_1_1_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_1_1_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_1_1_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_1_1_1_win)
        self.qtgui_const_sink_x_0_4 = qtgui.const_sink_c(
            1024, #size
            "mimo 2", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0_4.set_update_time(0.10)
        self.qtgui_const_sink_x_0_4.set_y_axis((-2), 2)
        self.qtgui_const_sink_x_0_4.set_x_axis((-2), 2)
        self.qtgui_const_sink_x_0_4.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0_4.enable_autoscale(True)
        self.qtgui_const_sink_x_0_4.enable_grid(False)
        self.qtgui_const_sink_x_0_4.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0_4.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0_4.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0_4.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0_4.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0_4.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0_4.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0_4.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_4_win = sip.wrapinstance(self.qtgui_const_sink_x_0_4.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_4_win)
        self.qtgui_const_sink_x_0_3 = qtgui.const_sink_c(
            1024, #size
            "mimo 1", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0_3.set_update_time(0.10)
        self.qtgui_const_sink_x_0_3.set_y_axis((-2), 2)
        self.qtgui_const_sink_x_0_3.set_x_axis((-2), 2)
        self.qtgui_const_sink_x_0_3.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0_3.enable_autoscale(True)
        self.qtgui_const_sink_x_0_3.enable_grid(False)
        self.qtgui_const_sink_x_0_3.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0_3.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0_3.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0_3.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0_3.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0_3.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0_3.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0_3.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_3_win = sip.wrapinstance(self.qtgui_const_sink_x_0_3.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_3_win)
        self.epy_block_4 = epy_block_4.blk(file_path=file_path, payload_data_len=data_len)
        self.epy_block_3 = epy_block_3.blk(file_path="./receive_a33.jpg")
        self.epy_block_2 = epy_block_2.blk(frame_len=1000)
        self.epy_block_1_1_0 = epy_block_1_1_0.blk(symbols=zc1_rrced, sps=1, threshold=threshold, tag_name="h12_corr_start")
        self.epy_block_1_1 = epy_block_1_1.blk(symbols=zc2_rrced, sps=1, threshold=threshold, tag_name="h22_corr_start")
        self.epy_block_1_0 = epy_block_1_0.blk(symbols=zc2_rrced, sps=1, threshold=threshold, tag_name="h21_corr_start")
        self.epy_block_1 = epy_block_1.blk(symbols=zc1_rrced, sps=1, threshold=threshold, tag_name="h11_corr_start")
        self.digital_pfb_clock_sync_xxx_0_0 = digital.pfb_clock_sync_ccf(4, 0.02, rrc_taps, nfilts, 0, 0.5, 1)
        self.digital_pfb_clock_sync_xxx_0 = digital.pfb_clock_sync_ccf(4, 0.02, rrc_taps, nfilts, 0, 0.5, 1)
        self.digital_map_bb_1 = digital.map_bb([0, 1, 3, 2])
        self.digital_map_bb_0_0_0 = digital.map_bb([0, 1, 3, 2])
        self.digital_map_bb_0_0 = digital.map_bb([0, 1, 3, 2])
        self.digital_map_bb_0 = digital.map_bb([0, 1, 3, 2])
        self.digital_constellation_decoder_cb_0_0 = digital.constellation_decoder_cb(data_modulator)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(data_modulator)
        self.digital_chunks_to_symbols_xx_1 = digital.chunks_to_symbols_bc([-0.707-0.707j, -0.707+0.707j, 0.707+0.707j, 0.707-0.707j], 1)
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bc([-0.707-0.707j, -0.707+0.707j, 0.707+0.707j, 0.707-0.707j], 1)
        self._button_msg_choices = {'Pressed': 1, 'Released': 0}

        _button_msg_toggle_button = qtgui.ToggleButton(self.set_button_msg, "调试/发送文件", self._button_msg_choices, False, 'value')
        _button_msg_toggle_button.setColors("default", "default", "default", "default")
        self.button_msg = _button_msg_toggle_button

        self.top_layout.addWidget(_button_msg_toggle_button)
        self.blocks_vector_source_x_0_0 = blocks.vector_source_c(tx2_preamble, True, 1, [])
        self.blocks_vector_source_x_0 = blocks.vector_source_c(tx1_preamble, True, 1, [])
        self.blocks_throttle2_0_0_1_0_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_throttle2_0_0_1_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_tagged_stream_mux_0_0 = blocks.tagged_stream_mux(gr.sizeof_gr_complex*1, "packet_len", 0)
        self.blocks_tagged_stream_mux_0 = blocks.tagged_stream_mux(gr.sizeof_gr_complex*1, "packet_len", 0)
        self.blocks_stream_to_tagged_stream_0_1_0 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, 1000, "packet_len")
        self.blocks_stream_to_tagged_stream_0_1 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, 1000, "packet_len")
        self.blocks_stream_to_tagged_stream_0_0 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, 218, "packet_len")
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, 218, "packet_len")
        self.blocks_repack_bits_bb_0_1 = blocks.repack_bits_bb(8, 2, "", False, gr.GR_LSB_FIRST)
        self.blocks_repack_bits_bb_0_0_0 = blocks.repack_bits_bb(2, 8, "", False, gr.GR_LSB_FIRST)
        self.blocks_repack_bits_bb_0_0 = blocks.repack_bits_bb(2, 8, "", False, gr.GR_LSB_FIRST)
        self.blocks_repack_bits_bb_0 = blocks.repack_bits_bb(8, 2, "", False, gr.GR_LSB_FIRST)
        self.blocks_interleave_0 = blocks.interleave(gr.sizeof_char*1, 1)
        self.blocks_deinterleave_0 = blocks.deinterleave(gr.sizeof_char*1, 1)
        self.analog_agc_xx_0_0 = analog.agc_cc((1e-2), 1.0, 1.0, 65536)
        self.analog_agc_xx_0 = analog.agc_cc((1e-2), 1.0, 1.0, 65536)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.button_msg, 'state'), (self.epy_block_4, 'test/transfer'))
        self.connect((self.analog_agc_xx_0, 0), (self.epy_block_1, 0))
        self.connect((self.analog_agc_xx_0_0, 0), (self.epy_block_1_1, 0))
        self.connect((self.blocks_deinterleave_0, 0), (self.blocks_repack_bits_bb_0, 0))
        self.connect((self.blocks_deinterleave_0, 1), (self.blocks_repack_bits_bb_0_1, 0))
        self.connect((self.blocks_interleave_0, 0), (self.epy_block_3, 0))
        self.connect((self.blocks_repack_bits_bb_0, 0), (self.digital_map_bb_0, 0))
        self.connect((self.blocks_repack_bits_bb_0_0, 0), (self.blocks_interleave_0, 0))
        self.connect((self.blocks_repack_bits_bb_0_0_0, 0), (self.blocks_interleave_0, 1))
        self.connect((self.blocks_repack_bits_bb_0_1, 0), (self.digital_map_bb_1, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_tagged_stream_mux_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0_0, 0), (self.blocks_tagged_stream_mux_0_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0_1, 0), (self.blocks_tagged_stream_mux_0, 1))
        self.connect((self.blocks_stream_to_tagged_stream_0_1_0, 0), (self.blocks_tagged_stream_mux_0_0, 1))
        self.connect((self.blocks_tagged_stream_mux_0, 0), (self.root_raised_cosine_filter_0_0, 0))
        self.connect((self.blocks_tagged_stream_mux_0_0, 0), (self.root_raised_cosine_filter_0, 0))
        self.connect((self.blocks_throttle2_0_0_1_0, 0), (self.epy_block_2, 0))
        self.connect((self.blocks_throttle2_0_0_1_0, 0), (self.qtgui_time_sink_x_0_0_1_1_1_0, 0))
        self.connect((self.blocks_throttle2_0_0_1_0_0, 0), (self.epy_block_2, 1))
        self.connect((self.blocks_throttle2_0_0_1_0_0, 0), (self.qtgui_time_sink_x_0_0_1_1_1_4_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.blocks_stream_to_tagged_stream_0_0, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.blocks_stream_to_tagged_stream_0_1, 0))
        self.connect((self.digital_chunks_to_symbols_xx_1, 0), (self.blocks_stream_to_tagged_stream_0_1_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.digital_map_bb_0_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0_0, 0), (self.digital_map_bb_0_0_0, 0))
        self.connect((self.digital_map_bb_0, 0), (self.digital_chunks_to_symbols_xx_0, 0))
        self.connect((self.digital_map_bb_0_0, 0), (self.blocks_repack_bits_bb_0_0, 0))
        self.connect((self.digital_map_bb_0_0_0, 0), (self.blocks_repack_bits_bb_0_0_0, 0))
        self.connect((self.digital_map_bb_1, 0), (self.digital_chunks_to_symbols_xx_1, 0))
        self.connect((self.digital_pfb_clock_sync_xxx_0, 0), (self.blocks_throttle2_0_0_1_0, 0))
        self.connect((self.digital_pfb_clock_sync_xxx_0_0, 0), (self.blocks_throttle2_0_0_1_0_0, 0))
        self.connect((self.epy_block_1, 0), (self.epy_block_1_0, 0))
        self.connect((self.epy_block_1_0, 0), (self.digital_pfb_clock_sync_xxx_0, 0))
        self.connect((self.epy_block_1_1, 0), (self.epy_block_1_1_0, 0))
        self.connect((self.epy_block_1_1_0, 0), (self.digital_pfb_clock_sync_xxx_0_0, 0))
        self.connect((self.epy_block_2, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.epy_block_2, 1), (self.digital_constellation_decoder_cb_0_0, 0))
        self.connect((self.epy_block_2, 0), (self.qtgui_const_sink_x_0_3, 0))
        self.connect((self.epy_block_2, 1), (self.qtgui_const_sink_x_0_4, 0))
        self.connect((self.epy_block_2, 0), (self.qtgui_time_sink_x_0_0_1_1_1, 0))
        self.connect((self.epy_block_2, 1), (self.qtgui_time_sink_x_0_0_1_1_1_4, 0))
        self.connect((self.epy_block_4, 0), (self.blocks_deinterleave_0, 0))
        self.connect((self.root_raised_cosine_filter_0, 0), (self.uhd_usrp_sink_0, 1))
        self.connect((self.root_raised_cosine_filter_0_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.analog_agc_xx_0, 0))
        self.connect((self.uhd_usrp_source_0, 1), (self.analog_agc_xx_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "mimo22")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_zc2(self):
        return self.zc2

    def set_zc2(self, zc2):
        self.zc2 = zc2
        self.set_tx2_preamble([0]*32 + [0]*61 +[0]*32 + self.zc2 + [0]*32)
        self.set_zc2_rrced(vr.rrc_interpolation_filter(self.zc2, 4, 1, 0.35, 11*self.sample_rate))

    def get_zc1(self):
        return self.zc1

    def set_zc1(self, zc1):
        self.zc1 = zc1
        self.set_tx1_preamble([0]*32 + self.zc1 + [0]*32 + [0]*61 + [0]*32)
        self.set_zc1_rrced(vr.rrc_interpolation_filter(self.zc1, 4, 1, 0.35, 11*self.sample_rate))

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts*self.sample_rate, 1, 0.35, (11*self.sample_rate*self.nfilts)))
        self.set_zc1_rrced(vr.rrc_interpolation_filter(self.zc1, 4, 1, 0.35, 11*self.sample_rate))
        self.set_zc2_rrced(vr.rrc_interpolation_filter(self.zc2, 4, 1, 0.35, 11*self.sample_rate))
        self.root_raised_cosine_filter_0.set_taps(firdes.root_raised_cosine(4, self.sample_rate, 1.0, 0.35, (11*self.sample_rate)))
        self.root_raised_cosine_filter_0_0.set_taps(firdes.root_raised_cosine(4, self.sample_rate, 1.0, 0.35, (11*self.sample_rate)))

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts*self.sample_rate, 1, 0.35, (11*self.sample_rate*self.nfilts)))

    def get_zc_modulator(self):
        return self.zc_modulator

    def set_zc_modulator(self, zc_modulator):
        self.zc_modulator = zc_modulator

    def get_zc2_rrced(self):
        return self.zc2_rrced

    def set_zc2_rrced(self, zc2_rrced):
        self.zc2_rrced = zc2_rrced

    def get_zc1_rrced(self):
        return self.zc1_rrced

    def set_zc1_rrced(self, zc1_rrced):
        self.zc1_rrced = zc1_rrced

    def get_tx2_preamble(self):
        return self.tx2_preamble

    def set_tx2_preamble(self, tx2_preamble):
        self.tx2_preamble = tx2_preamble
        self.blocks_vector_source_x_0_0.set_data(self.tx2_preamble, [])

    def get_tx1_preamble(self):
        return self.tx1_preamble

    def set_tx1_preamble(self, tx1_preamble):
        self.tx1_preamble = tx1_preamble
        self.blocks_vector_source_x_0.set_data(self.tx1_preamble, [])

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.epy_block_1.threshold = self.threshold
        self.epy_block_1_0.threshold = self.threshold
        self.epy_block_1_1.threshold = self.threshold
        self.epy_block_1_1_0.threshold = self.threshold

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle2_0_0_1_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle2_0_0_1_0_0.set_sample_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_0_1_1_1.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_0_1_1_1_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_0_1_1_1_4.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_0_1_1_1_4_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps
        self.digital_pfb_clock_sync_xxx_0.update_taps(self.rrc_taps)
        self.digital_pfb_clock_sync_xxx_0_0.update_taps(self.rrc_taps)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_sink_0.set_gain(self.gain, 0)
        self.uhd_usrp_sink_0.set_gain(self.gain, 1)
        self.uhd_usrp_source_0.set_gain(self.gain, 0)
        self.uhd_usrp_source_0.set_gain(self.gain, 1)

    def get_file_path(self):
        return self.file_path

    def set_file_path(self, file_path):
        self.file_path = file_path
        self.epy_block_4.file_path = self.file_path

    def get_data_modulator(self):
        return self.data_modulator

    def set_data_modulator(self, data_modulator):
        self.data_modulator = data_modulator
        self.digital_constellation_decoder_cb_0.set_constellation(self.data_modulator)
        self.digital_constellation_decoder_cb_0_0.set_constellation(self.data_modulator)

    def get_data_len(self):
        return self.data_len

    def set_data_len(self, data_len):
        self.data_len = data_len
        self.epy_block_4.payload_data_len = self.data_len

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.uhd_usrp_sink_0.set_center_freq(int(self.center_freq), 0)
        self.uhd_usrp_sink_0.set_center_freq(int(self.center_freq), 1)
        self.uhd_usrp_source_0.set_center_freq(int(self.center_freq), 0)
        self.uhd_usrp_source_0.set_center_freq(int(self.center_freq), 1)

    def get_button_msg(self):
        return self.button_msg

    def set_button_msg(self, button_msg):
        self.button_msg = button_msg




def main(top_block_cls=mimo22, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
