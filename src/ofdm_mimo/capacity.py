from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def mimo_capacity(h: ArrayLike, snr_linear: float, nt: int | None = None) -> float:
    channel = np.asarray(h, dtype=complex)
    nt = channel.shape[1] if nt is None else nt
    n = min(channel.shape)
    gram = channel.conj().T @ channel if channel.shape[0] >= channel.shape[1] else channel @ channel.conj().T
    return float(np.real(np.log2(np.linalg.det(np.eye(n) + snr_linear / nt * gram))))


def water_pouring(singular_values: ArrayLike, snr_linear: float, nt: int) -> np.ndarray:
    values = np.asarray(singular_values, dtype=float)
    inv_gains = nt / (snr_linear * np.maximum(values, np.finfo(float).eps))
    order = np.argsort(inv_gains)
    sorted_inv = inv_gains[order]
    power = np.zeros_like(values)
    for active in range(1, len(values) + 1):
        level = (nt + np.sum(sorted_inv[:active])) / active
        alloc = level - sorted_inv[:active]
        if active == len(values) or level <= sorted_inv[active]:
            power[order[:active]] = np.maximum(alloc, 0)
            break
    return power
