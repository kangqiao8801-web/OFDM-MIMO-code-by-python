from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/ofdm_mimo_matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ofdm_mimo.coding import conv_encoder, viterbi_decode, viterbi_decode_soft, viterbi_init
from ofdm_mimo.modulation import qam16_demapper, qam16_mod, qam16_slicer, soft_decision_sigma


def run_simulation(quick: bool = False, seed: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    trellis = viterbi_init()
    packet_len = 120 if quick else 1200
    ebn0_dbs = np.arange(0, 8 if quick else 20)
    max_packets = 30 if quick else 1000
    target_errors = 5 if quick else 50
    bits_per_symbol = 4
    sq05 = np.sqrt(0.5)
    per_hard = np.zeros_like(ebn0_dbs, dtype=float)
    per_soft = np.zeros_like(ebn0_dbs, dtype=float)

    for idx, ebn0_db in enumerate(ebn0_dbs):
        hard_errors = 0
        soft_errors = 0
        packets = 0
        for packets in range(1, max_packets + 1):
            bit_stream = rng.integers(0, 2, packet_len)
            coded_bits = conv_encoder(bit_stream)
            symbol_stream = qam16_mod(coded_bits)
            h = sq05 * (rng.standard_normal(symbol_stream.size) + 1j * rng.standard_normal(symbol_stream.size))
            faded = symbol_stream * h
            bit_power = np.mean(np.abs(faded) ** 2) / bits_per_symbol
            sigma = np.sqrt(bit_power / 2 * 10 ** (-ebn0_db / 10))
            noisy = faded + sigma * (rng.standard_normal(symbol_stream.size) + 1j * rng.standard_normal(symbol_stream.size))
            compensated = noisy / h

            hard_bits = qam16_demapper(qam16_slicer(compensated))
            hard_decoded = viterbi_decode(hard_bits, trellis=trellis)[:packet_len]
            soft_bits = soft_decision_sigma(compensated, h)
            soft_decoded = viterbi_decode_soft(soft_bits, trellis=trellis)[:packet_len]

            hard_errors += int(np.any(hard_decoded != bit_stream))
            soft_errors += int(np.any(soft_decoded != bit_stream))
            if hard_errors > target_errors and soft_errors > target_errors:
                break
        per_hard[idx] = hard_errors / packets
        per_soft[idx] = soft_errors / packets
    return ebn0_dbs, per_hard, per_soft


def save_outputs(ebn0_dbs: np.ndarray, per_hard: np.ndarray, per_soft: np.ndarray, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(
        output_dir / "per.dat",
        np.column_stack([ebn0_dbs, per_hard, per_soft]),
        header="EbN0dB PER_hard PER_soft",
    )
    plt.figure(figsize=(6, 4))
    plt.semilogy(ebn0_dbs, per_hard, "o-", label="Hard")
    plt.semilogy(ebn0_dbs, per_soft, "s-", label="Soft")
    plt.xlabel("Eb/N0 [dB]")
    plt.ylabel("PER")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "per.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/soft_hard_siso"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    ebn0_dbs, per_hard, per_soft = run_simulation(quick=args.quick)
    save_outputs(ebn0_dbs, per_hard, per_soft, args.output_dir)


if __name__ == "__main__":
    main()
