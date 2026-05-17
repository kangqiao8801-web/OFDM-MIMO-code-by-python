from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike
from scipy.interpolate import interp1d
from scipy.special import erfc


def qfunc(x: ArrayLike) -> np.ndarray:
    return 0.5 * erfc(np.asarray(x, dtype=float) / np.sqrt(2))


def db2w(db: ArrayLike) -> np.ndarray:
    return 10 ** (0.1 * np.asarray(db, dtype=float))


def deci2bin(x: ArrayLike, b: int | None = None, kc: int = 0) -> np.ndarray:
    values = np.asarray(x, dtype=int).ravel()
    if b is None:
        xmax = int(np.max(values)) if values.size else 0
        b = 1
        while xmax > 1:
            xmax //= 2
            b += 1
    shifts = np.arange(b - 1, -1, -1)
    bits = ((values[:, None] >> shifts) & 1).ravel()
    if kc > 0:
        while bits.size and bits[0] == 0:
            bits = bits[1:]
    return bits.astype(int)


def equalpower_subray(as_deg: float) -> np.ndarray:
    if as_deg == 2:
        return np.array([0.0894, 0.2826, 0.4984, 0.7431, 1.0257, 1.3594, 1.7688, 2.2961, 3.0389, 4.3101])
    if as_deg == 5:
        return np.array([0.2236, 0.7064, 1.2461, 1.8578, 2.5642, 3.3986, 4.4220, 5.7403, 7.5974, 10.7753])
    if as_deg == 35:
        return np.array([1.5649, 4.9447, 8.7224, 13.0045, 17.9492, 23.7899, 30.9538, 40.1824, 53.1816, 75.4274])
    raise ValueError("Unsupported angle spread.")


def assign_offset(aoa_deg: ArrayLike, as_deg: float) -> np.ndarray:
    offset = equalpower_subray(as_deg)
    signed = np.column_stack([offset, -offset]).ravel()
    return np.asarray(aoa_deg, dtype=float).reshape(-1, 1) + signed.reshape(1, -1)


def exp_pdp(tau_d: float, ts: float, a_db: float = -20, norm_flag: bool = True) -> np.ndarray:
    threshold = 10 ** (a_db / 10)
    lmax = int(np.ceil(-tau_d * np.log(threshold) / ts))
    if norm_flag:
        p0 = (1 - np.exp(-ts / tau_d)) / (1 - np.exp(-(lmax + 1) * ts / tau_d))
    else:
        p0 = 1 / tau_d
    taps = np.arange(lmax + 1)
    return p0 * np.exp(-taps * ts / tau_d)


def interpolate(h_est: ArrayLike, pilot_loc: ArrayLike, nfft: int, method: str = "linear") -> np.ndarray:
    h = np.asarray(h_est, dtype=complex).ravel()
    loc = np.asarray(pilot_loc, dtype=float).ravel()
    if loc.min() >= 1:
        loc = loc - 1
    if loc[0] > 0:
        slope = (h[1] - h[0]) / (loc[1] - loc[0])
        h = np.r_[h[0] - slope * loc[0], h]
        loc = np.r_[0, loc]
    if loc[-1] < nfft - 1:
        slope = (h[-1] - h[-2]) / (loc[-1] - loc[-2])
        h = np.r_[h, h[-1] + slope * (nfft - 1 - loc[-1])]
        loc = np.r_[loc, nfft - 1]
    kind = "linear" if method.lower().startswith("l") else "cubic"
    return interp1d(loc, h, kind=kind)(np.arange(nfft))


def zero_insertion(x: ArrayLike, m: int, n: int | None = None) -> np.ndarray:
    arr = np.asarray(x)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if n is None:
        n = arr.shape[1] * m
    out = np.zeros((arr.shape[0], n), dtype=arr.dtype)
    out[:, 0:n:m] = arr[:, : len(range(0, n, m))]
    return out


def zero_padding(x: ArrayLike, nzero: int) -> np.ndarray:
    arr = np.asarray(x)
    mid = int(np.ceil(arr.size / 2))
    return np.r_[arr[:mid], np.zeros(nzero, dtype=arr.dtype), arr[mid:]]


def branch_metric(sig: ArrayLike, q_test: ArrayLike, ch_coefs: ArrayLike) -> np.ndarray:
    sig_arr = np.asarray(sig, dtype=complex)
    q_arr = np.asarray(q_test, dtype=complex)
    ch_arr = np.asarray(ch_coefs, dtype=complex)
    replica = q_arr @ ch_arr
    return np.sum(np.abs(sig_arr - replica) ** 2, axis=1)


