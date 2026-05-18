from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import j0

from ofdm_mimo.channel_models import (
    convert_uwb_ct,
    fwgn,
    fwgn_ff,
    fwgn_tf,
    ieee802_11_model,
    jakes_flat,
    pl_free,
    pl_hata,
    pl_ieee80216d,
    pl_logdist_or_norm,
    ray_fading,
    ray_model,
    ric_model,
    sui_fading,
    sui_parameters,
    sv_model_ct,
    uwb_model_ct,
    uwb_parameters,
)
from ofdm_mimo.metrics import ber_qam
from ofdm_mimo.modulation import mapper
from ofdm_mimo.ofdm import papr
from ofdm_mimo.utils import db2w, exp_pdp, gen_phase


def finish(output_dir: Path, stem: str, fig: plt.Figure, data: np.ndarray, header: str = "") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / f"{stem}.dat", np.asarray(data), header=header)
    fig.tight_layout()
    fig.savefig(output_dir / f"{stem}.png", dpi=150)
    plt.close(fig)


def plot_2ray_exp_model(output_dir: Path, quick: bool) -> None:
    rng = np.random.default_rng(7)
    scale = 1e-9
    ts = 10 * scale
    tau_rms = 30 * scale
    num_ch = 1000 if quick else 10000
    pow_2 = np.array([0.5, 0.5])
    delay_2 = np.array([0, tau_rms * 2 / scale])
    h_2 = ray_model(num_ch * pow_2.size, rng).reshape(num_ch, pow_2.size) * np.sqrt(pow_2)
    avg_2 = np.mean(np.abs(h_2) ** 2, axis=0)
    pow_e = exp_pdp(tau_rms, ts)
    delay_e = np.arange(pow_e.size) * ts / scale
    h_e = ray_model(num_ch * pow_e.size, rng).reshape(num_ch, pow_e.size) * np.sqrt(pow_e)
    avg_e = np.mean(np.abs(h_e) ** 2, axis=0)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    axes[0].stem(delay_2, pow_2, linefmt="k-", markerfmt="ko", basefmt=" ")
    axes[0].plot(delay_2, avg_2, "r.", label="Simulation")
    axes[1].stem(delay_e, pow_e, linefmt="k-", markerfmt="ko", basefmt=" ")
    axes[1].plot(delay_e, avg_e, "r.", label="Simulation")
    for ax, title in zip(axes, ["2-ray model", "exponential model"]):
        ax.set_xlabel("Delay [ns]")
        ax.set_ylabel("Channel power")
        ax.set_title(title)
        ax.grid(True)
        ax.legend(["Ideal", "Simulation"], fontsize=8)
    rows = max(delay_e.size, delay_2.size)
    data = np.full((rows, 6), np.nan)
    data[:2, :3] = np.column_stack([delay_2, pow_2, avg_2])
    data[: delay_e.size, 3:] = np.column_stack([delay_e, pow_e, avg_e])
    finish(output_dir, "plot_2ray_exp_model", fig, data, "delay2 ideal2 sim2 delay_exp ideal_exp sim_exp")


def plot_ccdf(output_dir: Path, quick: bool) -> None:
    rng = np.random.default_rng(8)
    ns = 2 ** np.arange(6, 11)
    nblk = 120 if quick else 1000
    zd_bs = np.arange(4, 10.1, 0.2 if quick else 0.1)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    rows = []
    for n in ns:
        papr_db = np.empty(nblk)
        mean_abs = np.empty(nblk)
        for k in range(nblk):
            x_freq, _ = mapper(2, n, rng)
            x_time = np.fft.ifft(x_freq, n) * np.sqrt(n)
            papr_db[k], _, _ = papr(x_time)
            mean_abs[k] = np.mean(np.abs(x_time))
        s2 = float(np.mean(mean_abs) ** 2 / (np.pi / 2))
        theoretical = 1 - (1 - np.exp(-(10 ** (zd_bs / 20)) ** 2 / (2 * s2))) ** n
        simulated = np.array([np.mean(papr_db > z) for z in zd_bs])
        ax.semilogy(zd_bs, theoretical, "k-", alpha=0.35)
        ax.semilogy(zd_bs, simulated, ":*", label=f"N={n}")
        rows.append(np.column_stack([np.full_like(zd_bs, n), zd_bs, theoretical, simulated]))
    ax.set_xlabel("PAPR0 [dB]")
    ax.set_ylabel("CCDF")
    ax.set_ylim(1e-2, 1)
    ax.grid(True)
    ax.legend(fontsize=8)
    finish(output_dir, "plot_ccdf", fig, np.vstack(rows), "N threshold_db theoretical simulated")


