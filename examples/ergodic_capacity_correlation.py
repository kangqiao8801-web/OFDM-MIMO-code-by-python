from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import sqrtm

from ofdm_mimo.capacity import mimo_capacity


def run(quick: bool = False, seed: int = 2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    snr_db = np.arange(0, 21, 5)
    snr_linear = 10 ** (snr_db / 10)
    n_iter = 80 if quick else 1000
    nt = nr = 4
    r = np.array(
        [
            [1, 0.76 * np.exp(0.17j * np.pi), 0.43 * np.exp(0.35j * np.pi), 0.25 * np.exp(0.53j * np.pi)],
            [0.76 * np.exp(-0.17j * np.pi), 1, 0.76 * np.exp(0.17j * np.pi), 0.43 * np.exp(0.35j * np.pi)],
            [0.43 * np.exp(-0.35j * np.pi), 0.76 * np.exp(-0.17j * np.pi), 1, 0.76 * np.exp(0.17j * np.pi)],
            [0.25 * np.exp(-0.53j * np.pi), 0.43 * np.exp(-0.35j * np.pi), 0.76 * np.exp(-0.17j * np.pi), 1],
        ]
    )
    r_sqrt = sqrtm(r)
    iid = np.zeros_like(snr_linear)
    corr = np.zeros_like(snr_linear)
    for _ in range(n_iter):
        h_iid = np.sqrt(0.5) * (rng.standard_normal((nr, nt)) + 1j * rng.standard_normal((nr, nt)))
        h_corr = h_iid @ r_sqrt
        for idx, snr in enumerate(snr_linear):
            iid[idx] += mimo_capacity(h_iid, snr, nt)
            corr[idx] += mimo_capacity(h_corr, snr, nt)
    return snr_db, iid / n_iter, corr / n_iter


def save(output_dir: Path, snr_db: np.ndarray, iid: np.ndarray, corr: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "capacity_correlation.dat", np.column_stack([snr_db, iid, corr]), header="SNRdB iid corr")
    plt.plot(snr_db, iid, label="iid 4x4")
    plt.plot(snr_db, corr, ":", label="correlated 4x4")
    plt.xlabel("SNR [dB]")
    plt.ylabel("bps/Hz")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "capacity_correlation.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/ergodic_capacity_correlation"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