def sort_matrix(matrix: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(matrix)
    order = np.argsort(arr.ravel(order="C"), kind="stable")
    rows, cols = np.unravel_index(order, arr.shape, order="C")
    return arr[rows, cols], np.column_stack([cols, rows])


def list_length(values: ArrayLike) -> int:
    count = 0
    for value in np.asarray(values).ravel()[:4]:
        if value == 0:
            break
        count += 1
    return count


def vector_comparison(vector_1: ArrayLike, vector_2: ArrayLike) -> int:
    v1 = np.asarray(vector_1).ravel()
    v2 = np.asarray(vector_2).ravel()
    if v1.shape != v2.shape:
        raise ValueError("vector size is different")
    return int(np.array_equal(v1, v2))


def gen_phase(
    bs_theta_los_deg: float,
    bs_as_deg: float,
    bs_aod_deg: ArrayLike,
    ms_theta_los_deg: float,
    ms_as_deg: float,
    ms_aoa_deg: ArrayLike,
    m: int = 20,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng() if rng is None else rng
    bs_phi_rad = 2 * np.pi * rng.random((len(np.asarray(bs_aod_deg).ravel()), m))
    bs_theta_deg = assign_offset(bs_theta_los_deg + np.asarray(bs_aod_deg), bs_as_deg)
    ms_theta_deg = assign_offset(ms_theta_los_deg + np.asarray(ms_aoa_deg), ms_as_deg)
    index = rng.permutation(m)
    ms_theta_deg = ms_theta_deg[:, index]
    return bs_theta_deg, ms_theta_deg, bs_phi_rad


def gen_filter(fm_hz: float, fmax_hz: float, nfading: int, nfosf: int, doppler_type: str, *args: float) -> np.ndarray:
    dfmax = 2 * nfosf * fmax_hz / nfading
    nd = int(np.floor(fm_hz / dfmax) - 1)
    if nd < 1:
        raise ValueError("Increase Nfading for this Doppler spacing.")
    f0 = np.arange(0, nd + 1) / nd
    typ = doppler_type.lower()
    if typ.startswith("flat"):
        psd = np.ones_like(f0)
    elif typ.startswith("class"):
        psd = 1 / np.sqrt(np.maximum(1 - f0**2, np.finfo(float).eps))
    elif typ.startswith("sui"):
        psd = np.where(f0 <= 0.7, 1.0, np.maximum(1 - f0, 0.0))
    else:
        psd = np.ones_like(f0)
    spec = np.r_[psd[:-1], np.zeros(nfading - 2 * nd + 3), psd[-2:0:-1]]
    filt = np.real(np.fft.ifftshift(np.fft.ifft(np.sqrt(spec[:nfading]))))
    return filt / np.sqrt(np.sum(filt**2))


def calculate_norm(
    symbol_replica: ArrayLike,
    stage: int,
    qam_table: ArrayLike,
    r: ArrayLike,
    y_tilde: ArrayLike,
    nt: int,
    m_param: int,
) -> np.ndarray:
    replica = np.asarray(symbol_replica, dtype=int)
    qam = np.asarray(qam_table, dtype=complex).ravel()
    r_arr = np.asarray(r, dtype=complex)
    y_arr = np.asarray(y_tilde, dtype=complex).ravel()
    m = 1 if stage == 1 else m_param
    stage_index = nt - stage
    out = np.zeros((m, qam.size))
    for i in range(m):
        x_temp = np.zeros(nt, dtype=complex)
        for a in range(nt - 1, nt - stage, -1):
            x_temp[a] = qam[replica[nt - 1 - a, i, stage_index + 1] - 1]
        x_temp[nt + 1 - stage - 1 : nt] = x_temp[nt + 1 - stage - 1 : nt][::-1]
        y_now = y_arr[nt - stage : nt]
        r_now = r_arr[nt - stage : nt, nt - stage : nt]
        for k, symbol in enumerate(qam):
            x_temp[stage_index] = symbol
            out[i, k] = np.linalg.norm(y_now - r_now @ x_temp[nt - stage : nt]) ** 2
    return out


def radius_control(radius_squared: float, transition: int, length: int) -> tuple[int, int, float, np.ndarray]:
    return 1, transition + 1, radius_squared * 2, np.zeros(4 if length <= 1 else (length, 4))


def bound(
    transition: int,
    r: ArrayLike,
    radius_squared: float,
    x_now: ArrayLike,
    x_hat: ArrayLike,
) -> tuple[complex, complex]:
    r_arr = np.asarray(r, dtype=complex)
    now = np.asarray(x_now, dtype=complex).ravel()
    hat = np.asarray(x_hat, dtype=complex).ravel()
    length = hat.size
    temp_sqrt = radius_squared
    for i in range(1, transition):
        index_1 = length - i
        temp_abs = 0
        for k in range(i):
            index_2 = index_1 + k
            temp_abs += r_arr[index_1, index_2] * (now[index_2] - hat[index_2])
        temp_sqrt -= abs(temp_abs) ** 2
    temp_sqrt = np.sqrt(temp_sqrt)
    index_1 = length - transition
    temp_no_sqrt = 0
    for index_2 in range(index_1 + 1, length):
        temp_no_sqrt -= r_arr[index_1, index_2] * (now[index_2] - hat[index_2])
    lower = (-temp_sqrt + temp_no_sqrt) / r_arr[index_1, index_1] + hat[index_1]
    upper = (temp_sqrt + temp_no_sqrt) / r_arr[index_1, index_1] + hat[index_1]
    return np.ceil(lower * np.sqrt(10)) / np.sqrt(10), np.fix(upper * np.sqrt(10)) / np.sqrt(10)


def compare_vector_norm(
    transition: int,
    x_list: ArrayLike,
    x_pre: ArrayLike,
    x_now: ArrayLike,
    x_hat: ArrayLike,
    r: ArrayLike,
    radius_squared: float,
) -> tuple[int, int, np.ndarray, float, np.ndarray, np.ndarray]:
    x_list_arr = np.asarray(x_list).copy()
    pre = np.asarray(x_pre, dtype=complex).ravel()
    now = np.asarray(x_now, dtype=complex).ravel()
    hat = np.asarray(x_hat, dtype=complex).ravel()
    r_arr = np.asarray(r, dtype=complex)
    length = hat.size
    if vector_comparison(pre, now):
        remaining = sum(list_length(row) for row in x_list_arr[:length])
        return (1, length + 2, x_list_arr, radius_squared, now, now) if remaining == 0 else (0, transition - 1, x_list_arr, radius_squared, pre, now)

    metric = np.linalg.norm(r_arr @ (now - hat)) ** 2
    if metric <= radius_squared:
        return 2, 1, np.zeros((length, 4), dtype=x_list_arr.dtype), float(metric), now.copy(), np.zeros_like(now)
    return 0, transition - 1, x_list_arr, radius_squared, pre, now


def stage_processing(
    flag: int,
    transition: int,
    x_list: ArrayLike,
    x_metric: float,
    x_now: ArrayLike,
    x_hat: ArrayLike,
    real_constellation: ArrayLike,
    r: ArrayLike,
    radius_squared: float,
    x_sliced: ArrayLike,
) -> tuple[int, int, np.ndarray, np.ndarray, float]:
    x_list_arr = np.asarray(x_list).copy()
    now = np.asarray(x_now, dtype=complex).copy()
    r_arr = np.asarray(r, dtype=complex)
    length = r_arr.shape[1]
    stage_index = length - transition
    if flag == 2:
        radius_squared = float(np.linalg.norm(r_arr @ (np.asarray(x_sliced).ravel() - np.asarray(x_hat).ravel())) ** 2)
    if flag != 0:
        lower, upper = bound(transition, r_arr, radius_squared, now, x_hat)
        for value in np.asarray(real_constellation).ravel()[:4]:
            if lower <= value <= upper:
                llen = list_length(x_list_arr[stage_index, :])
                if llen < x_list_arr.shape[1]:
                    x_list_arr[stage_index, llen] = value
    llen = list_length(x_list_arr[stage_index, :])
    if llen == 0:
        if x_metric == 0 or transition != 1:
            return 0, transition - 1, x_list_arr, now, radius_squared
        return flag, length + 2, x_list_arr, now, radius_squared
    now[stage_index] = x_list_arr[stage_index, 0]
    x_list_arr[stage_index, :] = np.r_[x_list_arr[stage_index, 1:4], 0]
    return 1, transition + 1, x_list_arr, now, radius_squared


def stage_processing1(
    symbol_replica: ArrayLike,
    stage: int,
    qam_table: ArrayLike,
    r: ArrayLike,
    y_tilde: ArrayLike,
    nt: int,
    m_param: int,
) -> np.ndarray:
    replica = np.asarray(symbol_replica, dtype=int).copy()
    m = 1 if stage == 1 else m_param
    norms = calculate_norm(replica, stage, qam_table, r, y_tilde, nt, m_param)
    _, sorted_idx = sort_matrix(norms)
    sorted_idx = sorted_idx[:m_param].T + 1
    if stage >= 2:
        for i in range(m):
            sorted_idx[1:stage, i] = replica[: stage - 1, sorted_idx[1, i] - 1, nt + 1 - stage]
    if stage == 1:
        replica[:stage, :, nt - stage] = sorted_idx[:1, :]
    else:
        replica[:stage, :, nt - stage] = sorted_idx[:stage, :]
    return replica
