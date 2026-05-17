from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import firwin, lfilter

from ofdm_mimo.modulation import mapper
from ofdm_mimo.ofdm import add_cp, clipping, ifft_oversampling


def run(seed: int = 4) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    cr = 1.2
    n = 128
    ncp = 32
    oversampling = 8
    x, _ = mapper(2, n, rng=rng)
    x[0] = 0
    base = add_cp(ifft_oversampling(x, n, oversampling), ncp * oversampling)
    padded = np.r_[np.zeros((n // 2 - ncp) * oversampling), base, np.zeros(n * oversampling // 2)]
    passband = np.sqrt(2) * np.real(padded * np.exp(1j * 4 * np.pi * np.arange(padded.size) / oversampling))
    clipped = clipping(passband, cr)
    filt = firwin(105, [1.5 / 4, 2.5 / 4], pass_zero=False)
    filtered = lfilter(filt, [1.0], clipped)
    return passband, clipped, filtered, filt


def save(output_dir: Path, passband: np.ndarray, clipped: np.ndarray, filtered: np.ndarray, filt: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "pdf.dat", np.column_stack([passband, clipped, filtered]), header="passband clipped filtered")
    fig, axes = plt.subplots(2, 2, figsize=(8, 6))
    axes[0, 0].hist(passband, bins=50, density=True)
    axes[0, 0].set_title("Unclipped")
    axes[0, 1].hist(clipped, bins=50, density=True)
    axes[0, 1].set_title("Clipped")
    axes[1, 0].hist(filtered, bins=50, density=True)
    axes[1, 0].set_title("Clipped + filtered")
    axes[1, 1].stem(filt)
    axes[1, 1].set_title("BPF coefficients")
    fig.tight_layout()
    fig.savefig(output_dir / "pdf_clipped_filtered.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/pdf_clipped_filtered_ofdm_signal"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run())


if __name__ == "__main__":
    main()
