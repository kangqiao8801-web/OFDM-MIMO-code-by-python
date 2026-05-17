from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import sqrtm

from ofdm_mimo.capacity import water_pouring


def run(quick: bool = False, seed: int = 3) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    snr_db = np.arange(0, 21, 5)
    snr_linear = 10 ** (snr_db / 10)
    n_iter = 80 if quick else 1000
    nt = nr = 4
    rho = 0.2
    corr = np.array([[rho ** abs(i - j) for j in range(4)] for i in range(4)], dtype=float)
    rtx = sqrtm(corr)
    rrx = sqrtm(corr)
    ol = np.zeros_like(snr_linear)
    cl = np.zeros_like(snr_linear)
    for _ in range(n_iter):
        hw = np.sqrt(0.5) * (rng.standard_normal((nr, nt)) + 1j * rng.standard_normal((nr, nt)))
        h = rrx @ hw @ rtx
        gram = h.conj().T @ h
        singular = np.linalg.svd(gram, compute_uv=False)
        for idx, snr in enumerate(snr_linear):
            ol[idx] += np.real(np.log2(np.linalg.det(np.eye(4) + snr * gram / nt)))
            gamma = water_pouring(singular, snr, nt)
            cl[idx] += np.real(np.sum(np.log2(1 + snr / nt * gamma * singular)))
    return snr_db, ol / n_iter, cl / n_iter


def save(output_dir: Path, snr_db: np.ndarray, ol: np.ndarray, cl: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "ol_cl.dat", np.column_stack([snr_db, ol, cl]), header="SNRdB open_loop closed_loop")
    plt.plot(snr_db, ol, "o-", label="Channel Unknown")
    plt.plot(snr_db, cl, "<-", label="Channel Known")
    plt.xlabel("SNR [dB]")
    plt.ylabel("bps/Hz")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "ol_cl.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/ol_cl_comparison"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