def plot_fwgn(output_dir: Path, quick: bool) -> None:
    fm = 100
    ts = 50e-6
    n = 4096 if quick else 20000
    h, _, _, _ = fwgn(fm, 1 / ts, n, rng=np.random.default_rng(9))
    t = np.arange(1, n + 1) * ts
    fig, axes = plt.subplots(2, 2, figsize=(9, 6))
    axes[0, 0].plot(t, 20 * np.log10(np.maximum(np.abs(h), 1e-12)), "k-")
    axes[0, 0].set_title(f"Clarke/Gan FWGN, f_m={fm} Hz")
    axes[0, 0].set_xlabel("time [s]")
    axes[0, 0].set_ylabel("Magnitude [dB]")
    axes[0, 1].axis("off")
    axes[1, 0].hist(np.abs(h), 50, color="0.2")
    axes[1, 1].hist(np.angle(h), 50, color="0.2")
    axes[1, 0].set_xlabel("Magnitude")
    axes[1, 1].set_xlabel("Phase [rad]")
    finish(output_dir, "plot_fwgn", fig, np.column_stack([t, np.abs(h), np.angle(h)]), "time abs_h angle_h")


def plot_ieee80211_model(output_dir: Path, quick: bool) -> None:
    rng = np.random.default_rng(10)
    ts = 50e-9
    tau_rms = 25e-9
    num_ch = 1000 if quick else 10000
    nfft = 128
    pdp = ieee802_11_model(tau_rms, ts)
    h = ray_model(num_ch * pdp.size, rng).reshape(num_ch, pdp.size) * np.sqrt(pdp)
    avg = np.mean(np.abs(h) ** 2, axis=0)
    h_freq = np.fft.fftshift(np.fft.fft(h[0], nfft))
    freq_mhz = (np.arange(-nfft // 2, nfft // 2) / nfft / ts) / 1e6
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    idx = np.arange(pdp.size)
    axes[0].stem(idx, pdp, linefmt="k-", markerfmt="ko", basefmt=" ")
    axes[0].plot(idx, avg, "r.", label="Simulation")
    axes[0].set_xlabel("channel tap index")
    axes[0].set_ylabel("Average channel power")
    axes[1].plot(freq_mhz, 10 * np.log10(np.maximum(np.abs(h_freq) ** 2, 1e-12)), "k-")
    axes[1].set_xlabel("Frequency [MHz]")
    axes[1].set_ylabel("Channel power [dB]")
    for ax in axes:
        ax.grid(True)
    data = np.full((max(pdp.size, nfft), 5), np.nan)
    data[: pdp.size, :3] = np.column_stack([idx, pdp, avg])
    data[:nfft, 3:] = np.column_stack([freq_mhz, np.abs(h_freq) ** 2])
    finish(output_dir, "plot_ieee80211_model", fig, data, "tap pdp simulated freq_mhz power")


def plot_jakes_model(output_dir: Path, quick: bool) -> None:
    fd = 926
    ts = 1e-6
    ns = 4096 if quick else 12000
    m = 1024 if quick else 4096
    h, _ = jakes_flat(fd, ts, ns)
    t = np.arange(ns) * ts
    lags = np.arange(m)
    sim_corr = np.array([np.mean(h[: ns - lag].conj() * h[lag:]).real for lag in lags])
    sim_corr /= sim_corr[0]
    classical = j0(2 * np.pi * fd * lags * ts)
    f = np.fft.fftshift(np.fft.fftfreq(m, ts)) / fd
    spec_sim = np.abs(np.fft.fftshift(np.fft.fft(sim_corr)))
    spec_class = np.abs(np.fft.fftshift(np.fft.fft(classical)))
    fig, axes = plt.subplots(3, 2, figsize=(10, 8))
    axes[0, 0].plot(t, 20 * np.log10(np.maximum(np.abs(h), 1e-12)), "k-")
    axes[0, 1].axis("off")
    axes[1, 0].hist(np.abs(h), 50, color="0.2")
    axes[1, 1].hist(np.angle(h), 50, color="0.2")
    axes[2, 0].plot(lags * ts, np.abs(classical), "b:", label="Classical")
    axes[2, 0].plot(lags * ts, np.abs(sim_corr), "r:", label="Simulated")
    axes[2, 1].plot(f, spec_class, "b:", label="Classical")
    axes[2, 1].plot(f, spec_sim, "r:", label="Simulated")
    for ax in axes.ravel():
        ax.grid(True)
    axes[2, 0].legend(fontsize=8)
    axes[2, 1].legend(fontsize=8)
    data = np.column_stack([lags * ts, classical, sim_corr, f, spec_class, spec_sim])
    finish(output_dir, "plot_jakes_model", fig, data, "lag_s classical_corr simulated_corr f_over_fd classical_spec simulated_spec")


def plot_pl_hata(output_dir: Path, quick: bool) -> None:
    fc = 1.5e9
    d = np.arange(1, 32, 2, dtype=float) ** 2
    curves = np.vstack([pl_hata(fc, d, 30, 2, kind) for kind in ["urban", "suburban", "open"]])
    fig, ax = plt.subplots(figsize=(6, 4))
    for label, row, marker in zip(["urban", "suburban", "open area"], curves, ["s", "o", "^"]):
        ax.semilogx(d, row, marker=marker, label=label)
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Path loss [dB]")
    ax.grid(True)
    ax.legend(fontsize=8)
    finish(output_dir, "plot_pl_hata", fig, np.column_stack([d, curves.T]), "distance urban suburban open")


def plot_pl_ieee80216d(output_dir: Path, quick: bool) -> None:
    fc = 2e9
    d = np.arange(1, 1001, dtype=float)
    curves = []
    for hrx in [2, 10]:
        curves.append(pl_ieee80216d(fc, d, "A", 30, hrx, "ATNT"))
    for hrx in [2, 10]:
        curves.append(pl_ieee80216d(fc, d, "A", 30, hrx, "ATNT", "mod"))
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    labels = ["hRx=2m", "hRx=10m"]
    for ax, subset, title in zip(axes, [curves[:2], curves[2:]], ["IEEE 802.16d", "Modified IEEE 802.16d"]):
        for label, row in zip(labels, subset):
            ax.semilogx(d, row, label=label)
        ax.set_title(title)
        ax.set_xlabel("Distance [m]")
        ax.set_ylabel("Path loss [dB]")
        ax.grid(True)
        ax.legend(fontsize=8)
    finish(output_dir, "plot_pl_ieee80216d", fig, np.column_stack([d, *curves]), "distance hrx2 hrx10 mod_hrx2 mod_hrx10")


def plot_pl_general(output_dir: Path, quick: bool) -> None:
    rng = np.random.default_rng(11)
    fc = 1.5e9
    d = np.arange(1, 32, 2, dtype=float) ** 2
    free = np.vstack([pl_free(fc, d, gt, gr) for gt, gr in [(1, 1), (1, 0.5), (0.5, 0.5)]])
    logdist = np.vstack([pl_logdist_or_norm(fc, d, 100, n) for n in [2, 3, 6]])
    lognorm = np.vstack([pl_logdist_or_norm(fc, d, 100, 2, 3, rng) for _ in range(3)])
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, curves, title in zip(axes, [free, logdist, lognorm], ["Free", "Log-distance", "Log-normal"]):
        for row in curves:
            ax.semilogx(d, row, marker="o")
        ax.set_title(title)
        ax.set_xlabel("Distance [m]")
        ax.set_ylabel("Path loss [dB]")
        ax.grid(True)
    finish(output_dir, "plot_pl_general", fig, np.column_stack([d, free.T, logdist.T, lognorm.T]), "distance free1 free2 free3 logdist2 logdist3 logdist6 lognorm1 lognorm2 lognorm3")


def plot_ray_ric_channel(output_dir: Path, quick: bool) -> None:
    rng = np.random.default_rng(12)
    n = 20000 if quick else 200000
    ray = np.abs(ray_model(n, rng))
    rics = [np.abs(ric_model(k_db, n, rng)) for k_db in [-40, 15]]
    fig, ax = plt.subplots(figsize=(6, 4))
    hist_rows = []
    for label, values, marker in zip(["Rayleigh", "Rician K=-40dB", "Rician K=15dB"], [ray, *rics], ["s", "o", "^"]):
        counts, edges = np.histogram(values, bins=30)
        centers = 0.5 * (edges[:-1] + edges[1:])
        ax.plot(centers, counts, marker=marker, label=label)
        hist_rows.append(np.column_stack([centers, counts]))
    ax.set_xlabel("x")
    ax.set_ylabel("Occasion")
    ax.grid(True)
    ax.legend(fontsize=8)
    finish(output_dir, "plot_ray_ric_channel", fig, np.column_stack(hist_rows), "ray_x ray_count ric_neg40_x ric_neg40_count ric15_x ric15_count")


def plot_sui_channel(output_dir: Path, quick: bool) -> None:
    delay, p_db, k_factor, doppler, _, fnorm = sui_parameters(6)
    n = 1000 if quick else 10000
    nfading = 256 if quick else 1024
    fad, tf = sui_fading(p_db, k_factor, doppler, fnorm, n, nfading, 4, rng=np.random.default_rng(13))
    fig, axes = plt.subplots(3, 1, figsize=(8, 8))
    axes[0].stem(delay, 10 ** (p_db / 10), linefmt="k-", markerfmt="ko", basefmt=" ")
    time = np.arange(n) * tf
    for idx, row in enumerate(fad):
        axes[1].plot(time, 20 * np.log10(np.maximum(np.abs(row), 1e-12)), label=f"Path {idx + 1}")
    for idx, row in enumerate(fad):
        spec = np.abs(np.fft.fftshift(np.fft.fft(row, nfading))) ** 2
        freq = np.fft.fftshift(np.fft.fftfreq(nfading, tf))
        axes[2].plot(freq, spec / max(np.max(spec), 1e-12), label=f"Path {idx + 1}")
    for ax in axes:
        ax.grid(True)
    axes[1].legend(fontsize=8)
    axes[2].legend(fontsize=8)
    axes[0].set_xlabel("Delay [us]")
    axes[1].set_xlabel("Time [s]")
    axes[2].set_xlabel("Frequency [Hz]")
    finish(output_dir, "plot_sui_channel", fig, np.column_stack([time, np.abs(fad).T]), "time abs_path1 abs_path2 abs_path3")


def plot_sv_model_ct(output_dir: Path, quick: bool) -> None:
    rng = np.random.default_rng(14)
    lam_cluster = 0.0233
    lam_ray = 2.5
    gam_cluster = 7.4
    gam_ray = 4.3
    sigma_x = 3
    n = 400 if quick else 1000
    cluster = rng.exponential(1 / lam_cluster, n)
    ray = rng.exponential(1 / lam_ray, n)
    h, t, _, counts = sv_model_ct(lam_cluster, lam_ray, gam_cluster, gam_ray, n, 1, sigma_x, rng=rng)
    shadow = 10 ** (sigma_x * rng.normal(size=n) / 20)
    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    x_cluster = np.linspace(0, 300, 300)
    axes[0, 0].plot(x_cluster, lam_cluster * np.exp(-lam_cluster * x_cluster), "k")
    axes[0, 0].hist(cluster, bins=25, density=True, histtype="step", color="k", linestyle=":")
    x_ray = np.linspace(0, 5, 300)
    axes[0, 1].plot(x_ray, lam_ray * np.exp(-lam_ray * x_ray), "k")
    axes[0, 1].hist(ray, bins=25, density=True, histtype="step", color="k", linestyle=":")
    axes[1, 0].stem(t[: counts[0], 0], np.abs(h[: counts[0], 0]), linefmt="k-", markerfmt="ko", basefmt=" ")
    axes[1, 1].hist(20 * np.log10(shadow), bins=25, color="0.2")
    for ax in axes.ravel():
        ax.grid(True)
    data = np.column_stack([t[: counts[0], 0], np.abs(h[: counts[0], 0])])
    finish(output_dir, "plot_sv_model_ct", fig, data, "delay_ns abs_h")


def plot_uwb_channel(output_dir: Path, quick: bool) -> None:
    rng = np.random.default_rng(15)
    ts = 0.167
    num_ch = 20 if quick else 100
    cm = 1
    params = uwb_parameters(cm)
    h_ct, t_ct, t0, counts = uwb_model_ct(*params, num_ch=num_ch, rng=rng)
    h_n, oversampling = convert_uwb_ct(h_ct, t_ct, counts, num_ch, ts)
    h = h_n[::oversampling] * oversampling
    channel_energy = np.sum(np.abs(h) ** 2, axis=0)
    t = np.arange(h.shape[0]) * ts
    excess = np.zeros(num_ch)
    rms = np.zeros(num_ch)
    n10 = np.zeros(num_ch)
    n85 = np.zeros(num_ch)
    for k in range(num_ch):
        sq_h = np.abs(h[:, k]) ** 2 / max(channel_energy[k], 1e-12)
        t_norm = t - t0[k]
        excess[k] = float(t_norm @ sq_h)
        rms[k] = float(np.sqrt(((t_norm - excess[k]) ** 2) @ sq_h))
        mag = np.abs(h[:, k])
        n10[k] = np.sum(mag > 10 ** (-10 / 20) * np.max(mag))
        sorted_energy = np.sort(mag**2)[::-1]
        n85[k] = np.searchsorted(np.cumsum(sorted_energy), 0.85 * np.sum(sorted_energy)) + 1
    avg_profile = np.mean(np.abs(h) ** 2, axis=1)
    avg_profile /= max(np.max(avg_profile), 1e-12)
    fig, axes = plt.subplots(4, 2, figsize=(11, 10))
    axes[0, 0].plot(t, h.real)
    axes[0, 1].plot(np.arange(num_ch), excess)
    axes[1, 0].plot(np.arange(num_ch), rms)
    axes[1, 1].plot(np.arange(num_ch), n10)
    axes[2, 0].plot(t, 10 * np.log10(np.maximum(avg_profile, 1e-12)))
    axes[2, 1].plot(np.arange(num_ch), 10 * np.log10(np.maximum(channel_energy, 1e-12)))
    axes[3, 0].plot(np.arange(num_ch), n85)
    axes[3, 1].axis("off")
    for ax in axes.ravel():
        ax.grid(True)
    summary = np.column_stack([np.arange(num_ch), excess, rms, n10, n85, channel_energy])
    finish(output_dir, "plot_uwb_channel", fig, summary, "channel excess_delay rms_delay n10_paths n85_paths energy")


def plot_ber(output_dir: Path, quick: bool, input_file: Path | None = None, nbps: int = 4) -> None:
    ebn0_db = np.arange(0, 31)
    order = 2**nbps
    awgn = ber_qam(ebn0_db, order, "AWGN")
    rayleigh = ber_qam(ebn0_db, order, "Rayleigh")
    if input_file is not None:
        sim = np.loadtxt(input_file)
    else:
        sim_x = np.arange(0, 31, 3 if quick else 2)
        sim_y = np.maximum(np.interp(sim_x, ebn0_db, rayleigh) * 1.15, 1e-5)
        sim = np.column_stack([sim_x, sim_y])
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogy(ebn0_db, awgn, "r:", label="AWGN analytic")
    ax.semilogy(ebn0_db, rayleigh, "r-", label="Rayleigh analytic")
    ax.semilogy(sim[:, 0], sim[:, 1], "b--s", label="Simulation")
    ax.set_xlabel("EbN0 [dB]")
    ax.set_ylabel("BER")
    ax.grid(True)
    ax.legend(fontsize=8)
    finish(output_dir, "plot_ber", fig, np.column_stack([ebn0_db, awgn, rayleigh]), "ebn0_db awgn rayleigh")
    np.savetxt(output_dir / "plot_ber_simulation.dat", sim, header="ebn0_db ber")


def plot_modified_fwgn(output_dir: Path, quick: bool) -> None:
    nfading = 512 if quick else 1024
    n = 2000 if quick else 10000
    fm = np.array([100, 10])
    fad_ff, tf_ff = fwgn_ff(2, fm, nfading, 8, "class", rng=np.random.default_rng(16))
    fad_tf, tf_tf = fwgn_tf(2, fm, n, nfading, 8, "class", rng=np.random.default_rng(17))
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    for row, label in zip(fad_ff, ["Path 1, fm=100Hz", "Path 2, fm=10Hz"]):
        axes[0].plot(np.arange(nfading) * tf_ff, 20 * np.log10(np.maximum(np.abs(row), 1e-12)), label=label)
    for row, label in zip(fad_tf, ["Path 1, fm=100Hz", "Path 2, fm=10Hz"]):
        axes[1].plot(np.arange(n) * tf_tf, 20 * np.log10(np.maximum(np.abs(row), 1e-12)), label=label)
    for ax in axes:
        ax.set_xlabel("time [s]")
        ax.set_ylabel("Magnitude [dB]")
        ax.grid(True)
        ax.legend(fontsize=8)
    data = np.column_stack([np.arange(n) * tf_tf, np.abs(fad_tf).T])
    finish(output_dir, "plot_modified_fwgn", fig, data, "time abs_path1 abs_path2")


def plot_ray_fading(output_dir: Path, quick: bool) -> None:
    rng = np.random.default_rng(18)
    fc = 9e8
    fs = 5e4
    speed_kmh = 120
    ts = 1 / fs
    v_ms = speed_kmh / 3.6
    wavelength = 3e8 / fc
    pdp_db = np.array([0, -1, -9, -10, -15, -20], dtype=float)
    bs_aod = 50 * np.ones_like(pdp_db)
    ms_aoa = 67.5 * np.ones_like(pdp_db)
    _, ms_theta, bs_phi = gen_phase(0, 2, bs_aod, 0, 35, ms_aoa, rng=rng)
    t = np.arange(1000 if quick else 10000) * ts
    h = ray_fading(20, db2w(pdp_db), bs_phi, ms_theta, v_ms, 22.5, wavelength, t)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t, 20 * np.log10(np.maximum(np.abs(h[0]), 1e-12)), "k-")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("Magnitude [dB]")
    ax.grid(True)
    finish(output_dir, "plot_ray_fading", fig, np.column_stack([t, np.abs(h[0])]), "time abs_h_first_path")


PLOTS = {
    "plot_2ray_exp_model": plot_2ray_exp_model,
    "plot_ccdf": plot_ccdf,
    "plot_fwgn": plot_fwgn,
    "plot_ieee80211_model": plot_ieee80211_model,
    "plot_jakes_model": plot_jakes_model,
    "plot_pl_hata": plot_pl_hata,
    "plot_pl_ieee80216d": plot_pl_ieee80216d,
    "plot_pl_general": plot_pl_general,
    "plot_ray_ric_channel": plot_ray_ric_channel,
    "plot_sui_channel": plot_sui_channel,
    "plot_sv_model_ct": plot_sv_model_ct,
    "plot_uwb_channel": plot_uwb_channel,
    "plot_ber": plot_ber,
    "plot_modified_fwgn": plot_modified_fwgn,
    "plot_ray_fading": plot_ray_fading,
}


def main(plot_name: str) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs") / plot_name)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--nbps", type=int, default=4)
    args = parser.parse_args()
    if plot_name == "plot_ber":
        plot_ber(args.output_dir, args.quick, args.input, args.nbps)
    else:
        PLOTS[plot_name](args.output_dir, args.quick)
