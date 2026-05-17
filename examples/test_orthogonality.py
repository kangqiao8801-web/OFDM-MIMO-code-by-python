from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np


def run() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    total_time = 1.6
    nd = 1000
    ts = 0.002
    tt = np.arange(nd + 1) * ts
    sample_period = 0.1
    step = round(sample_period / ts)
    indices = np.arange(0, nd + 1, step)
    ks = np.array([1, 2, 3, 4, 3.9, 4.0])
    delays = np.array([0, 0, 0.1, 0.1, 0, 0.15])
    x = np.exp(1j * 2 * np.pi * ks[:, None] * (tt[None, :] - delays[:, None]) / total_time)
    x[-1] = np.r_[x[-1, 301:], x[2, :301]]
    n = round(total_time / sample_period)
    xn = x[:, indices[:n]]
    gram = xn @ xn.conj().T / n
    spectrum = np.fft.fft(xn, axis=1)
    return tt, x, gram, spectrum


def save(output_dir: Path, tt: np.ndarray, x: np.ndarray, gram: np.ndarray, spectrum: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "orthogonality.dat", np.abs(gram), header="abs(xn*xnH/N)")
    fig, axes = plt.subplots(2, 1, figsize=(7, 5))
    axes[0].plot(tt, x[0].real, label="k=1")
    axes[0].plot(tt, x[3].real, label="k=4")
    axes[0].set_xlabel("t")
    axes[0].set_ylabel("Re{x(t)}")
    axes[0].legend()
    axes[0].grid(True)
    axes[1].stem(np.arange(spectrum.shape[1]), np.abs(spectrum[0]))
    axes[1].set_xlabel("DFT bin")
    axes[1].set_ylabel("|X[k]|")
    axes[1].grid(True)
    fig.tight_layout()
    fig.savefig(output_dir / "orthogonality.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/test_orthogonality"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run())


if __name__ == "__main__":
    main()
