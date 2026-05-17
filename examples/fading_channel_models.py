from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.channel_models import channel1, channel_coeff, ray_fading, ray_model, ric_model


def run(quick: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = 512 if quick else 2000
    ray = ray_model(n, rng=np.random.default_rng(7))
    ric = ric_model(6, n, rng=np.random.default_rng(8))
    hh = channel_coeff(2, 2, 64, [1, 0.7], [1, 0.3], "complex", rng=np.random.default_rng(9))
    sig = np.ones((16, 2, 8), dtype=complex)
    corr, _ = channel1(sig, 20, 2, rng=np.random.default_rng(10))
    pdp = np.array([0.8, 0.2])
    phases = np.zeros((2, 4))
    angles = np.tile(np.array([0, 90, 180, 270]), (2, 1))
    t = np.linspace(0, 1e-3, 64)
    ray_paths = ray_fading(4, pdp, phases, angles, 10.0, 0.0, 0.15, t)
    summary = np.array([[np.mean(np.abs(ray) ** 2), np.mean(np.abs(ric) ** 2), np.mean(np.abs(hh) ** 2), np.mean(np.abs(corr) ** 2)]])
    return np.abs(ray), np.abs(ric), np.abs(ray_paths), summary


def save(output_dir: Path, ray_abs: np.ndarray, ric_abs: np.ndarray, ray_paths_abs: np.ndarray, summary: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "fading_channel_models.dat", summary, header="ray_power ric_power correlated_mimo_power channel1_rx_power")
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    axes[0].hist(ray_abs, bins=40, density=True, alpha=0.6, label="Rayleigh")
    axes[0].hist(ric_abs, bins=40, density=True, alpha=0.6, label="Rician K=6dB")
    for idx, row in enumerate(ray_paths_abs):
        axes[1].plot(row, label=f"path {idx}")
    axes[0].set_xlabel("envelope")
    axes[0].set_ylabel("PDF")
    axes[1].set_xlabel("sample")
    axes[1].set_ylabel("|h|")
    for ax in axes:
        ax.grid(True)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "fading_channel_models.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/fading_channel_models"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
