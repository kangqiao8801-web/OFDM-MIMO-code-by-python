from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/ofdm_mimo_matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ofdm_mimo.channel_estimation import ls_ce, mmse_ce
from ofdm_mimo.modulation import qam_mod


def awgn_measured(rng: np.random.Generator, x: np.ndarray, snr_db: float) -> np.ndarray:
    sig_pow = np.mean(np.abs(x) ** 2)
    noise_pow = sig_pow / (10 ** (snr_db / 10))
    noise = np.sqrt(noise_pow / 2) * (rng.standard_normal(x.shape) + 1j * rng.standard_normal(x.shape))
    return x + noise


def run(output_dir: Path, quick: bool = False, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    nfft = 32
    ng = nfft // 8
    nofdm = nfft + ng
    nsym = 12 if quick else 100
    nps = 4
    npilot = nfft // nps
    ndata = nfft - npilot
    order = 16
    snr = 30
    pilot_loc = np.arange(0, nfft, nps)
    mse = np.zeros(6)
    first_snapshot = None

    for symbol_idx in range(nsym):
        xp = 2 * (rng.standard_normal(npilot) > 0) - 1
        msgint = rng.integers(0, order, size=ndata)
        data = qam_mod(msgint, order)
        x_freq = np.zeros(nfft, dtype=complex)
        data_idx = np.setdiff1d(np.arange(nfft), pilot_loc)
        x_freq[pilot_loc] = xp
        x_freq[data_idx] = data
        x_time = np.fft.ifft(x_freq, nfft)
        xt = np.concatenate([x_time[-ng:], x_time])
        h = np.array([
            rng.standard_normal() + 1j * rng.standard_normal(),
            (rng.standard_normal() + 1j * rng.standard_normal()) / 2,
        ])
        h_freq = np.fft.fft(h, nfft)
        y_channel = np.convolve(xt, h)
        yt = awgn_measured(rng, y_channel, snr)
        y = yt[ng:nofdm]
        y_freq = np.fft.fft(y)

        estimates = [
            ls_ce(y_freq, xp, pilot_loc, nfft, nps, "linear"),
            ls_ce(y_freq, xp, pilot_loc, nfft, nps, "spline"),
            mmse_ce(y_freq, xp, pilot_loc, nfft, nps, h, snr),
        ]
        for idx, h_est in enumerate(estimates):
            h_dft = np.fft.fft(np.fft.ifft(h_est)[: len(h)], nfft)
            mse[idx] += np.mean(np.abs(h_freq - h_est) ** 2)
            mse[idx + 3] += np.mean(np.abs(h_freq - h_dft) ** 2)
        if symbol_idx == 0:
            first_snapshot = (h_freq, estimates)

    mse = mse / nsym
    np.savetxt(
        output_dir / "mse.dat",
        mse[None, :],
        header="LS_linear LS_spline MMSE LS_linear_DFT LS_spline_DFT MMSE_DFT",
    )

    h_freq, estimates = first_snapshot
    labels = ["LS-linear", "LS-spline", "MMSE"]
    fig, axes = plt.subplots(3, 1, figsize=(7, 7), sharex=True)
    true_power = 10 * np.log10(np.maximum(np.abs(h_freq) ** 2, 1e-12))
    for ax, label, h_est in zip(axes, labels, estimates):
        est_power = 10 * np.log10(np.maximum(np.abs(h_est) ** 2, 1e-12))
        ax.plot(true_power, label="True Channel")
        ax.plot(est_power, ":+", label=label)
        ax.set_ylabel("Power [dB]")
        ax.grid(True)
        ax.legend(fontsize=8)
    axes[-1].set_xlabel("Subcarrier Index")
    fig.tight_layout()
    fig.savefig(output_dir / "channel_estimation.png", dpi=150)
    plt.close(fig)
    return mse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "channel_estimation")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    mse = run(args.output_dir, args.quick)
    print(f"Saved channel estimation results to {args.output_dir}")
    print("MSE:", mse)


if __name__ == "__main__":
    main()
