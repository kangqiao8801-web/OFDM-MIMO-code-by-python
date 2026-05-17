from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from _papr_common import save_dat
from ofdm_mimo.ofdm import ifft_oversampling, papr


def run() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = 16
    i = np.arange(n)
    x_freq = np.exp(1j * 3 * np.pi / n * i * i)
    x = ifft_oversampling(x_freq, n, 1)
    x_os = ifft_oversampling(x_freq, n, 4)
    return np.arange(n) / n, x, np.arange(4 * n) / (4 * n), x_os


def save(output_dir: Path, time: np.ndarray, x: np.ndarray, time_os: np.ndarray, x_os: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    save_dat(output_dir / "papr_of_chu.dat", [np.array([papr(x)[0]]), np.array([papr(x_os)[0]])], "PAPR_dB PAPR_oversampled_dB")
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
    axes[0].plot(x.real, x.imag, "o", label="L=1")
    axes[0].plot(x_os.real, x_os.imag, "k*", label="L=4")
    circle = 0.25 * np.exp(1j * np.deg2rad(np.arange(360)))
    axes[0].plot(circle.real, circle.imag, "k:", linewidth=0.8)
    axes[0].axis("equal")
    axes[0].grid(True)
    axes[0].legend()
    axes[1].plot(time, np.abs(x), "o", label="L=1")
    axes[1].plot(time_os, np.abs(x_os), "k:*", label="L=4")
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("|x(t)|")
    axes[1].grid(True)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(output_dir / "papr_of_chu.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/papr_of_chu"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run())


if __name__ == "__main__":
    main()
