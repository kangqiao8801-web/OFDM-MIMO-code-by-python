from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.channel_models import channel1
from ofdm_mimo.coding import trellis_encoder
from ofdm_mimo.modulation import data_generator
from ofdm_mimo.mimo import sttc_detector, sttc_modulator, sttc_stage_modulation


def run(quick: bool = False, seed: int = 15) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    snr = np.array([5, 7, 9, 11])
    states = ["4_State_4PSK", "8_State_4PSK", "16_State_4PSK", "32_State_4PSK"]
    nframe = 30 if quick else 130
    npackets = 20 if quick else 100
    fer = np.zeros((len(states), snr.size))
    for sidx, state in enumerate(states):
        dlt, slt, order = sttc_stage_modulation(state, 2)
        source = data_generator(nframe, npackets, order, 3, rng)
        encoded = trellis_encoder(source, dlt, slt)
        modulated = sttc_modulator(encoded, order)
        for i, db in enumerate(snr):
            signal, coefs = channel1(modulated, float(db), 2, rng)
            detected, _ = sttc_detector(signal, dlt, slt, coefs)
            fer[sidx, i] = np.mean(np.any(source != detected, axis=(0, 1)))
    return snr, fer


def save(output_dir: Path, snr: np.ndarray, fer: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "sttc_simulation.dat", np.column_stack([snr, fer.T]), header="SNR_dB FER_4 FER_8 FER_16 FER_32")
    plt.figure(figsize=(7, 4))
    for label, row in zip(["4-state", "8-state", "16-state", "32-state"], fer):
        plt.semilogy(snr, row, "o-", label=label)
    plt.xlabel("SNR [dB]")
    plt.ylabel("FER")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "sttc_simulation.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/sttc_simulation"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
