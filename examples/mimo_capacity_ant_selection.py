from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.capacity import water_pouring
from ofdm_mimo.mimo import mimo_capacity_ant_selection_optimal, mimo_capacity_ant_selection_suboptimal


def run(quick: bool = False, seed: int = 14) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    snr_db = np.array([0, 5, 10, 15, 20])
    trials = 80 if quick else 600
    caps = np.zeros((4, snr_db.size))
    for i, db in enumerate(snr_db):
        snr = 10 ** (db / 10)
        for _ in range(trials):
            h = (rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))) / np.sqrt(2)
            caps[0, i] += mimo_capacity_ant_selection_optimal(h, 1, snr)[0]
            caps[1, i] += mimo_capacity_ant_selection_optimal(h, 2, snr)[0]
            caps[2, i] += mimo_capacity_ant_selection_suboptimal(h, 2, snr)[0]
            caps[3, i] += np.sum(water_pouring(np.linalg.svd(h, compute_uv=False) ** 2, snr, 4))
    return snr_db, caps / trials


def save(output_dir: Path, snr_db: np.ndarray, caps: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "mimo_capacity_ant_selection.dat", np.column_stack([snr_db, caps.T]), header="SNR_dB opt1 opt2 subopt2 water_power_sum")
    labels = ["optimal 1 ant", "optimal 2 ant", "suboptimal 2 ant", "water power sum"]
    plt.figure(figsize=(7, 4))
    for label, row in zip(labels, caps):
        plt.plot(snr_db, row, "o-", label=label)
    plt.xlabel("SNR [dB]")
    plt.ylabel("capacity / allocation metric")
    plt.grid(True)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output_dir / "mimo_capacity_ant_selection.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/mimo_capacity_ant_selection"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
