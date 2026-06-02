import numpy as np
from scipy import signal
from gnuradio.filter import firdes


def rrc_interpolation_filter(input_signal, interpolation, gain, *args):
    """
    RRC（Root Raised Cosine）插值滤波器

    使用 GNU Radio firdes.root_raised_cosine 生成滤波器抽头，
    确保与 TX 链路中 interp_fir_filter_ccf 使用完全相同的 RRC 脉冲形状，
    保证接收端相关性估计的参考序列与发射信号精确匹配。

    参数：
    -----------
    input_signal : list of complex
        输入复数信号
    interpolation : int
        插值倍数，同时作为每符号采样数
    gain : float
        滤波器增益系数（传给 firdes.root_raised_cosine）
    alpha : float
        RRC滚降系数 (0 < alpha <= 1)
    num_taps : int
        滤波器抽头数

    兼容旧调用格式：
    -----------
    rrc_interpolation_filter(input_signal, interpolation, gain,
                             samplerate, symbol_rate, alpha, num_taps)
    其中 samplerate 和 symbol_rate 会被忽略。

    返回：
    --------
    output_signal : list of complex
        滤波后的复数信号
    """

    if len(args) == 2:
        alpha, num_taps = args
    elif len(args) == 4:
        _, _, alpha, num_taps = args
    else:
        raise TypeError(
            "rrc_interpolation_filter expects (input_signal, interpolation, gain, alpha, num_taps) "
            "or legacy (input_signal, interpolation, gain, samplerate, symbol_rate, alpha, num_taps)"
        )

    signal_array = np.asarray(input_signal, dtype=complex)

    interpolation = int(np.round(interpolation))
    if interpolation < 1:
        raise ValueError("interpolation must be a positive integer")

    alpha = float(alpha)
    if not 0 < alpha <= 1:
        raise ValueError("alpha must satisfy 0 < alpha <= 1")

    num_taps = int(np.round(num_taps))
    if num_taps < 1:
        raise ValueError("num_taps must be positive")

    if signal_array.size == 0:
        return []

    # 始终使用 interpolation 作为 firdes gain，与 TX 链路中
    # interp_fir_filter_ccf 使用的 firdes.root_raised_cosine(interpolation, ...)
    # 完全一致，确保参考序列幅度匹配发射信号。
    # （忽略调用者传入的 gain 参数，因为 corr_est_cc 的 THRESHOLD_ABSOLUTE
    #  阈值 = threshold * symbols_energy²，参考序列幅度必须与 TX 信号匹配。）
    firdes_gain = float(interpolation)
    h = np.array(firdes.root_raised_cosine(
        firdes_gain, interpolation, 1.0, alpha, num_taps))

    interpolated_signal = np.zeros(signal_array.size * interpolation, dtype=complex)
    interpolated_signal[::interpolation] = signal_array

    output_signal = signal.convolve(interpolated_signal, h, mode='same')

    return output_signal.tolist()