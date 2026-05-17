from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.channel_models import pl_free, pl_hata, pl_ieee80216d, pl_logdist_or_norm


def run() -> tuple[np.ndarray, np.ndarray]:
    d = np.linspace(100, 5000, 120)
    fc = 2e9
    curves = np.vstack(
        [
            pl_free(fc, d),
            pl_logdist_or_norm(fc, d, 100, 3.0),
            pl_hata(900e6, d, 30, 1.5, "urban"),
            pl_hata(900e6, d, 30, 1.5, "suburban"),
            pl_ieee80216d(2.5e9, d, "A"),
            pl_ieee80216d(2.5e9, d, "C", corr_fact="ATNT"),
        ]
    )
    return d, curves


def save(output_dir: Path, d: np.ndarray, curves: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "path_loss_models.dat", np.column_stack([d, curves.T]), header="distance_m free logdist hata_urban hata_suburban ieee80216d_A ieee80216d_C")
    labels = ["Free", "Log-distance", "Hata urban", "Hata suburban", "802.16d A", "802.16d C"]
    plt.figure(figsize=(7, 4.5))
    for label, row in zip(labels, curves):
        plt.plot(d, row, label=label)
    plt.xlabel("distance [m]")
    plt.ylabel("path loss [dB]")
    plt.grid(True)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output_dir / "path_loss_models.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/path_loss_models"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run())


if __name__ == "__main__":
    main()
