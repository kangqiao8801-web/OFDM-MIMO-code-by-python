from __future__ import annotations

from itertools import combinations, product

import numpy as np
from numpy.typing import ArrayLike

from .capacity import water_pouring
from .modulation import QAM16_SOFT_TABLE, modulo, qam16_slicer_soft, qam_demod, qam_mod


def alamouti_encode(symbols: ArrayLike) -> np.ndarray:
    x = np.asarray(symbols, dtype=complex)
    if x.shape[-1] != 2:
        raise ValueError("Alamouti code expects pairs of symbols.")
    out = np.empty((2, 2, x.reshape(-1, 2).shape[0]), dtype=complex)
    flat = x.reshape(-1, 2)
    out[0, 0] = flat[:, 0]
    out[0, 1] = flat[:, 1]
    out[1, 0] = -np.conj(flat[:, 1])
    out[1, 1] = np.conj(flat[:, 0])
    return np.moveaxis(out, -1, 0)


def alamouti_decode_2x1(r1: ArrayLike, r2: ArrayLike, h: ArrayLike) -> np.ndarray:
    y1 = np.asarray(r1, dtype=complex).ravel()
    y2 = np.asarray(r2, dtype=complex).ravel()
    ch = np.asarray(h, dtype=complex).reshape(-1, 2)
    z1 = y1 * np.conj(ch[:, 0]) + np.conj(y2) * ch[:, 1]
    z2 = y1 * np.conj(ch[:, 1]) - np.conj(y2) * ch[:, 0]
    gain = np.sum(np.abs(ch) ** 2, axis=1)
    return np.column_stack([z1 / gain, z2 / gain])


def alamouti_combine_2rx(r1: ArrayLike, r2: ArrayLike, h: ArrayLike) -> np.ndarray:
    y1 = np.asarray(r1, dtype=complex)
    y2 = np.asarray(r2, dtype=complex)
    ch = np.asarray(h, dtype=complex)
    z1 = np.sum(y1 * np.conj(ch[:, 0, :]) + np.conj(y2) * ch[:, 1, :], axis=1)
    z2 = np.sum(y1 * np.conj(ch[:, 1, :]) - np.conj(y2) * ch[:, 0, :], axis=1)
    gain = np.sum(np.abs(ch) ** 2, axis=(1, 2))
    return np.column_stack([z1 / gain, z2 / gain])


def stbc_3x4_code(symbols: ArrayLike) -> np.ndarray:
    x = np.asarray(symbols, dtype=complex).reshape(-1, 4)
    out = np.zeros((8, 3, x.shape[0]), dtype=complex)
    out[0] = x[:, [0, 1, 2]].T
    out[1] = np.column_stack([-x[:, 1], x[:, 0], -x[:, 3]]).T
    out[2] = np.column_stack([-x[:, 2], x[:, 3], x[:, 0]]).T
    out[3] = np.column_stack([-x[:, 3], -x[:, 2], x[:, 1]]).T
    out[4:] = np.conj(out[:4])
    return out


def mrc_combine(received: ArrayLike, channel: ArrayLike, constellation: ArrayLike) -> np.ndarray:
    r = np.asarray(received, dtype=complex)
    h = np.asarray(channel, dtype=complex)
    z = np.sum(r * np.conj(h), axis=1)
    habs = np.sum(np.abs(h) ** 2, axis=1)
    table = np.asarray(constellation, dtype=complex).ravel()
    metrics = np.abs(z[:, None] - table[None, :]) ** 2 + (-1 + habs[:, None]) * np.abs(table[None, :]) ** 2
    return table[np.argmin(metrics, axis=1)]


def mmse_detect(y: ArrayLike, h: ArrayLike, sigma2: float, constellation: ArrayLike) -> np.ndarray:
    y_arr = np.asarray(y, dtype=complex).ravel()
    h_arr = np.asarray(h, dtype=complex)
    w = np.linalg.solve(h_arr.conj().T @ h_arr + sigma2 * np.eye(h_arr.shape[1]), h_arr.conj().T)
    return _slice_constellation(w @ y_arr, constellation)


