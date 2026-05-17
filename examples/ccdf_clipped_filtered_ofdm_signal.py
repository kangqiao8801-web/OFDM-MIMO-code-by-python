from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import firwin, lfilter

from ofdm_mimo.modulation import mapper
from ofdm_mimo.ofdm import clipping, ifft_oversampling


def _papr(x: np.ndarray) -> float:
    p = np.abs(x) ** 2
    return float(np.max(p) / np.mean(p))


def run(quick: bool = False, seed: int = 5) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    n = 128
    oversampling = 8
    nblk = 40 if quick else 200
    crs = np.array([0.8, 1.0, 1.2, 1.4, 1.6])
    z = np.arange(2, 16.1, 0.5)
    filt = firwin(105, [1.5 / 4, 2.5 / 4], pass_zero=False)
    papr = np.zeros((2 * len(crs) + 1, nblk))
    for blk in range(nblk):
        x, _ = mapper(2, n, rng=rng)
        x[0] = 0
        time = np.sqrt(2) * np.real(ifft_oversampling(x, n, oversampling))
        papr[0, blk] = _papr(time)
        for idx, cr in enumerate(crs):
            clipped = clipping(time, cr)
            filtered = lfilter(filt, [1.0], clipped)
            papr[1 + idx, blk] = _papr(clipped)
            papr[1 + len(crs) + idx, blk] = _papr(filtered)
    ccdf = np.array([[np.mean(row > threshold) for threshold in z] for row in papr])
    return z, ccdf


def save(output_dir: Path, z: np.ndarray, ccdf: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "ccdf_clipped_filtered.dat", np.column_stack([z, ccdf.T]), header="PAPR CCDF_rows")
    for idx, row in enumerate(ccdf):
        label = "no clip" if idx == 0 else f"case {idx}"
        plt.semilogy(z, row, label=label)
    plt.xlabel("PAPR0")
    plt.ylabel("CCDF")
    plt.grid(True, which="both")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(output_dir / "ccdf_clipped_filtered.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/ccdf_clipped_filtered_ofdm_signal"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
