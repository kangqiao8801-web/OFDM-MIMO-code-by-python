from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

QPSK_TABLE = np.array([1, 1j, -1j, -1], dtype=complex) / np.sqrt(2)
QAM16_TABLE = np.array(
    [
        -3 + 3j,
        -1 + 3j,
        3 + 3j,
        1 + 3j,
        -3 + 1j,
        -1 + 1j,
        3 + 1j,
        1 + 1j,
        -3 - 3j,
        -1 - 3j,
        3 - 3j,
        1 - 3j,
        -3 - 1j,
        -1 - 1j,
        3 - 1j,
        1 - 1j,
    ],
    dtype=complex,
) / np.sqrt(10)
QAM16_SOFT_TABLE = np.array(
    [
        -3 - 3j,
        -3 - 1j,
        -3 + 3j,
        -3 + 1j,
        -1 - 3j,
        -1 - 1j,
        -1 + 3j,
        -1 + 1j,
        3 - 3j,
        3 - 1j,
        3 + 3j,
        3 + 1j,
        1 - 3j,
        1 - 1j,
        1 + 3j,
        1 + 1j,
    ],
    dtype=complex,
) / np.sqrt(10)


def qam_mod(symbols: ArrayLike, order: int, unit_average_power: bool = True) -> np.ndarray:
    """Square Gray-coded QAM modulation compatible with MATLAB qammod defaults."""
    symbols_arr = np.asarray(symbols, dtype=int)
    side = _square_qam_side(order)
    gray = symbols_arr ^ (symbols_arr >> 1)
    i = gray % side
    q = gray // side
    levels = np.arange(-(side - 1), side, 2)
    modulated = levels[i] + 1j * levels[q]
    if unit_average_power:
        modulated = modulated / np.sqrt((2 / 3) * (order - 1))
    return modulated.astype(complex)


def qam_demod(values: ArrayLike, order: int, unit_average_power: bool = True) -> np.ndarray:
    """Nearest-neighbor square Gray-coded QAM demodulation."""
    values_arr = np.asarray(values, dtype=complex)
    side = _square_qam_side(order)
    if unit_average_power:
        values_arr = values_arr * np.sqrt((2 / 3) * (order - 1))
    levels = np.arange(-(side - 1), side, 2)
    i = np.abs(values_arr.real[..., None] - levels).argmin(axis=-1)
    q = np.abs(values_arr.imag[..., None] - levels).argmin(axis=-1)
    gray = q * side + i
    return _gray_to_binary(gray).astype(int)


def bpsk_mod(bits: ArrayLike) -> np.ndarray:
    bits_arr = np.asarray(bits, dtype=int)
    return 2 * bits_arr - 1


def qpsk_mod(symbols: ArrayLike) -> np.ndarray:
    return qam_mod(symbols, 4, unit_average_power=True)


def qpsk_mapper(bitseq: ArrayLike) -> np.ndarray:
    bits = np.asarray(bitseq, dtype=int).ravel()
    if bits.size % 2:
        raise ValueError("QPSK bit sequence length must be a multiple of 2.")
    indices = bits[0::2] * 2 + bits[1::2]
    return QPSK_TABLE[indices]


def qpsk_demapper(x: ArrayLike) -> np.ndarray:
    symbols = np.asarray(x, dtype=complex).ravel()
    indices = _nearest_indices(symbols, QPSK_TABLE)
    return _indices_to_bits(indices, 2)


def qam16_mod(bitseq: ArrayLike, n: int | None = None) -> np.ndarray:
    bits = np.asarray(bitseq, dtype=int).ravel()
    if n is None:
        n = bits.size // 4
    if bits.size < 4 * n:
        raise ValueError("QAM16 bit sequence is shorter than 4*N.")
    chunks = bits[: 4 * n].reshape(n, 4)
    indices = chunks @ np.array([8, 4, 2, 1])
    return QAM16_TABLE[indices]


def qam16_demapper(qam16: ArrayLike, n: int | None = None) -> np.ndarray:
    symbols = np.asarray(qam16, dtype=complex).ravel()
    if n is None:
        n = symbols.size
    indices = _nearest_indices(symbols[:n], QAM16_TABLE)
    return _indices_to_bits(indices, 4)


def qam16_slicer(x: ArrayLike, n: int | None = None) -> np.ndarray:
    arr = np.asarray(x, dtype=complex)
    flat = arr.ravel()
    if n is not None:
        flat = flat[:n]
    sliced = qam16_real_slicer(flat.real) + 1j * qam16_real_slicer(flat.imag)
    return sliced.reshape(arr.shape if n is None else (n,))


def qam16_real_slicer(x: ArrayLike, n: int | None = None) -> np.ndarray:
    arr = np.asarray(x)
    flat = np.real(arr).ravel()
    if n is not None:
        flat = flat[:n]
    levels = np.array([-3, -1, 1, 3], dtype=float) / np.sqrt(10)
    bins = np.array([-2, 0, 2], dtype=float) / np.sqrt(10)
    sliced = levels[np.digitize(flat, bins)]
    return sliced.reshape(arr.shape if n is None else (n,))


def qam16_slicer_soft(x: ArrayLike) -> np.ndarray:
    symbols = np.asarray(x, dtype=complex).ravel()
    indices = _nearest_indices(symbols, QAM16_SOFT_TABLE)
    return _indices_to_bits(indices, 4)


