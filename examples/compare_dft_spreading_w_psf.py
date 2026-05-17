from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from _papr_common import save_dat
from ofdm_mimo.ofdm import ccdf_papr_dft_spreading, raised_cosine_filter


def run(quick: bool = False, seed: int = 5489) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = 256
    nd = 64
    nblk = 50 if quick else 5000
    rhos = np.arange(0, 1.01, 0.5 if quick else 0.2)
    dbs = np.arange(0, 10.01, 0.5 if quick else 0.2)
    first = np.zeros((2, rhos.size + 1, dbs.size))
    for mode_idx, mode in enumerate(["IF", "LF"]):
        first[mode_idx, 0], _ = ccdf_papr_dft_spreading(mode, nd, 2, n, dbs, nblk, rng=np.random.default_rng(seed))
        for rho_idx, rho in enumerate(rhos, start=1):
            psf = raised_cosine_filter(float(rho), 6, 8)
            first[mode_idx, rho_idx], _ = ccdf_papr_dft_spreading(mode, nd, 2, n, dbs, nblk, psf=psf, nos=8, rng=np.random.default_rng(seed))

    nds = np.array([4, 8, 32, 64, 128])
    psf = raised_cosine_filter(0.4, 6, 2)
    second = np.zeros((nds.size, dbs.size))
    for i, ndb in enumerate(nds):
        second[i], _ = ccdf_papr_dft_spreading("LF", int(ndb), 6, n, dbs, nblk, psf=psf, nos=2, rng=np.random.default_rng(seed))
    return dbs, rhos, first, second


def save(output_dir: Path, dbs: np.ndarray, rhos: np.ndarray, first: np.ndarray, second: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    save_dat(output_dir / "compare_dft_spreading_w_psf.dat", [dbs, *first.reshape(-1, dbs.size), *second], "PAPR_dB curves")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for mode_idx, mode in enumerate(["IFDMA", "LFDMA"]):
        axes[0].semilogy(dbs, first[mode_idx, 0], label=f"{mode} no PSF")
        for rho, row in zip(rhos, first[mode_idx, 1:]):
            axes[0].semilogy(dbs, row, linestyle="-" if mode_idx == 0 else ":", label=f"{mode} a={rho:.1f}")
    for ndb, row in zip([4, 8, 32, 64, 128], second):
        axes[1].semilogy(dbs, row, marker="o", markersize=3, label=f"Nd={ndb}")
    for ax in axes:
        ax.set_xlabel("PAPR0 [dB]")
        ax.grid(True, which="both")
        ax.legend(fontsize=6)
    axes[0].set_ylabel("Pr(PAPR>PAPR0)")
    axes[0].set_title("roll-off")
    axes[1].set_title("localized block size")
    fig.tight_layout()
    fig.savefig(output_dir / "compare_dft_spreading_w_psf.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/compare_dft_spreading_w_psf"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
