from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.mimo import block_diagonalization_precoders, codebook_generator, dirty_or_th_precoding, multi_user_precoder


def run(quick: bool = False, seed: int = 13) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    trials = 50 if quick else 300
    metrics = np.zeros((trials, 5))
    cb = codebook_generator()
    x = np.ones((4, 4), dtype=complex)
    for i in range(trials):
        h1 = (rng.normal(size=(2, 4)) + 1j * rng.normal(size=(2, 4))) / np.sqrt(2)
        h2 = (rng.normal(size=(2, 4)) + 1j * rng.normal(size=(2, 4))) / np.sqrt(2)
        w1, w2 = block_diagonalization_precoders(h1, h2)
        metrics[i, 0] = np.linalg.norm(h2 @ w1) + np.linalg.norm(h1 @ w2)
        h_used = (rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))) / np.sqrt(2)
        dirty, _ = dirty_or_th_precoding(h_used, x, "dirty")
        th, _ = dirty_or_th_precoding(h_used, x, "th")
        metrics[i, 1] = np.mean(np.abs(dirty) ** 2)
        metrics[i, 2] = np.mean(np.abs(th) ** 2)
        w, beta, _ = multi_user_precoder((rng.normal(size=(10, 4)) + 1j * rng.normal(size=(10, 4))) / np.sqrt(2), 4, 0.1)
        metrics[i, 3] = beta
        metrics[i, 4] = np.max([np.linalg.norm(h1 @ cb[:, :, k]) for k in range(cb.shape[2])])
    return np.arange(trials), metrics


def save(output_dir: Path, idx: np.ndarray, metrics: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "mimo_precoding_algorithms.dat", np.column_stack([idx, metrics]), header="trial bd_leak dirty_power th_power multiuser_beta best_codebook_gain")
    plt.figure(figsize=(7, 4))
    plt.plot(idx, metrics[:, 0], label="BD leakage")
    plt.plot(idx, metrics[:, 1], label="Dirty power")
    plt.plot(idx, metrics[:, 2], label="TH power")
    plt.plot(idx, metrics[:, 3], label="MU beta")
    plt.xlabel("trial")
    plt.ylabel("metric")
    plt.grid(True)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output_dir / "mimo_precoding_algorithms.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/mimo_precoding_algorithms"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
