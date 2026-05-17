from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from _papr_common import load_preamble, save_dat
from ofdm_mimo.ofdm import ifft_oversampling, papr


def run(quick: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = 1024
    count = 16 if quick else 114
    idx = np.arange(count)
    papr_db = np.zeros(count)
    papr_os_db = np.zeros(count)
    for i in idx:
        x_freq = load_preamble(int(i))
        papr_db[i] = papr(ifft_oversampling(x_freq, n, 1))[0]
        papr_os_db[i] = papr(ifft_oversampling(x_freq, n, 4))[0]
    return idx, papr_db, papr_os_db


def save(output_dir: Path, idx: np.ndarray, papr_db: np.ndarray, papr_os_db: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    save_dat(output_dir / "papr_of_preamble.dat", [idx, papr_db, papr_os_db], "index PAPR_dB PAPR_oversampled_dB")
    plt.figure(figsize=(7, 4))
    plt.plot(idx, papr_db, "-o", label="L=1")
    plt.plot(idx, papr_os_db, ":*", label="L=4")
    plt.xlabel("preamble index")
    plt.ylabel("PAPR [dB]")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "papr_of_preamble.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/papr_of_preamble"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
