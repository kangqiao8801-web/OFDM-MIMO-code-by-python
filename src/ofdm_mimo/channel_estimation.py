from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike
from scipy.interpolate import CubicSpline, interp1d


def ls_ce(
    y: ArrayLike,
    xp: ArrayLike,
    pilot_loc: ArrayLike,
    nfft: int,
    nps: int,
    method: str = "linear",
) -> np.ndarray:
    """Least-squares pilot channel estimate with linear or spline interpolation."""
    y_arr = np.asarray(y, dtype=complex)
    xp_arr = np.asarray(xp, dtype=complex)
    loc = np.asarray(pilot_loc, dtype=int)
    h_pilot = y_arr[loc] / xp_arr
    return _interpolate(h_pilot, loc, nfft, nps, method)


def mmse_ce(
    y: ArrayLike,
    xp: ArrayLike,
    pilot_loc: ArrayLike,
    nfft: int,
    nps: int,
    h: ArrayLike,
    snr_db: float,
) -> np.ndarray:
    """MMSE channel estimate following the book example's pilot-correlation form."""
    y_arr = np.asarray(y, dtype=complex)
    xp_arr = np.asarray(xp, dtype=complex)
    loc = np.asarray(pilot_loc, dtype=int)
    h_arr = np.asarray(h, dtype=complex)
    h_pilot_ls = y_arr[loc] / xp_arr

    channel_power = np.mean(np.abs(h_arr) ** 2)
    snr_linear = 10 ** (snr_db / 10)
    noise_var = channel_power / snr_linear if snr_linear else channel_power
    n = np.arange(nfft)
    channel_lags = np.arange(len(h_arr))
    power_delay = np.abs(h_arr) ** 2
    power_delay = power_delay / np.sum(power_delay)

    full_to_pilot_lag = n[:, None] - loc[None, :]
    r_hp = np.sum(
        power_delay[:, None, None]
        * np.exp(-2j * np.pi * channel_lags[:, None, None] * full_to_pilot_lag[None, :, :] / nfft),
        axis=0,
    )
    lag_pp = loc[:, None] - loc[None, :]
    r_pp = np.sum(power_delay[:, None, None] * np.exp(-2j * np.pi * channel_lags[:, None, None] * lag_pp / nfft), axis=0)
    regularized = r_pp + noise_var * np.eye(len(loc))
    weights = r_hp @ np.linalg.pinv(regularized)
    return weights @ h_pilot_ls


def _interpolate(h_pilot: np.ndarray, pilot_loc: np.ndarray, nfft: int, nps: int, method: str) -> np.ndarray:
    if pilot_loc[0] != 0:
        pilot_loc = np.insert(pilot_loc, 0, 0)
        h_pilot = np.insert(h_pilot, 0, h_pilot[0])
    if pilot_loc[-1] != nfft - 1:
        pilot_loc = np.append(pilot_loc, nfft - 1)
        h_pilot = np.append(h_pilot, h_pilot[-1])

    x = np.arange(nfft)
    if method == "linear":
        interp = interp1d(pilot_loc, h_pilot, kind="linear")
        return interp(x)
    if method == "spline":
        spline_real = CubicSpline(pilot_loc, h_pilot.real)
        spline_imag = CubicSpline(pilot_loc, h_pilot.imag)
        return spline_real(x) + 1j * spline_imag(x)
    raise ValueError(f"Unsupported interpolation method {method}.")
