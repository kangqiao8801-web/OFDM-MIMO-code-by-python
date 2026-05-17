from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.mimo import exhaustive_ml_detector, lrad_mmse, mmse_detect, osic_detector, qrm_mld_detector, qrm_mld_soft
from ofdm_mimo.modulation import qam_demod, qam_mod


def run(quick: bool = False, seed: int = 12) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    snr = np.array([0, 8, 16, 24])
    trials = 60 if quick else 400
    table = qam_mod(np.arange(16), 16)
    errors = np.zeros((5, snr.size))
    for i, snr_db in enumerate(snr):
        sigma2 = 2 * 10 ** (-snr_db / 10)
        for _ in range(trials):
            idx = rng.integers(0, 16, size=2)
            x = table[idx]
            h = (rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))) / np.sqrt(2)
            y = h @ x + np.sqrt(sigma2 / 2) * (rng.normal(size=2) + 1j * rng.normal(size=2))
            detected = [
                mmse_detect(y, h, sigma2, table),
                osic_detector(y, h, sigma2, 2, 1, table),
                exhaustive_ml_detector(y, h, table),
                qrm_mld_detector(y, h, 8, table),
                lrad_mmse(h, y, sigma2),
            ]
            for row, est in enumerate(detected):
                errors[row, i] += np.count_nonzero(qam_demod(est, 16) != idx)
    ser = errors / (trials * 2)
    _ = qrm_mld_soft(np.ones(4), np.eye(4), 8)
    return snr, ser


def save(output_dir: Path, snr: np.ndarray, ser: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "mimo_detection_algorithms.dat", np.column_stack([snr, ser.T]), header="SNR_dB MMSE OSIC ML QRM LRAD")
    labels = ["MMSE", "OSIC", "ML", "QRM-MLD", "LRAD-MMSE"]
    plt.figure(figsize=(7, 4))
    for label, row in zip(labels, ser):
        plt.semilogy(snr, row, "o-", label=label)
    plt.xlabel("SNR [dB]")
    plt.ylabel("symbol error rate")
    plt.grid(True, which="both")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output_dir / "mimo_detection_algorithms.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/mimo_detection_algorithms"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
