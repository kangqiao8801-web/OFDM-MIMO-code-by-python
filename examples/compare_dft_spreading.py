from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from _papr_common import save_dat
from ofdm_mimo.ofdm import ccdf_papr_dft_spreading


def run(quick: bool = False, seed: int = 5489) -> tuple[np.ndarray, list[int], np.ndarray]:
    nblk = 80 if quick else 5000
    n = 256
    nd = 64
    bits = [2, 4, 6]
    dbs = np.arange(0, 12.01, 0.5 if quick else 0.2)
    curves = np.zeros((len(bits), 3, dbs.size))
    for i, b in enumerate(bits):
        for j, mode in enumerate(["OF", "LF", "IF"]):
            ndb = n if mode == "OF" else nd
            curves[i, j], _ = ccdf_papr_dft_spreading(mode, ndb, b, n, dbs, nblk, rng=np.random.default_rng(seed))
    return dbs, bits, curves


def save(output_dir: Path, dbs: np.ndarray, bits: list[int], curves: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    save_dat(output_dir / "compare_dft_spreading.dat", [dbs, *curves.reshape(-1, dbs.size)], "PAPR_dB curves")
    fig, axes = plt.subplots(1, len(bits), figsize=(11, 3.5), sharey=True)
    for ax, b, rows in zip(axes, bits, curves):
        for label, row in zip(["OFDMA", "LFDMA", "IFDMA"], rows):
            ax.semilogy(dbs, row, marker="o", markersize=3, label=label)
        ax.set_title(f"{2**b}-QAM")
        ax.set_xlabel("PAPR0 [dB]")
        ax.grid(True, which="both")
    axes[0].set_ylabel("Pr(PAPR>PAPR0)")
    axes[-1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "compare_dft_spreading.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/compare_dft_spreading"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
