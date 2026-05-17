from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike
from scipy.linalg import sqrtm, toeplitz
from scipy.signal import fftconvolve

from .utils import gen_filter


def pl_free(fc: float, dist: ArrayLike, gt: float | None = None, gr: float | None = None) -> np.ndarray:
    lam = 3e8 / fc
    tmp = lam / (4 * np.pi * np.asarray(dist, dtype=float))
    if gt is not None:
        tmp = tmp * np.sqrt(gt)
    if gr is not None:
        tmp = tmp * np.sqrt(gr)
    return -20 * np.log10(tmp)


def pl_logdist_or_norm(
    fc: float,
    d: ArrayLike,
    d0: float,
    n: float,
    sigma: float | None = None,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    d_arr = np.asarray(d, dtype=float)
    lam = 3e8 / fc
    loss = -20 * np.log10(lam / (4 * np.pi * d0)) + 10 * n * np.log10(d_arr / d0)
    if sigma is not None:
        rng = np.random.default_rng() if rng is None else rng
        loss = loss + sigma * rng.normal(size=d_arr.shape)
    return loss


def pl_hata(fc: float, d: ArrayLike, htx: float, hrx: float, etype: str = "urban") -> np.ndarray:
    fc_mhz = fc / 1e6
    if 150 <= fc_mhz <= 200:
        c_rx = 8.29 * (np.log10(1.54 * hrx)) ** 2 - 1.1
    elif fc_mhz > 200:
        c_rx = 3.2 * (np.log10(11.75 * hrx)) ** 2 - 4.97
    else:
        c_rx = 0.8 + (1.1 * np.log10(fc_mhz) - 0.7) * hrx - 1.56 * np.log10(fc_mhz)
    d_arr = np.asarray(d, dtype=float)
    loss = 69.55 + 26.16 * np.log10(fc_mhz) - 13.82 * np.log10(htx) - c_rx
    loss = loss + (44.9 - 6.55 * np.log10(htx)) * np.log10(d_arr / 1000)
    typ = etype.upper()
    if typ.startswith("S"):
        loss = loss - 2 * (np.log10(fc_mhz / 28)) ** 2 - 5.4
    elif typ.startswith("O"):
        loss = loss + (18.33 - 4.78 * np.log10(fc_mhz)) * np.log10(fc_mhz) - 40.97
    return loss


def pl_ieee80216d(
    fc: float,
    d: ArrayLike,
    typ: str = "A",
    htx: float = 30,
    hrx: float = 2,
    corr_fact: str = "NO",
    mod: str = "UNMOD",
) -> np.ndarray:
    d0 = 100
    typ_u = typ.upper()[0]
    if typ_u not in {"A", "B", "C"}:
        raise ValueError("type must be A, B, or C")
    corr = corr_fact.upper()
    if corr == "ATNT":
        cf = 6 * np.log10(fc / 2e9)
        c_rx = -10.8 * np.log10(hrx / 2)
    elif corr == "OKUMURA":
        cf = 6 * np.log10(fc / 2e9)
        c_rx = -10 * np.log10(hrx / 3) if hrx <= 3 else -20 * np.log10(hrx / 3)
    else:
        cf = 0.0
        c_rx = 0.0
    params = {"A": (4.6, 0.0075, 12.6), "B": (4.0, 0.0065, 17.1), "C": (3.6, 0.005, 20.0)}
    a, b, c = params[typ_u]
    gamma = a - b * htx + c / htx
    lam = 3e8 / fc
    d0_pr = d0 * 10 ** (-(cf + c_rx) / (10 * gamma)) if mod.upper().startswith("M") else d0
    a0 = 20 * np.log10(4 * np.pi * d0_pr / lam) + cf + c_rx
    d_arr = np.asarray(d, dtype=float)
    return np.where(d_arr > d0_pr, a0 + 10 * gamma * np.log10(d_arr / d0), -10 * np.log10((lam / (4 * np.pi * d_arr)) ** 2))


def doppler_psd(kind: str, f0: ArrayLike, *args: float) -> np.ndarray:
    x = np.asarray(f0, dtype=float)
    eps = 1e-9
    key = kind.lower()[:2]
    if key == "fl":
        return np.ones_like(x)
    if key == "cl":
        return 1 / np.sqrt(np.maximum(1 + eps - x**2, eps))
    if key == "la":
        sigma, phi = args
        return (np.exp(-np.sqrt(2) / sigma * np.abs(np.arccos(x) - phi)) + np.exp(-np.sqrt(2) / sigma * np.abs(np.arccos(x) + phi))) / np.sqrt(
            np.maximum(1 + eps - x**2, eps)
        )
    if key == "su":
        return 0.785 * x**4 - 1.72 * x**2 + 1
    if kind.lower().startswith("3g"):
        f, fm = x, args[0]
        return 0.41 / (2 * np.pi * fm * np.sqrt(np.maximum(1 + eps - (f / fm) ** 2, eps)))
    if key == "dr":
        dsp, dsh = args
        return (1 / np.sqrt(2 * np.pi * dsp / 2)) * np.exp(-((x - dsh) ** 2) / dsp)
    raise ValueError(f"unknown Doppler type {kind}")


def doppler_spectrum(fd: float, nfft: int) -> np.ndarray:
    df = 2 * fd / nfft
    f = np.zeros(nfft // 2 + 1)
    y = np.zeros(nfft)
    y[0] = 1.5 / (np.pi * fd)
    for i in range(1, nfft // 2):
        f[i] = i * df
        val = 1.5 / (np.pi * fd * np.sqrt(max(1 - (f[i] / fd) ** 2, np.finfo(float).eps)))
        y[i] = val
        y[nfft - i] = val
    nfit = min(3, nfft // 2 - 1)
    kk = np.arange(nfft // 2 - nfit, nfft // 2 + 1)
    valid = kk[kk < nfft // 2]
    nfit = min(nfit, valid.size - 1)
    coeff = np.polyfit(f[valid], y[valid], nfit)
    y[nfft // 2] = np.polyval(coeff, f[nfft // 2 - 1] + df)
    return y


def fwgn(fm: float, fs: float, n: int, rng: np.random.Generator | None = None) -> tuple[np.ndarray, int, int, np.ndarray]:
    rng = np.random.default_rng() if rng is None else rng
    nfft = 2 ** max(3, int(np.ceil(np.log2(2 * fm / fs * n))))
    nifft = int(np.ceil(nfft * fs / (2 * fm)))
    gi = rng.normal(size=nfft)
    gq = rng.normal(size=nfft)
    cgi = np.fft.fft(gi)
    cgq = np.fft.fft(gq)
    coeff = doppler_spectrum(fm, nfft)
    zeros = np.zeros(nifft - nfft)
    filt_i = np.r_[cgi[: nfft // 2] * np.sqrt(coeff[: nfft // 2]), zeros, cgi[nfft // 2 :] * np.sqrt(coeff[nfft // 2 :])]
    filt_q = np.r_[cgq[: nfft // 2] * np.sqrt(coeff[: nfft // 2]), zeros, cgq[nfft // 2 :] * np.sqrt(coeff[nfft // 2 :])]
    hi = np.fft.ifft(filt_i)
    hq = np.fft.ifft(filt_q)
    env = np.sqrt(np.abs(hi) ** 2 + np.abs(hq) ** 2)
    rms = np.sqrt(np.mean(env[:n] ** 2))
    return (hi[:n].real - 1j * hq[:n].real) / rms, nfft, nifft, coeff


def fwgn_ff(
    npaths: int,
    fm_hz: ArrayLike,
    nfading: int,
    nfosf: int,
    fading_type: str,
    *args: ArrayLike,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, float]:
    rng = np.random.default_rng() if rng is None else rng
    fm = _as_path_vector(fm_hz, npaths)
    fmax = float(np.max(fm))
    dfmax = 2 * nfosf * fmax / nfading
    freq = np.zeros((npaths, nfading), dtype=float)
    for p in range(npaths):
        nd = int(np.floor(fm[p] / dfmax) - 1)
        if nd < 1:
            raise ValueError("increase IFFT size")
        vals = doppler_psd(fading_type, np.arange(0, nd + 1) / nd)
        row = np.r_[vals[: nd - 1], np.zeros(nfading - 2 * nd + 3), vals[1:nd][::-1]]
        freq[p, : row.size] = row[:nfading]
    phase = np.exp(2j * np.pi * rng.random((npaths, nfading)))
    time = np.fft.ifft(np.sqrt(np.maximum(freq, 0)) * phase, nfading, axis=1)
    time = _normalize_rows(time)
    return time, 1 / (2 * fmax * nfosf)


def fwgn_tf(
    npaths: int,
    fm_hz: ArrayLike,
    n: int,
    m: int,
    nfosf: int,
    fading_type: str,
    *args: float,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, float]:
    rng = np.random.default_rng() if rng is None else rng
    fm = _as_path_vector(fm_hz, npaths)
    fmax = float(np.max(fm))
    wgn = (rng.normal(size=(npaths, n)) + 1j * rng.normal(size=(npaths, n))) / np.sqrt(2)
    out = np.zeros((npaths, n), dtype=complex)
    for p in range(npaths):
        filt = gen_filter(float(fm[p]), fmax, m, nfosf, fading_type, *args)
        padded = np.r_[wgn[p], np.zeros(m, dtype=complex)]
        conv = fftconvolve(padded, filt, mode="full")
        start = m // 2
        out[p] = conv[start : start + n]
    return _normalize_rows(out), 1 / (2 * fmax * nfosf)


def jakes_flat(fd: float, ts: float, ns: int, t0: float = 0, e0: float = 1, phi_n: float = 0) -> tuple[np.ndarray, float]:
    n0 = 8
    n = 4 * n0 + 2
    wd = 2 * np.pi * fd
    t = t0 + np.arange(ns) * ts
    rows = [np.sqrt(2) * np.cos(wd * t)]
    for k in range(1, n0 + 1):
        rows.append(2 * np.cos(wd * np.cos(2 * np.pi * k / n) * t))
    coswt = np.vstack(rows)
    phase = np.exp(1j * np.r_[phi_n, np.pi / (n0 + 1) * np.arange(1, n0 + 1)])
    return e0 / np.sqrt(2 * n0 + 1) * (phase @ coswt), float(t[-1] + ts)


def ray_model(length: int, rng: np.random.Generator | None = None) -> np.ndarray:
    rng = np.random.default_rng() if rng is None else rng
    return (rng.normal(size=length) + 1j * rng.normal(size=length)) / np.sqrt(2)


def ric_model(k_db: float, length: int, rng: np.random.Generator | None = None) -> np.ndarray:
    k = 10 ** (k_db / 10)
    return np.sqrt(k / (k + 1)) + np.sqrt(1 / (k + 1)) * ray_model(length, rng)


def channel_coeff(
    nt: int,
    nr: int,
    n: int,
    rtx: ArrayLike | None = None,
    rrx: ArrayLike | None = None,
    corr_type: str = "complex",
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    rng = np.random.default_rng() if rng is None else rng
    h = (rng.normal(size=(nt * nr, n)) + 1j * rng.normal(size=(nt * nr, n))) / np.sqrt(2)
    if rtx is None or rrx is None:
        return h.reshape(n, nr, nt).transpose(1, 2, 0)
    tx = _corr_matrix(rtx)
    rx = _corr_matrix(rrx)
    kron = np.kron(tx, rx)
    c = np.linalg.cholesky(kron).T if corr_type == "complex" else sqrtm(sqrtm(kron))
    out = np.zeros((nr, nt, n), dtype=complex)
    for i in range(n):
        out[:, :, i] = (c @ h[:, i]).reshape(nr, nt)
    return out


def channel1(sig: ArrayLike, snr_db: float, nr: int, rng: np.random.Generator | None = None) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng() if rng is None else rng
    arr = np.asarray(sig, dtype=complex)
    n_frame, _, n_packets = arr.shape
    spowr = np.sum(np.abs(arr[:, 0, 0])) / n_frame
    sigma = np.sqrt(0.5 * spowr * 10 ** (-snr_db / 10))
    coefs = (rng.normal(size=(2, nr, n_packets)) + 1j * rng.normal(size=(2, nr, n_packets))) / np.sqrt(2)
    noise = sigma * (rng.normal(size=(n_frame, nr, n_packets)) + 1j * rng.normal(size=(n_frame, nr, n_packets)))
    out = np.zeros((n_frame, nr, n_packets), dtype=complex)
    for k in range(n_packets):
        out[:, :, k] = arr[:, :, k] @ coefs[:, :, k]
    return out + noise, coefs


def ieee802_11_model(sigma_tau: float, ts: float) -> np.ndarray:
    lmax = int(np.ceil(10 * sigma_tau / ts))
    sigma02 = (1 - np.exp(-ts / sigma_tau)) / (1 - np.exp(-(lmax + 1) * ts / sigma_tau))
    taps = np.arange(lmax + 1)
    return sigma02 * np.exp(-taps * ts / sigma_tau)


def sui_parameters(ch_no: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float]:
    if ch_no < 1 or ch_no > 6:
        raise ValueError("SUI channel number must be 1..6")
    delays = np.array([[0, 0.4, 0.9], [0, 0.4, 1.1], [0, 0.4, 0.9], [0, 1.5, 4], [0, 4, 10], [0, 14, 20]], dtype=float)
    powers = np.array([[0, -15, -20], [0, -12, -15], [0, -5, -10], [0, -4, -8], [0, -5, -10], [0, -10, -14]], dtype=float)
    ks = np.array([[4, 0, 0], [2, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]], dtype=float)
    dopplers = np.array([[0.4, 0.3, 0.5], [0.2, 0.15, 0.25], [0.4, 0.3, 0.5], [0.2, 0.15, 0.25], [2, 1.5, 2.5], [0.4, 0.3, 0.5]])
    corr = np.array([0.7, 0.5, 0.4, 0.3, 0.5, 0.3])
    fnorm = np.array([-0.1771, -0.393, -1.5113, -1.9218, -1.5113, -0.5683])
    idx = ch_no - 1
    return delays[idx], powers[idx], ks[idx], dopplers[idx], float(corr[idx]), float(fnorm[idx])


def sui_fading(
    p_db: ArrayLike,
    k_factor: ArrayLike,
    doppler_shift_hz: ArrayLike,
    fnorm_db: float,
    n: int,
    m: int,
    nfosf: int,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, float]:
    power = 10 ** (np.asarray(p_db, dtype=float) / 10)
    k = np.asarray(k_factor, dtype=float)
    scatter = np.sqrt(power / (k + 1))
    mean = np.sqrt(power * k / (k + 1))
    fad, tf = fwgn_tf(power.size, doppler_shift_hz, n, m, nfosf, "sui", rng=rng)
    return (fad * scatter[:, None] + mean[:, None]) * 10 ** (fnorm_db / 20), tf


def uwb_parameters(cm: int) -> tuple[float, float, float, float, int, float, float, float]:
    tmp = 4.8 / np.sqrt(2)
    table = np.array(
        [
            [0.0233, 2.5, 7.1, 4.3, 0, 3, tmp, tmp],
            [0.4, 0.5, 5.5, 6.7, 1, 3, tmp, tmp],
            [0.0667, 2.1, 14.0, 7.9, 1, 3, tmp, tmp],
            [0.0667, 2.1, 24.0, 12.0, 1, 3, tmp, tmp],
        ]
    )
    row = table[cm - 1]
    return float(row[0]), float(row[1]), float(row[2]), float(row[3]), int(row[4]), float(row[5]), float(row[6]), float(row[7])


def uwb_model_ct(
    lam_cluster: float,
    lam_ray: float,
    gam_cluster: float,
    gam_ray: float,
    nlos: int,
    sdi: float,
    sdc: float,
    sdr: float,
    num_ch: int,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng() if rng is None else rng
    h_cols: list[np.ndarray] = []
    t_cols: list[np.ndarray] = []
    t0 = np.zeros(num_ch)
    counts = np.zeros(num_ch, dtype=int)
    sd_lam = 1 / np.sqrt(2 * lam_cluster)
    sd_ray = 1 / np.sqrt(2 * lam_ray)
    mu_const = (sdc**2 + sdr**2) * np.log(10) / 20
    for k in range(num_ch):
        tc = (sd_lam * rng.normal()) ** 2 + (sd_lam * rng.normal()) ** 2 if nlos else 0.0
        t0[k] = tc
        vals: list[float] = []
        times: list[float] = []
        while tc < 10 * gam_cluster:
            tr = 0.0
            ln_xi = sdc * rng.normal()
            while tr < 10 * gam_ray:
                mu = (-10 * tc / gam_cluster - 10 * tr / gam_ray) / np.log(10) - mu_const
                sign = 1 if rng.random() >= 0.5 else -1
                vals.append(sign * 10 ** ((ln_xi + mu + sdr * rng.normal()) / 20))
                times.append(tc + tr)
                tr += (sd_ray * rng.normal()) ** 2 + (sd_ray * rng.normal()) ** 2
            tc += (sd_lam * rng.normal()) ** 2 + (sd_lam * rng.normal()) ** 2
        h_col, t_col = _sort_and_shadow(vals, times, sdi, rng)
        h_cols.append(h_col)
        t_cols.append(t_col)
        counts[k] = h_col.size
    return _pack_columns(h_cols, complex), _pack_columns(t_cols, float), t0, counts


def sv_model_ct(
    lam_cluster: float,
    lam_ray: float,
    gam_cluster: float,
    gam_ray: float,
    num_ch: int,
    b002: float = 1,
    sdi: float = 0,
    nlos: int = 0,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng() if rng is None else rng
    h_cols: list[np.ndarray] = []
    t_cols: list[np.ndarray] = []
    t0 = np.zeros(num_ch)
    counts = np.zeros(num_ch, dtype=int)
    for k in range(num_ch):
        tc = rng.exponential(1 / lam_cluster) if nlos else 0.0
        t0[k] = tc
        vals: list[complex] = []
        times: list[float] = []
        while tc < 10 * gam_cluster:
            tr = 0.0
            while tr < 10 * gam_ray:
                power = b002 * np.exp(-tc / gam_cluster) * np.exp(-tr / gam_ray)
                r = np.hypot(rng.normal(), rng.normal()) * np.sqrt(power / 2)
                vals.append(np.exp(2j * np.pi * rng.random()) * r)
                times.append(tc + tr)
                tr += rng.exponential(1 / lam_cluster)
            tc += rng.exponential(1 / lam_ray)
        h_col, t_col = _sort_and_shadow(vals, times, sdi, rng)
        h_cols.append(h_col)
        t_cols.append(t_col)
        counts[k] = h_col.size
    return _pack_columns(h_cols, complex), _pack_columns(t_cols, float), t0, counts


def convert_uwb_ct(h_ct: ArrayLike, t: ArrayLike, np_paths: ArrayLike, num_channels: int, ts: float) -> tuple[np.ndarray, int]:
    h_arr = np.asarray(h_ct)
    t_arr = np.asarray(t, dtype=float)
    counts = np.asarray(np_paths, dtype=int)
    oversampling = 2 ** int(np.ceil(np.log2(max(1, np.ceil(100 * ts)))))
    nfs = oversampling / ts
    h_len = 1 + int(np.floor(np.max(t_arr) * nfs))
    out = np.zeros((h_len, num_channels), dtype=h_arr.dtype)
    for k in range(num_channels):
        idx = np.floor(t_arr[: counts[k], k] * nfs).astype(int)
        for src, dst in enumerate(idx):
            out[dst, k] += h_arr[src, k]
    return out, oversampling


uwb_convert_ct = convert_uwb_ct


def ray_fading(
    m: int,
    pdp: ArrayLike,
    bs_phi_rad: ArrayLike,
    ms_theta_deg: ArrayLike,
    v_ms: float,
    theta_v_deg: float,
    wavelength: float,
    t: ArrayLike,
) -> np.ndarray:
    pdp_arr = np.asarray(pdp, dtype=float).ravel()
    phase = np.asarray(bs_phi_rad, dtype=float)
    theta = np.deg2rad(np.asarray(ms_theta_deg, dtype=float))
    theta_v = np.deg2rad(theta_v_deg)
    time = np.asarray(t, dtype=float).ravel()
    out = np.zeros((pdp_arr.size, time.size), dtype=complex)
    for n, power in enumerate(pdp_arr):
        rays = np.exp(-1j * phase[n, :m, None]) * np.exp(-1j * 2 * np.pi / wavelength * v_ms * np.cos(theta[n, :m, None] - theta_v) * time)
        out[n] = np.sqrt(power / m) * np.sum(rays, axis=0)
    return out


def _as_path_vector(values: ArrayLike, n: int) -> np.ndarray:
    arr = np.asarray(values, dtype=float).ravel()
    return np.repeat(arr, n) if arr.size == 1 else arr


def _normalize_rows(x: np.ndarray) -> np.ndarray:
    power = np.mean(np.abs(x) ** 2, axis=1, keepdims=True)
    return x / np.sqrt(power)


def _corr_matrix(values: ArrayLike) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    return toeplitz(arr) if arr.ndim == 1 else arr


def _sort_and_shadow(values: list[complex] | list[float], times: list[float], sdi: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(times)
    h = np.asarray(values)[order]
    t = np.asarray(times, dtype=float)[order]
    norm = np.sqrt(np.vdot(h, h).real)
    if norm > 0:
        h = h * (10 ** (sdi * rng.normal() / 20) / norm)
    return h, t


def _pack_columns(cols: list[np.ndarray], dtype: type) -> np.ndarray:
    max_len = max((col.size for col in cols), default=0)
    out = np.zeros((max_len, len(cols)), dtype=dtype)
    for idx, col in enumerate(cols):
        out[: col.size, idx] = col
    return out