def osic_detector(y: ArrayLike, h: ArrayLike, sigma2: float, nt: int | None = None, osic_type: int = 1, constellation: ArrayLike | None = None) -> np.ndarray:
    table = qam_mod(np.arange(16), 16) if constellation is None else np.asarray(constellation, dtype=complex)
    y_work = np.asarray(y, dtype=complex).ravel().copy()
    h_work = np.asarray(h, dtype=complex).copy()
    nt = h_work.shape[1] if nt is None else nt
    remaining = list(range(nt))
    out = np.zeros(nt, dtype=complex)
    for _ in range(nt):
        if osic_type == 2:
            local = int(np.argmax(np.linalg.norm(h_work, axis=0)))
            w = np.linalg.pinv(h_work)
        else:
            w = np.linalg.solve(h_work.conj().T @ h_work + (sigma2 if osic_type == 1 else 0) * np.eye(h_work.shape[1]), h_work.conj().T)
            if osic_type == 1:
                wh = w @ h_work
                scores = []
                for i in range(h_work.shape[1]):
                    interference = np.linalg.norm(np.delete(wh[i], i)) ** 2 + sigma2 * np.linalg.norm(w[i]) ** 2
                    scores.append(np.abs(wh[i, i]) ** 2 / max(interference, np.finfo(float).eps))
                local = int(np.argmax(scores))
            else:
                local = int(np.argmin(np.linalg.norm(w, axis=1)))
        sym = _slice_constellation(np.array([w[local] @ y_work]), table)[0]
        original = remaining.pop(local)
        out[original] = sym
        y_work = y_work - h_work[:, local] * sym
        h_work = np.delete(h_work, local, axis=1)
    return out


def exhaustive_ml_detector(y: ArrayLike, h: ArrayLike, constellation: ArrayLike) -> np.ndarray:
    table = np.asarray(constellation, dtype=complex).ravel()
    h_arr = np.asarray(h, dtype=complex)
    y_arr = np.asarray(y, dtype=complex).ravel()
    best_metric = np.inf
    best = None
    for candidate in product(table, repeat=h_arr.shape[1]):
        x = np.asarray(candidate, dtype=complex)
        metric = np.linalg.norm(y_arr - h_arr @ x) ** 2
        if metric < best_metric:
            best_metric = metric
            best = x
    return np.asarray(best)


def qrm_mld_detector(y: ArrayLike, h: ArrayLike, m: int = 4, constellation: ArrayLike | None = None) -> np.ndarray:
    table = qam_mod(np.arange(16), 16) if constellation is None else np.asarray(constellation, dtype=complex)
    q, r = np.linalg.qr(np.asarray(h, dtype=complex))
    yt = q.conj().T @ np.asarray(y, dtype=complex).ravel()
    nt = r.shape[1]
    candidates: list[tuple[float, np.ndarray]] = [(0.0, np.array([], dtype=complex))]
    for stage in range(nt - 1, -1, -1):
        expanded: list[tuple[float, np.ndarray]] = []
        for _, tail in candidates:
            for sym in table:
                x_tail = np.r_[sym, tail]
                rows = slice(stage, nt)
                metric = np.linalg.norm(yt[rows] - r[rows, stage:nt] @ x_tail) ** 2
                expanded.append((float(metric), x_tail))
        expanded.sort(key=lambda item: item[0])
        candidates = expanded[:m]
    return candidates[0][1]


