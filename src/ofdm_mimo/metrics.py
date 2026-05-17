from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


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
