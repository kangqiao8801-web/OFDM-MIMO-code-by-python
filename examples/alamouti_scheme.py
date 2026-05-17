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

from ofdm_mimo.modulation import qam_demod, qam_mod


def run(output_dir: Path, quick: bool = False, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    l_frame = 64 if quick else 130
    n_packets = 40 if quick else 600
    snr_dbs = np.array([0, 10, 20] if quick else [0, 5, 10, 15, 20, 25, 30])
    nt = 2
    order = 4
    ber = []

    for snr_db in snr_dbs:
        sigma = np.sqrt(0.5 / (10 ** (snr_db / 10)))
        errors = 0
        total = 0
        for _ in range(n_packets):
            tx_symbols = rng.integers(0, order, size=(l_frame, nt))
            x = qam_mod(tx_symbols, order)
            x1 = x
            x2 = np.column_stack([-np.conj(x[:, 1]), np.conj(x[:, 0])])
            h = (rng.standard_normal((l_frame, nt)) + 1j * rng.standard_normal((l_frame, nt))) / np.sqrt(2)
            n1 = sigma * (rng.standard_normal(l_frame) + 1j * rng.standard_normal(l_frame))
            n2 = sigma * (rng.standard_normal(l_frame) + 1j * rng.standard_normal(l_frame))
            r1 = np.sum(h * x1, axis=1) / np.sqrt(nt) + n1
            r2 = np.sum(h * x2, axis=1) / np.sqrt(nt) + n2

            z1 = r1 * np.conj(h[:, 0]) + np.conj(r2) * h[:, 1]
            z2 = r1 * np.conj(h[:, 1]) - np.conj(r2) * h[:, 0]
            gain = np.sum(np.abs(h) ** 2, axis=1) / np.sqrt(nt)
            detected = np.column_stack([
                qam_demod(z1 / gain, order),
                qam_demod(z2 / gain, order),
            ])
            errors += int(np.count_nonzero(detected != tx_symbols))
            total += tx_symbols.size
        ber.append(errors / total)

    ber_arr = np.asarray(ber)
    np.savetxt(output_dir / "ber.dat", np.column_stack([snr_dbs, ber_arr]), header="SNR_dB BER")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.semilogy(snr_dbs, ber_arr, marker="o")
    ax.set_xlabel("SNR [dB]")
    ax.set_ylabel("BER")
    ax.set_ylim(1e-4, 1)
    ax.grid(True, which="both")
    fig.tight_layout()
    fig.savefig(output_dir / "ber.png", dpi=150)
    plt.close(fig)
    return np.column_stack([snr_dbs, ber_arr])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "alamouti_scheme")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(args.output_dir, args.quick)
    print(f"Saved Alamouti BER results to {args.output_dir}")
    print(result)


if __name__ == "__main__":
    main()
