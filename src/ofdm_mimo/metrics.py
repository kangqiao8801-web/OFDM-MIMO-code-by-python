from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike
from scipy.special import erfc

_BER_ERROR_BITS = 0
_BER_TOTAL_BITS = 0

def bit_error_rate(received: ArrayLike, reference: ArrayLike, bits_per_symbol: int) -> tuple[float, int, int]:
    received_arr = np.asarray(received, dtype=int)
    reference_arr = np.asarray(reference, dtype=int)
    if received_arr.shape != reference_arr.shape:
        raise ValueError("received and reference must have the same shape.")
    xor = np.bitwise_xor(received_arr, reference_arr).ravel()
    errors = int(sum(int(x).bit_count() for x in xor))
    total = int(received_arr.size * bits_per_symbol)
    return errors / total if total else 0.0, errors, total


def papr_db(x: ArrayLike) -> tuple[float, float, float]:
    arr = np.asarray(x)
    power = np.abs(arr) ** 2
    avg = float(np.mean(power))
    peak = float(np.max(power))
    return 10 * np.log10(peak / avg), 10 * np.log10(avg), 10 * np.log10(peak)


def ber(
    x: ArrayLike | None = None,
    x_ref: ArrayLike | None = None,
    nbps: int | None = None,
    *,
    reset: bool = False,
) -> tuple[float, int, int]:
    global _BER_ERROR_BITS, _BER_TOTAL_BITS
    if reset or x is None:
        _BER_ERROR_BITS = 0
        _BER_TOTAL_BITS = 0
        return 0.0, 0, 0
    if x_ref is None or nbps is None:
        raise ValueError("x, x_ref, and nbps are required unless reset=True.")

    received = np.asarray(x, dtype=int).ravel()
    reference = np.asarray(x_ref, dtype=int).ravel()
    if received.shape != reference.shape:
        raise ValueError("x and x_ref must have the same shape.")

    xor = np.bitwise_xor(received, reference)
    _BER_ERROR_BITS += int(sum(int(value).bit_count() for value in xor))
    _BER_TOTAL_BITS += int(received.size * nbps)
    value = _BER_ERROR_BITS / _BER_TOTAL_BITS if _BER_TOTAL_BITS else 0.0
    return value, _BER_ERROR_BITS, _BER_TOTAL_BITS


def ber_qam(ebn0_db: ArrayLike, order: int, channel: str = "AWGN") -> np.ndarray:
    ebn0 = np.asarray(ebn0_db, dtype=float)
    sqrt_order = np.sqrt(order)
    a = 2 * (1 - sqrt_order**-1) / np.log2(sqrt_order)
    b = 6 * np.log2(sqrt_order) / (order - 1)
    if channel.lower().startswith("a"):
        return a * qfunc(np.sqrt(b * 10 ** (ebn0 / 10)))
    rn = b * 10 ** (ebn0 / 10) / 2
    return 0.5 * a * (1 - np.sqrt(rn / (rn + 1)))


def qfunc(x: ArrayLike) -> np.ndarray:
    return 0.5 * erfc(np.asarray(x, dtype=float) / np.sqrt(2))