def qrm_mld_soft(y: ArrayLike, h: ArrayLike, m: int = 8) -> np.ndarray:
    table = QAM16_SOFT_TABLE
    q, r = np.linalg.qr(np.asarray(h, dtype=complex))
    yt = q.conj().T @ np.asarray(y, dtype=complex).ravel()
    nt = r.shape[1]
    hard = qrm_mld_detector(y, h, m=m, constellation=table)
    costs0 = np.full((nt, 4), np.inf)
    costs1 = np.full((nt, 4), np.inf)
    candidates = list(product(table, repeat=nt))
    if len(candidates) > m * 16:
        center = hard
        candidates = sorted(candidates, key=lambda c: np.linalg.norm(np.asarray(c) - center))[: m * 16]
    for candidate in candidates:
        x = np.asarray(candidate)
        metric = np.linalg.norm(yt - r @ x) ** 2
        for ant, sym in enumerate(x):
            bits = qam16_slicer_soft(np.array([sym]))
            for b, bit in enumerate(bits):
                if bit == 0:
                    costs0[ant, b] = min(costs0[ant, b], metric)
                else:
                    costs1[ant, b] = min(costs1[ant, b], metric)
    return np.nan_to_num(costs0 - costs1, posinf=100.0, neginf=-100.0)


def sqrd(h: ArrayLike) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    arr = np.asarray(h, dtype=complex)
    order = np.argsort(np.linalg.norm(arr, axis=0))
    q, r = np.linalg.qr(arr[:, order], mode="reduced")
    p = np.zeros((arr.shape[1], arr.shape[1]))
    for col, original in enumerate(order):
        p[original, col] = 1
    return q, r, p, order


def original_lll(q: ArrayLike, r: ArrayLike, m: int, delta: float = 0.75) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q_arr = np.asarray(q, dtype=float).copy()
    r_arr = np.asarray(r, dtype=float).copy()
    t = np.eye(m)
    k = 1
    while k < m:
        for j in range(k - 1, -1, -1):
            mu = np.round(r_arr[j, k] / r_arr[j, j])
            if mu != 0:
                r_arr[: j + 1, k] -= mu * r_arr[: j + 1, j]
                t[:, k] -= mu * t[:, j]
        if delta * r_arr[k - 1, k - 1] ** 2 > r_arr[k, k] ** 2 + r_arr[k - 1, k] ** 2:
            r_arr[:, [k - 1, k]] = r_arr[:, [k, k - 1]]
            t[:, [k - 1, k]] = t[:, [k, k - 1]]
            norm = np.hypot(r_arr[k - 1, k - 1], r_arr[k, k - 1])
            theta = np.array([[r_arr[k - 1, k - 1] / norm, r_arr[k, k - 1] / norm], [-r_arr[k, k - 1] / norm, r_arr[k - 1, k - 1] / norm]])
            r_arr[k - 1 : k + 1, k - 1 : m] = theta @ r_arr[k - 1 : k + 1, k - 1 : m]
            q_arr[:, k - 1 : k + 1] = q_arr[:, k - 1 : k + 1] @ theta.T
            k = max(k - 1, 1)
        else:
            k += 1
    return q_arr, r_arr, t


def lrad_mmse(h_complex: ArrayLike, y: ArrayLike, noise_variance: float, delta: float = 0.75) -> np.ndarray:
    h = np.asarray(h_complex, dtype=complex)
    y_arr = np.asarray(y, dtype=complex).ravel()
    return np.linalg.solve(h.conj().T @ h + noise_variance * np.eye(h.shape[1]), h.conj().T @ y_arr)


def block_diagonalization_precoders(h1: ArrayLike, h2: ArrayLike, streams: int = 2) -> tuple[np.ndarray, np.ndarray]:
    return _nullspace(np.asarray(h2, dtype=complex))[:, :streams], _nullspace(np.asarray(h1, dtype=complex))[:, :streams]


def dirty_or_th_precoding(h_used: ArrayLike, x: ArrayLike, mode: str = "dirty") -> tuple[np.ndarray, np.ndarray]:
    q, r = np.linalg.qr(np.asarray(h_used, dtype=complex).conj().T)
    l = r.conj().T
    xp = np.asarray(x, dtype=complex).copy()
    for row in range(1, xp.shape[0]):
        xp[row] = xp[row] - (l[row, :row] / l[row, row]) @ xp[:row]
        if mode.lower().startswith("th"):
            xp[row] = modulo(xp[row], np.sqrt(2))
    return q @ xp, q


