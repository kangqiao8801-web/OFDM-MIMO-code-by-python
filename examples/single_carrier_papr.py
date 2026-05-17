from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from _papr_common import save_dat
from ofdm_mimo.modulation import mapper, modulate_carrier
from ofdm_mimo.ofdm import papr


def run() -> tuple[np.ndarray, np.ndarray, list[tuple[np.ndarray, np.ndarray, np.ndarray]]]:
    ts = 1
    nos = 8
    fc = 1
    bits = np.array([1, 2, 4])
    paprs = np.zeros((2, bits.size))
    waveforms = []
    for i, b in enumerate(bits):
        symbols, _ = mapper(int(b))
        base = np.repeat(symbols, nos)
        passband, time = modulate_carrier(symbols, ts, nos, fc, passband=True)
        paprs[0, i] = papr(base)[0]
        paprs[1, i] = papr(passband)[0]
        waveforms.append((time, base, passband))
    return bits, paprs, waveforms


def save(output_dir: Path, bits: np.ndarray, paprs: np.ndarray, waveforms: list[tuple[np.ndarray, np.ndarray, np.ndarray]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    save_dat(output_dir / "single_carrier_papr.dat", [bits, paprs[0], paprs[1]], "bits baseband_PAPR_dB passband_PAPR_dB")
    fig, axes = plt.subplots(bits.size, 2, figsize=(9, 7), squeeze=False)
    for row, b, (time, base, passband) in zip(axes, bits, waveforms):
        row[0].stem(np.arange(base.size), np.abs(base) ** 2, linefmt="k-", markerfmt="k.", basefmt=" ")
        row[0].set_title(f"{2**b}-ary baseband")
        row[1].stem(time, passband * passband, linefmt="r-", markerfmt="r.", basefmt=" ")
        row[1].set_title(f"{2**b}-ary passband")
        for ax in row:
            ax.set_ylabel("power")
            ax.grid(True)
    fig.tight_layout()
    fig.savefig(output_dir / "single_carrier_papr.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/single_carrier_papr"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run())


if __name__ == "__main__":
    main()
