from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.capacity import mimo_capacity


def run(quick: bool = False, seed: int = 1) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    snr = 10.0
    n_iter = 500 if quick else 50000
    rates = []
    cdfs = []
    for nt, nr in [(2, 2), (4, 4)]:
        values = np.empty(n_iter)
        for idx in range(n_iter):
            h = np.sqrt(0.5) * (rng.standard_normal((nr, nt)) + 1j * rng.standard_normal((nr, nt)))
            values[idx] = mimo_capacity(h, snr, nt)
        hist, bins = np.histogram(values, 50)
        centers = (bins[:-1] + bins[1:]) / 2
        rates.append(centers)
        cdfs.append(np.cumsum(hist) / n_iter)
    return rates[0], np.asarray(cdfs), np.asarray(rates)


def save(output_dir: Path, base_rate: np.ndarray, cdfs: np.ndarray, rates: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "capacity_cdf.dat", np.column_stack([rates[0], cdfs[0], rates[1], cdfs[1]]), header="Rate22 CDF22 Rate44 CDF44")
    plt.plot(rates[0], cdfs[0], ":", label="2x2")
    plt.plot(rates[1], cdfs[1], "-", label="4x4")
    plt.xlabel("Rate [bps/Hz]")
    plt.ylabel("CDF")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "capacity_cdf.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/ergodic_capacity_cdf"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
