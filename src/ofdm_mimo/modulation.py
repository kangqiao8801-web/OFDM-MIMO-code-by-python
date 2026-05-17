from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


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