def codebook_generator() -> np.ndarray:
    nnt, nm, nl = 4, 2, 64
    kk = np.arange(nnt)
    ll = np.arange(nnt)
    w = np.exp(1j * 2 * np.pi / nnt * np.outer(kk, ll)) / np.sqrt(nnt)
    codebook = np.zeros((nnt, nm, nl), dtype=complex)
    codebook[:, :, 0] = w[:, [0, 1]]
    theta = np.diag(np.exp(1j * 2 * np.pi / nl * np.array([1, 7, 52, 56])))
    for idx in range(1, nl):
        codebook[:, :, idx] = theta @ codebook[:, :, idx - 1]
    return codebook


def mimo_capacity_ant_selection_optimal(h: ArrayLike, sel_ant: int, snr_linear: float) -> tuple[float, tuple[int, ...]]:
    arr = np.asarray(h, dtype=complex)
    best = (-np.inf, ())
    for idx in combinations(range(arr.shape[1]), sel_ant):
        hn = arr[:, idx]
        cap = np.real(np.log2(np.linalg.det(np.eye(arr.shape[0]) + snr_linear / sel_ant * hn @ hn.conj().T)))
        if cap > best[0]:
            best = (float(cap), idx)
    return best


def mimo_capacity_ant_selection_suboptimal(h: ArrayLike, sel_ant: int, snr_linear: float, method: str = "increasing") -> tuple[float, tuple[int, ...]]:
    arr = np.asarray(h, dtype=complex)
    if method.startswith("de"):
        selected = list(range(arr.shape[1]))
        while len(selected) > sel_ant:
            caps = []
            for idx in selected:
                trial = [item for item in selected if item != idx]
                hn = arr[:, trial]
                caps.append(np.real(np.log2(np.linalg.det(np.eye(arr.shape[0]) + snr_linear / sel_ant * hn @ hn.conj().T))))
            del selected[int(np.argmax(caps))]
    else:
        selected: list[int] = []
        remaining = list(range(arr.shape[1]))
        while len(selected) < sel_ant:
            caps = []
            for idx in remaining:
                trial = selected + [idx]
                hn = arr[:, trial]
                caps.append(np.real(np.log2(np.linalg.det(np.eye(arr.shape[0]) + snr_linear / sel_ant * hn @ hn.conj().T))))
            pos = int(np.argmax(caps))
            selected.append(remaining.pop(pos))
    hn = arr[:, selected]
    cap = np.real(np.log2(np.linalg.det(np.eye(arr.shape[0]) + snr_linear / sel_ant * hn @ hn.conj().T)))
    return float(cap), tuple(selected)


def multi_user_precoder(h: ArrayLike, active_users: int, sigma2: float, regularized: bool = True) -> tuple[np.ndarray, float, np.ndarray]:
    arr = np.asarray(h, dtype=complex)
    norms = np.linalg.norm(arr, axis=1)
    selected = np.argsort(-norms, kind="stable")[:active_users]
    h_used = arr[selected]
    reg = sigma2 * np.eye(active_users) if regularized else 0
    temp = h_used.conj().T @ np.linalg.inv(h_used @ h_used.conj().T + reg)
    beta = np.sqrt(h_used.shape[1] / np.trace(temp @ temp.conj().T).real)
    return beta * temp, float(beta), selected


