from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.capacity import mimo_capacity


def run(quick: bool = False, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    snr_db = np.arange(0, 21, 5)
    cases = [(4, 4), (2, 2), (1, 1), (1, 2), (2, 1)]
    n_iter = 80 if quick else 1000
    capacity = np.zeros((len(cases), snr_db.size))
    for case_idx, (nt, nr) in enumerate(cases):
        for _ in range(n_iter):
            h = np.sqrt(0.5) * (rng.standard_normal((nr, nt)) + 1j * rng.standard_normal((nr, nt)))
            for idx, snr in enumerate(10 ** (snr_db / 10)):
                capacity[case_idx, idx] += mimo_capacity(h, snr, nt)
    return snr_db, capacity / n_iter


def save(output_dir: Path, snr_db: np.ndarray, capacity: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "capacity.dat", np.column_stack([snr_db, capacity.T]), header="SNRdB C44 C22 C11 C12 C21")
    labels = ["4x4", "2x2", "1x1", "1x2", "2x1"]
    for row, label in zip(capacity, labels):
        plt.plot(snr_db, row, marker="o", label=label)
    plt.xlabel("SNR [dB]")
    plt.ylabel("bps/Hz")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "capacity.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/ergodic_capacity_vs_snr"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
