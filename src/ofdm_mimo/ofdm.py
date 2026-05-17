from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

from .modulation import qam_mod


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


def add_cfo(y: ArrayLike, cfo: float, nfft: int) -> np.ndarray:
    arr = np.asarray(y, dtype=complex)
    n = np.arange(arr.size)
    return arr * np.exp(1j * 2 * np.pi * cfo * n / nfft)


def add_sto(y: ArrayLike, isto: int) -> np.ndarray:
    arr = np.asarray(y)
    if isto >= 0:
        return np.r_[arr[isto:], np.zeros(isto, dtype=arr.dtype)]
    return np.r_[np.zeros(-isto, dtype=arr.dtype), arr[:isto]]


def add_pilot(x: ArrayLike, nfft: int, nps: int = 4) -> np.ndarray:
    xp = np.asarray(x, dtype=complex).copy()
    if xp.size != nfft:
        raise ValueError(f"Expected {nfft} subcarriers, got {xp.size}.")
    npilots = nfft // nps
    for k in range(npilots):
        xp[k * nps] = np.exp(1j * np.pi * k**2 / npilots)
    return xp


def cfo_cp(y: ArrayLike, nfft: int, ng: int) -> float:
    arr = np.asarray(y, dtype=complex)
    metric = arr[nfft : nfft + ng] @ arr[:ng].conj()
    return float(np.angle(metric) / (2 * np.pi))


def cfo_moose(y: ArrayLike, nfft: int) -> float:
    arr = np.asarray(y, dtype=complex)
    y0 = np.fft.fft(arr[:nfft], nfft)
    y1 = np.fft.fft(arr[nfft : 2 * nfft], nfft)
    return float(np.angle(y1 @ y0.conj()) / (2 * np.pi))


def cfo_classen(yp: ArrayLike, nfft: int, ng: int, nps_or_xp: int | ArrayLike) -> float:
    arr = np.asarray(yp, dtype=complex)
    xp = add_pilot(np.zeros(nfft, dtype=complex), nfft, nps_or_xp) if np.isscalar(nps_or_xp) else np.asarray(nps_or_xp, dtype=complex)
    pilot_idx = np.flatnonzero(np.abs(xp) > 0)
    nofdm = nfft + ng
    y_pilots = []
    for i in range(2):
        sym = remove_cp(arr[i * nofdm : (i + 1) * nofdm], ng)
        y_pilots.append(np.fft.fft(sym, nfft)[pilot_idx])
    metric = (y_pilots[1] * xp[pilot_idx]) @ (y_pilots[0] * xp[pilot_idx]).conj()
    return float(np.angle(metric) / (2 * np.pi) * nfft / nofdm)


def sto_by_correlation(y: ArrayLike, nfft: int, ng: int, com_delay: int | None = None) -> tuple[int, np.ndarray]:
    arr = np.asarray(y, dtype=complex)
    nofdm = nfft + ng
    if com_delay is None:
        com_delay = nofdm // 2
    mag = np.zeros(nofdm)
    window = arr[com_delay : com_delay + ng] @ arr[com_delay + nfft : com_delay + nfft + ng].conj()
    maximum = abs(window)
    sto_est = 0
    for n in range(nofdm):
        yy1 = arr[n + com_delay] * arr[n + com_delay + nfft].conj()
        yy2 = arr[n + com_delay + ng] * arr[n + com_delay + nfft + ng].conj()
        window = window - yy1 + yy2
        mag[n] = abs(window)
        if mag[n] > maximum:
            maximum = mag[n]
            sto_est = nofdm - com_delay - n
    return int(sto_est), mag


def sto_by_difference(y: ArrayLike, nfft: int, ng: int, com_delay: int | None = None) -> tuple[int, np.ndarray]:
    arr = np.asarray(y, dtype=complex)
    nofdm = nfft + ng
    if com_delay is None:
        com_delay = nofdm // 2
    mag = np.zeros(nofdm)
    minimum = np.inf
    sto_est = 0
    for n in range(nofdm):
        idx = n + com_delay + np.arange(ng)
        diff = np.abs(arr[idx]) - np.abs(arr[idx + nfft])
        mag[n] = float(diff @ diff.conj())
        if mag[n] < minimum:
            minimum = mag[n]
            sto_est = nofdm - com_delay - n
    return int(sto_est), mag


def papr(x: ArrayLike) -> tuple[float, float, float]:
    """Return PAPR, average power, and peak power in dB using MATLAB PAPR.m semantics."""
    arr = np.asarray(x)
    power = arr.real * arr.real + arr.imag * arr.imag
    peak = np.max(power)
    avg = np.mean(power)
    return float(10 * np.log10(peak / avg)), float(10 * np.log10(avg)), float(10 * np.log10(peak))