def sttc_stage_modulation(state: str, nrx: int = 2) -> tuple[np.ndarray, np.ndarray, int]:
    mapping = {
        "4_State_4PSK": (4, 4),
        "8_State_4PSK": (4, 8),
        "16_State_4PSK": (4, 16),
        "32_State_4PSK": (4, 32),
        "8_State_8PSK": (8, 8),
        "16_State_8PSK": (8, 16),
        "32_State_8PSK": (8, 32),
        "DelayDiv_8PSK": (8, 8),
        "16_State_16qam": (16, 16),
        "DelayDiv_16qam": (16, 16),
    }
    m_order, ns = mapping[state]
    base = np.arange(1, ns + 1).reshape(ns // m_order, m_order)
    slt = np.tile(base, (m_order, 1))
    dlt = np.zeros((ns, m_order, 2), dtype=int)
    for symbol in range(m_order):
        for st in range(ns):
            dlt[st, symbol, 0] = st % m_order
            dlt[st, symbol, 1] = symbol
    return dlt, slt[:, :, None], m_order


def sttc_modulator(data: ArrayLike, m_order: int, sim_options: object | None = None) -> np.ndarray:
    arr = np.asarray(data, dtype=int)
    if m_order == 16:
        qam16 = np.array([[1, 1], [2, 1], [3, 1], [4, 1], [4, 2], [3, 2], [2, 2], [1, 2], [1, 3], [2, 3], [3, 3], [4, 3], [4, 4], [3, 4], [2, 4], [1, 4]])
        k1 = qam16[arr, 0]
        k2 = qam16[arr, 1]
        return 2 * k1 - m_order - 1 - 1j * (2 * k2 - m_order - 1)
    return np.exp(1j * 2 * np.pi / m_order * arr)


def sttc_detector(sig: ArrayLike, dlt: ArrayLike, slt: ArrayLike, ch_coefs: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    received = np.asarray(sig, dtype=complex)
    dlt_arr = np.asarray(dlt, dtype=int)
    slt_arr = np.asarray(slt, dtype=int)
    slt_lookup = slt_arr[:, :, 0] if slt_arr.ndim == 3 else slt_arr
    ch = np.asarray(ch_coefs, dtype=complex)
    steps, space_dim, packets = received.shape
    nstates, order, _ = dlt_arr.shape
    data_est = np.zeros((steps, space_dim, packets), dtype=int)
    state_est = np.zeros(steps + 1, dtype=int)
    const = qam_mod(np.arange(order), order) if order in {4, 16} else np.exp(1j * 2 * np.pi / order * np.arange(order))
    for pkt in range(packets):
        metric = np.full((steps + 1, nstates), np.inf)
        metric[0, 0] = 0
        vit_state = np.zeros((steps + 1, nstates), dtype=int)
        vit_data = np.zeros((steps + 1, nstates), dtype=int)
        for step in range(steps):
            for state in range(nstates):
                predecessors = np.argwhere(slt_lookup == state + 1)[:, 0]
                if predecessors.size == 0:
                    predecessors = np.arange(nstates)
                symbol = state % order
                best_metric = np.inf
                best_pre = 0
                for pre in predecessors:
                    q_test = const[dlt_arr[pre, symbol]]
                    distance = np.linalg.norm(received[step, :, pkt] - q_test @ ch[:, :, pkt]) ** 2
                    cand = metric[step, pre] + distance
                    if cand < best_metric:
                        best_metric = cand
                        best_pre = pre
                metric[step + 1, state] = best_metric
                vit_state[step + 1, state] = best_pre
                vit_data[step + 1, state] = symbol
        state_est[-1] = int(np.argmin(metric[-1]))
        for step in range(steps - 1, -1, -1):
            data_est[step, :, pkt] = vit_data[step + 1, state_est[step + 1]]
            state_est[step] = vit_state[step + 1, state_est[step + 1]]
    return data_est, state_est


def water_pouring_power(lamda: ArrayLike, snr: float, nt: int) -> np.ndarray:
    return water_pouring(lamda, snr, nt)


def _slice_constellation(values: np.ndarray, constellation: ArrayLike) -> np.ndarray:
    table = np.asarray(constellation, dtype=complex).ravel()
    return table[np.argmin(np.abs(values[:, None] - table[None, :]) ** 2, axis=1)]


def _nullspace(h: np.ndarray) -> np.ndarray:
    _, _, vh = np.linalg.svd(h)
    rank = np.linalg.matrix_rank(h)
    return vh.conj().T[:, rank:]
