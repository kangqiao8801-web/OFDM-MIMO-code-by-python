from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from _papr_common import save_dat
from ofdm_mimo.modulation import mapper


def _quantize_saturate(x: np.ndarray, total_word_length: int, fractional_word_length: int) -> np.ndarray:
    step = 2.0 ** -fractional_word_length
    upper = 2.0 ** (total_word_length - fractional_word_length - 1) - step
    lower = -2.0 ** (total_word_length - fractional_word_length - 1)
    real = np.clip(np.round(x.real / step) * step, lower, upper)
    imag = np.clip(np.round(x.imag / step) * step, lower, upper)
    return real + 1j * imag


def run(quick: bool = False, seed: int = 7) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    n = 64
    b = 6
    max_iter = 80 if quick else 1000
    twls = np.array([6, 7, 8, 9])
    iwl = 1
    mus = np.arange(2, 8.01, 0.4 if quick else 0.2)
    sigma = 1 / np.sqrt(n)
    sqnr = np.zeros((twls.size, mus.size))
    for i, twl in enumerate(twls):
        fwl = int(twl - iwl)
        for j, mu0 in enumerate(mus):
            mu = mu0 / np.sqrt(2)
            tx = 0.0
            te = 0.0
            for _ in range(max_iter):
                x_freq, _ = mapper(b, n, rng)
                x = np.fft.ifft(x_freq, n) / sigma / mu
                xq = _quantize_saturate(x, int(twl), fwl)
                err = x - xq
                tx += np.vdot(x, x).real
                te += np.vdot(err, err).real
            sqnr[i, j] = 10 * np.log10(tx / te)
    return mus, twls, sqnr


def save(output_dir: Path, mus: np.ndarray, twls: np.ndarray, sqnr: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    save_dat(output_dir / "sqnr_with_quantization_clipping.dat", [mus, *sqnr], "mu SQNR_by_TWL")
    plt.figure(figsize=(7, 4))
    for twl, row in zip(twls, sqnr):
        best = int(np.argmax(row))
        plt.plot(mus, row, marker="o", markersize=3, label=f"{twl} bit")
        plt.plot(mus[best], row[best], "ro", markersize=4)
    plt.xlabel("mu")
    plt.ylabel("SQNR [dB]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "sqnr_with_quantization_clipping.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/sqnr_with_quantization_clipping"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
