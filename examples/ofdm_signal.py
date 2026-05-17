from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.modulation import mapper


def run(quick: bool = False, seed: int = 2) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    n = 8
    nos = 16
    nnos = n * nos
    time = np.arange(nnos) / nnos
    x, _ = mapper(2, n, rng)
    x[0] = 0
    components = np.zeros((n, nnos), dtype=complex)
    for i in range(n):
        freq = np.zeros(nnos, dtype=complex)
        index = i if i < n // 2 else nnos - n + i
        freq[index] = x[i]
        components[i] = np.fft.ifft(freq, nnos)
    summed = np.sum(components, axis=0)

    nhist = 80 if quick else 1000
    hist_samples = []
    for _ in range(nhist):
        xh, _ = mapper(2, 16, rng)
        xh[0] = 0
        hist_samples.append(np.fft.ifft(xh, 16))
    hist_samples = np.concatenate(hist_samples)
    return time, components, summed, hist_samples


def save(output_dir: Path, time: np.ndarray, components: np.ndarray, summed: np.ndarray, hist_samples: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "ofdm_signal.dat", np.column_stack([time, summed.real, summed.imag, np.abs(summed)]), header="t real imag abs")
    fig, axes = plt.subplots(3, 1, figsize=(7, 6))
    axes[0].plot(time, components.real.T, "k:", linewidth=0.6)
    axes[0].plot(time, summed.real, "b", linewidth=1.5)
    axes[0].set_ylabel("x_I(t)")
    axes[1].plot(time, components.imag.T, "k:", linewidth=0.6)
    axes[1].plot(time, summed.imag, "b", linewidth=1.5)
    axes[1].set_ylabel("x_Q(t)")
    axes[2].plot(time, np.abs(summed), "b")
    axes[2].set_ylabel("|x(t)|")
    axes[2].set_xlabel("t")
    fig.tight_layout()
    fig.savefig(output_dir / "ofdm_signal.png", dpi=150)
    plt.close(fig)

    plt.figure(figsize=(6, 4))
    plt.hist(hist_samples.real, bins=30, density=True, alpha=0.7, label="I")
    plt.hist(hist_samples.imag, bins=30, density=True, alpha=0.7, label="Q")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "ofdm_signal_pdf.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/ofdm_signal"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
