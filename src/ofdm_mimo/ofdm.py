from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def guard_interval(ng: int, nfft: int, ng_type: int, ofdm_sym: ArrayLike) -> np.ndarray:
    """Add MATLAB-style guard interval: 1 for cyclic prefix, 2 for zero padding."""
    symbol = np.asarray(ofdm_sym)
    if symbol.shape[-1] != nfft:
        raise ValueError(f"Expected OFDM symbol length {nfft}, got {symbol.shape[-1]}.")
    if ng == 0:
        return symbol.copy()
    if ng_type == 1:
        return np.concatenate([symbol[-ng:], symbol])
    if ng_type == 2:
        return np.concatenate([symbol, np.zeros(ng, dtype=symbol.dtype)])
    raise ValueError(f"Unsupported guard interval type {ng_type}.")


def remove_gi(ng: int, lsym: int, ng_type: int, ofdm_sym: ArrayLike) -> np.ndarray:
    """Remove MATLAB-style guard interval."""
    symbol = np.asarray(ofdm_sym)
    if symbol.shape[-1] < lsym:
        raise ValueError(f"Expected at least {lsym} samples, got {symbol.shape[-1]}.")
    if ng == 0:
        return symbol[:lsym].copy()
    if ng_type == 1:
        return symbol[ng:lsym].copy()
    if ng_type == 2:
        return symbol[: lsym - ng].copy()
    raise ValueError(f"Unsupported guard interval type {ng_type}.")


def add_cp(x: ArrayLike, ncp: int) -> np.ndarray:
    arr = np.asarray(x)
    if ncp == 0:
        return arr.copy()
    return np.concatenate([arr[-ncp:], arr])


def remove_cp(x: ArrayLike, ncp: int, offset: int = 0) -> np.ndarray:
    arr = np.asarray(x)
    return arr[ncp + offset :]