def modulator(bitseq: ArrayLike, b: int) -> tuple[np.ndarray, np.ndarray, int]:
    bits = np.asarray(bitseq, dtype=int).ravel()
    if bits.size % b:
        raise ValueError("bit sequence length must be a multiple of b.")

    if b == 1:
        sym_table = np.exp(1j * np.array([0, -np.pi]))[[1, 0]]
        indices = bits
    elif b == 2:
        sym_table = np.exp(1j * np.pi / 4 * np.array([-3, 3, 1, -1]))[[0, 1, 3, 2]]
        indices = bits.reshape(-1, b) @ np.array([2, 1])
    elif b == 3:
        sym_table = np.exp(1j * np.pi / 4 * np.arange(8))[[0, 1, 3, 2, 6, 7, 5, 4]]
        indices = bits.reshape(-1, b) @ np.array([4, 2, 1])
    elif b == 4:
        base = np.array([k + 1j * l for k in range(-3, 4, 2) for l in range(-3, 4, 2)]) / np.sqrt(10)
        sym_table = base[[0, 1, 3, 2, 4, 5, 7, 6, 12, 13, 15, 14, 8, 9, 11, 10]]
        indices = bits.reshape(-1, b) @ np.array([8, 4, 2, 1])
    else:
        raise ValueError("Unimplemented modulation.")
    return sym_table[indices], sym_table, 2**b


def mapper(b: int, n: int | None = None, rng: np.random.Generator | None = None) -> tuple[np.ndarray, str]:
    order = 2**b
    rng = np.random.default_rng() if rng is None else rng
    indices = rng.integers(0, order, size=n) if n is not None else np.arange(order)

    if b == 1:
        return np.exp(1j * np.pi * indices), "BPSK"
    if b == 2:
        return np.exp(1j * (2 * np.pi * indices / order + np.pi / 4)), "QPSK"
    return qam_mod(indices, order, unit_average_power=True), f"{order}QAM"


def data_generator(
    l_frame: int,
    n_frames: int,
    md: int,
    zf: int,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    rng = np.random.default_rng() if rng is None else rng
    data = rng.integers(0, md, size=(l_frame, 1, n_frames))
    if zf > 0:
        data = np.concatenate([data, np.zeros((zf, 1, n_frames), dtype=data.dtype)], axis=0)
    return data


def modulo(x: ArrayLike, a: float) -> np.ndarray:
    arr = np.asarray(x, dtype=complex)
    temp_real = np.floor((arr.real + a) / (2 * a))
    temp_imag = np.floor((arr.imag + a) / (2 * a))
    return arr - temp_real * (2 * a) - 1j * temp_imag * (2 * a)


def soft_decision_sigma(x: ArrayLike, h: ArrayLike) -> np.ndarray:
    values = np.asarray(x, dtype=complex).ravel()
    channel = np.asarray(h, dtype=complex).ravel()
    xr = values.real
    xi = values.imag
    metrics = np.vstack([xr, 2 - np.abs(xr), xi, 2 - np.abs(xi)])
    return (metrics * np.abs(channel)).ravel(order="F")


def soft_output2x2(x: ArrayLike) -> np.ndarray:
    values = np.asarray(x, dtype=complex).ravel()
    sq10 = np.sqrt(10)
    sq10_2 = 2 / sq10
    xr = values.real
    xi = values.imag
    metrics = sq10 * np.vstack([-xi, sq10_2 - np.abs(xi), xr, sq10_2 - np.abs(xr)])
    return metrics.ravel(order="F")


def modulate_carrier(
    x: ArrayLike,
    ts: float,
    nos: int,
    fc: float,
    passband: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(x, dtype=complex).ravel()
    scale = np.sqrt(2) if passband else 1.0
    sample_period = 1 / fc / 2 / nos if passband else ts / nos
    t_ts = np.arange(0, ts, sample_period)
    time = np.arange(0, values.size * ts, sample_period)
    tmp = 2 * np.pi * fc * t_ts
    cos_wct = np.cos(tmp) * scale
    sin_wct = np.sin(tmp) * scale
    signal = np.empty(values.size * t_ts.size)
    for idx, value in enumerate(values):
        start = idx * t_ts.size
        signal[start : start + t_ts.size] = value.real * cos_wct - value.imag * sin_wct
    return signal, time


def _square_qam_side(order: int) -> int:
    side = int(np.sqrt(order))
    if side * side != order:
        raise ValueError(f"Only square QAM orders are supported, got {order}.")
    return side


def _gray_to_binary(gray: np.ndarray) -> np.ndarray:
    binary = np.array(gray, copy=True)
    shift = binary >> 1
    while np.any(shift):
        binary ^= shift
        shift >>= 1
    return binary


def _nearest_indices(values: np.ndarray, table: np.ndarray) -> np.ndarray:
    return np.abs(values[..., None] - table).argmin(axis=-1)


def _indices_to_bits(indices: np.ndarray, width: int) -> np.ndarray:
    flat = np.asarray(indices, dtype=int).ravel()
    shifts = np.arange(width - 1, -1, -1)
    return ((flat[:, None] >> shifts) & 1).astype(int).ravel()