def ifft_oversampling(x: ArrayLike, n: int, oversampling: int) -> np.ndarray:
    arr = np.asarray(x, dtype=complex).ravel()
    if arr.size != n:
        raise ValueError(f"Expected {n} frequency samples, got {arr.size}.")
    nl = n * oversampling
    spectrum = np.r_[arr[: n // 2], np.zeros(nl - n, dtype=complex), arr[n // 2 :]]
    return oversampling * np.fft.ifft(spectrum, nl)


def clipping(
    x: ArrayLike,
    clipping_ratio: float,
    sigma: float | None = None,
    return_sigma: bool = False,
) -> np.ndarray | tuple[np.ndarray, float]:
    arr = np.asarray(x)
    if sigma is None:
        dev = arr - np.mean(arr)
        sigma = float(np.sqrt(np.vdot(dev, dev).real / arr.size))
    threshold = clipping_ratio * sigma
    magnitude = np.abs(arr)
    scale = np.ones_like(magnitude, dtype=float)
    mask = magnitude > threshold
    scale[mask] = threshold / magnitude[mask]
    clipped = arr * scale
    if return_sigma:
        return clipped, sigma
    return clipped


def ccdf_from_papr_db(papr_db: ArrayLike, thresholds_db: ArrayLike) -> np.ndarray:
    values = np.asarray(papr_db, dtype=float)
    thresholds = np.asarray(thresholds_db, dtype=float)
    return np.array([np.mean(values > threshold) for threshold in thresholds])


def ccdf_ofdma(
    n: int = 256,
    nos: int = 4,
    b: int = 2,
    dbs: ArrayLike | None = None,
    nblk: int = 100,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    rng = np.random.default_rng() if rng is None else rng
    dbs_arr = np.arange(0, 12) if dbs is None else np.asarray(dbs, dtype=float)
    order = 2**b
    papr_db = np.zeros(nblk)
    for idx in range(nblk):
        symbols = qam_mod(rng.integers(0, order, size=n), order)
        zero_pad = np.zeros(n * nos, dtype=complex)
        zero_pad[::nos] = symbols
        time = np.fft.ifft(zero_pad, n * nos)
        power = np.abs(time) ** 2
        papr_db[idx] = 10 * np.log10(np.max(power) / np.mean(power))
    return np.array([np.mean(papr_db > threshold) for threshold in dbs_arr])


def ccdf_pts(
    n: int,
    nos: int,
    nsb: int,
    b: int,
    dbs: ArrayLike,
    nblk: int,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    rng = np.random.default_rng() if rng is None else rng
    nnos = n * nos
    order = 2**b
    paprs = np.zeros(nblk)
    for idx in range(nblk):
        symbols = qam_mod(rng.integers(0, order, size=n), order)
        padded = np.zeros(nnos, dtype=complex)
        padded[::nos] = symbols
        subblocks = np.zeros((nsb, nnos), dtype=complex)
        width = nnos // nsb
        for k in range(nsb):
            sl = slice(k * width, (k + 1) * width)
            subblocks[k, sl] = padded[sl]
        ifft_blocks = np.fft.ifft(subblocks, nnos, axis=1)
        weights = np.ones(nsb)
        best = np.inf
        for k in range(nsb):
            candidate = weights @ ifft_blocks
            p = np.abs(candidate) ** 2
            current = np.max(p) / np.mean(p)
            if current < best:
                best = current
            else:
                weights[k] = 1
            if k + 1 < nsb:
                weights[k + 1] = -1
        selected = weights @ ifft_blocks
        p = np.abs(selected) ** 2
        paprs[idx] = np.max(p) / np.mean(p)
    return ccdf_from_papr_db(10 * np.log10(paprs), dbs)


def raised_cosine_filter(rolloff: float, nsym: int, nos: int) -> np.ndarray:
    t = np.arange(-nsym * nos, nsym * nos + 1, dtype=float) / nos
    taps = np.zeros_like(t)
    for idx, ti in enumerate(t):
        if abs(ti) < 1e-12:
            taps[idx] = 1.0
        elif rolloff and abs(abs(2 * rolloff * ti) - 1) < 1e-12:
            taps[idx] = np.pi / 4 * np.sinc(1 / (2 * rolloff))
        else:
            denom = 1 - (2 * rolloff * ti) ** 2
            taps[idx] = np.sinc(ti) * np.cos(np.pi * rolloff * ti) / denom
    return taps / np.sqrt(np.sum(taps**2)) * nos


def ccdf_papr_dft_spreading(
    fdma_type: str,
    ndb: int,
    b: int,
    n: int,
    thresholds_db: ArrayLike,
    nblk: int,
    psf: ArrayLike | None = None,
    nos: int | None = None,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng() if rng is None else rng
    order = 2**b
    spread = n // ndb
    paprs = np.zeros(nblk)
    mode = fdma_type.upper()[:2]
    for idx in range(nblk):
        symbols = qam_mod(rng.integers(0, order, size=ndb), order)
        if mode == "IF":
            freq = np.zeros(n, dtype=complex)
            freq[::spread] = np.fft.fft(symbols, ndb)
        elif mode == "LF":
            freq = np.r_[np.fft.fft(symbols, ndb), np.zeros(n - ndb, dtype=complex)]
        elif mode == "OF":
            freq = np.zeros(n, dtype=complex)
            freq[::spread] = symbols
        else:
            freq = symbols
        time = np.fft.ifft(freq, n)
        if nos is not None:
            upsampled = np.zeros(time.size * nos, dtype=complex)
            upsampled[::nos] = time
            time = upsampled
        if psf is not None:
            time = np.convolve(time, np.asarray(psf, dtype=float))
        power = np.abs(time) ** 2
        paprs[idx] = np.max(power) / np.mean(power)
    papr_db = 10 * np.log10(paprs)
    return ccdf_from_papr_db(papr_db, thresholds_db), paprs
