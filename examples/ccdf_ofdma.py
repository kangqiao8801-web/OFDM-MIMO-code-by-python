from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.ofdm import ccdf_ofdma


def run(quick: bool = False, seed: int = 3) -> tuple[np.ndarray, np.ndarray]:
    dbs = np.arange(0, 12, 0.5)
    ccdf = ccdf_ofdma(64 if quick else 256, 4, 2, dbs, 50 if quick else 1000, rng=np.random.default_rng(seed))
    return dbs, ccdf


def save(output_dir: Path, dbs: np.ndarray, ccdf: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "ccdf.dat", np.column_stack([dbs, ccdf]), header="PAPR_dB CCDF")
    plt.semilogy(dbs, ccdf, "o-")
    plt.xlabel("PAPR0 [dB]")
    plt.ylabel("Pr(PAPR > PAPR0)")
    plt.grid(True, which="both")
    plt.tight_layout()
    plt.savefig(output_dir / "ccdf.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/ccdf_ofdma"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
