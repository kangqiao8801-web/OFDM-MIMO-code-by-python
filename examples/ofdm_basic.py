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

from ofdm_mimo.metrics import bit_error_rate
from ofdm_mimo.modulation import qam_demod, qam_mod
from ofdm_mimo.ofdm import guard_interval, remove_gi


def run(output_dir: Path, quick: bool = False, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    ng_type = 1
    ch = 0
    nbps = 4
    order = 2**nbps
    nfft = 64
    ng = nfft // 4
    nsym = nfft + ng
    nvc = nfft // 4
    nused = nfft - nvc
    ebn0 = np.array([0, 10, 20] if quick else [0, 5, 10, 15, 20])
    n_iter = 60 if quick else 600
    nframe = 3
    target_errors = 50 if quick else 200
    results = []

    sig_pow = 0.0
    for _ in range(n_iter):
        x_int = rng.integers(0, order, size=nused * nframe)
        x_mod = qam_mod(x_int, order)
        x_gi = _ofdm_transmit_frames(x_mod, nframe, nused, nfft, nvc, ng, nsym, ng_type)
        sig_pow += np.vdot(x_gi[: nframe * nsym], x_gi[: nframe * nsym]).real
    sig_pow = sig_pow / nsym / nframe / n_iter

    for snr_bit in ebn0:
        errors = 0
        total = 0
        for _ in range(n_iter):
            x_int = rng.integers(0, order, size=nused * nframe)
            x_mod = qam_mod(x_int, order)
            x_gi = _ofdm_transmit_frames(x_mod, nframe, nused, nfft, nvc, ng, nsym, ng_type)
            snr = snr_bit + 10 * np.log10(nbps * (nused / nfft))
            noise_mag = np.sqrt((10 ** (-snr / 10)) * sig_pow / 2)
            y_gi = x_gi + noise_mag * (rng.standard_normal(x_gi.shape) + 1j * rng.standard_normal(x_gi.shape))
            x_mod_r = _ofdm_receive_frames(y_gi, nframe, nused, nfft, nvc, ng, nsym, ng_type)
            x_r = qam_demod(x_mod_r, order)
            _, neb, ntb = bit_error_rate(x_r, x_int, nbps)
            errors += neb
            total += ntb
            if errors > target_errors:
                break
        results.append((snr_bit, errors / total))

    results_arr = np.asarray(results)
    result_file = output_dir / "OFDM_BER_AWGN_CP_GL16.dat"
    with result_file.open("w", encoding="utf-8") as f:
        f.write(f"%Signal power= {sig_pow:11.3e}\n%EbN0[dB]       BER\n")
        for snr_bit, ber in results_arr:
            f.write(f"{int(snr_bit)}\t{ber:11.3e}\n")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.semilogy(results_arr[:, 0], results_arr[:, 1], marker="o")
    ax.set_xlabel("EbN0 [dB]")
    ax.set_ylabel("BER")
    ax.set_ylim(1e-5, 1)
    ax.grid(True, which="both")
    fig.tight_layout()
    fig.savefig(output_dir / "ber.png", dpi=150)
    plt.close(fig)
    return results_arr


def _ofdm_transmit_frames(
    x_mod: np.ndarray,
    nframe: int,
    nused: int,
    nfft: int,
    nvc: int,
    ng: int,
    nsym: int,
    ng_type: int,
) -> np.ndarray:
    x_gi = np.zeros(nframe * nsym, dtype=complex)
    half = nused // 2
    for frame_idx in range(nframe):
        symbols = x_mod[frame_idx * nused : (frame_idx + 1) * nused]
        x_shift = np.concatenate([symbols[half:], np.zeros(nvc, dtype=complex), symbols[:half]])
        x_time = np.fft.ifft(x_shift)
        x_gi[frame_idx * nsym : (frame_idx + 1) * nsym] = guard_interval(ng, nfft, ng_type, x_time)
    return x_gi


def _ofdm_receive_frames(
    y_gi: np.ndarray,
    nframe: int,
    nused: int,
    nfft: int,
    nvc: int,
    ng: int,
    nsym: int,
    ng_type: int,
) -> np.ndarray:
    x_mod_r = np.zeros(nframe * nused, dtype=complex)
    half = nused // 2
    for frame_idx in range(nframe):
        frame = y_gi[frame_idx * nsym : (frame_idx + 1) * nsym]
        y = np.fft.fft(remove_gi(ng, nsym, ng_type, frame))
        y_shift = np.concatenate([y[half + nvc :], y[:half]])
        x_mod_r[frame_idx * nused : (frame_idx + 1) * nused] = y_shift
    return x_mod_r


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "ofdm_basic")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, args.quick)
    print(f"Saved OFDM BER results to {args.output_dir}")
    print(result)


if __name__ == "__main__":
    main()
