from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from _papr_common import save_dat
from ofdm_mimo.ofdm import ccdf_ofdma, ccdf_pts


def run(quick: bool = False, seed: int = 5489) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    nblk = 80 if quick else 3000
    n = 256
    nos = 4
    b = 4
    dbs = np.arange(4, 11.01, 0.5 if quick else 0.1)
    nsbs = np.array([1, 2, 4, 8, 16])
    curves = [ccdf_ofdma(n, nos, b, dbs, nblk, rng)]
    for nsb in nsbs:
        curves.append(ccdf_pts(n, nos, int(nsb), b, dbs, nblk, rng))
    return dbs, nsbs, np.vstack(curves)


def save(output_dir: Path, dbs: np.ndarray, nsbs: np.ndarray, ccdf: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    save_dat(output_dir / "compare_ccdf_pts.dat", [dbs, *ccdf], "PAPR_dB OFDMA PTS_Nsb_1 PTS_Nsb_2 PTS_Nsb_4 PTS_Nsb_8 PTS_Nsb_16")
    plt.figure(figsize=(7, 4.5))
    plt.semilogy(dbs, ccdf[0], "k", label="OFDMA")
    for nsb, row in zip(nsbs, ccdf[1:]):
        plt.semilogy(dbs, row, marker="o", markersize=3, label=f"Nsb={nsb}")
    plt.xlabel("PAPR0 [dB]")
    plt.ylabel("Pr(PAPR>PAPR0)")
    plt.ylim(1e-3, 1)
    plt.grid(True, which="both")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output_dir / "compare_ccdf_pts.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/compare_ccdf_pts"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
