from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.modulation import qam_mod
from ofdm_mimo.ofdm import add_cfo, add_cp, cfo_cp, sto_by_correlation


def run(seed: int = 6) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    nfft = 64
    ng = 16
    cfo = 0.023
    null = np.zeros(nfft + ng, dtype=complex)
    short = np.tile(np.exp(1j * 2 * np.pi * np.arange(ng) / ng), 4)
    long_freq = np.ones(nfft, dtype=complex)
    long = np.r_[np.fft.ifft(long_freq), np.fft.ifft(long_freq)]
    data = []
    for _ in range(2):
        freq = qam_mod(rng.integers(0, 4, size=nfft), 4)
        data.append(add_cp(np.fft.ifft(freq), ng))
    frame = np.r_[rng.normal(scale=0.05, size=80), null, short, long, *data]
    rx = add_cfo(frame, cfo, nfft) + 0.01 * (rng.standard_normal(frame.size) + 1j * rng.standard_normal(frame.size))
    power = np.convolve(np.abs(rx) ** 2, np.ones(nfft + ng), mode="same")
    ratio = power / np.maximum(np.r_[np.ones(nfft + ng), power[: -(nfft + ng)]], 1e-12)
    start = int(np.argmax(ratio))
    cfo_est = cfo_cp(rx[start + len(short) : start + len(short) + nfft + ng], nfft, ng)
    _, metric = sto_by_correlation(np.r_[np.zeros(nfft), rx[start:]], nfft, ng, (nfft + ng) // 2)
    return np.arange(rx.size), np.column_stack([np.abs(rx), ratio]), np.array([cfo, cfo_est, start, len(rng.normal(scale=0.05, size=80)) + len(null)])


def save(output_dir: Path, n: np.ndarray, traces: np.ndarray, summary: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "sto_cfo_summary.dat", summary[None, :], header="CFO CFO_est frame_start_est frame_start_true")
    np.savetxt(output_dir / "sto_cfo_trace.dat", np.column_stack([n, traces]), header="n abs_rx energy_ratio")
    fig, axes = plt.subplots(2, 1, figsize=(7, 5))
    axes[0].plot(n, traces[:, 0])
    axes[0].set_ylabel("|rx|")
    axes[1].plot(n, traces[:, 1])
    axes[1].set_ylabel("Energy ratio")
    axes[1].set_xlabel("sample")
    fig.tight_layout()
    fig.savefig(output_dir / "sto_cfo.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/do_sto_cfo1"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run())


if __name__ == "__main__":
    main()
