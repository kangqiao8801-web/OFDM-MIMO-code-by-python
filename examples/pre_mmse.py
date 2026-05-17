from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.modulation import qam_demod, qam_mod


def run(quick: bool = False, seed: int = 4) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_frame = 20 if quick else 100
    n_packet = 30 if quick else 1000
    b = 2
    order = 2**b
    nt = nr = 4
    snr_dbs = np.arange(0, 21, 4 if quick else 2)
    ber = np.zeros_like(snr_dbs, dtype=float)
    eye = np.eye(nr)
    for i_snr, snr_db in enumerate(snr_dbs):
        noise_var = nt * 0.5 * 10 ** (-snr_db / 10)
        sigma = np.sqrt(noise_var)
        errors = 0
        total = 0
        for _ in range(n_packet):
            msg = rng.integers(0, order, nt * n_frame)
            symbols = qam_mod(msg, order).reshape(nt, n_frame)
            h = (rng.standard_normal((nr, nt)) + 1j * rng.standard_normal((nr, nt))) / np.sqrt(2)
            temp_w = h.conj().T @ np.linalg.inv(h @ h.conj().T + noise_var * eye)
            beta = np.sqrt(nt / np.trace(temp_w @ temp_w.conj().T).real)
            tx = beta * temp_w @ symbols
            rx = h @ tx + sigma * (rng.standard_normal((nr, n_frame)) + 1j * rng.standard_normal((nr, n_frame)))
            y = rx / beta
            detected = qam_demod(y.reshape(-1), order)
            errors += int(np.count_nonzero(detected != msg))
            total += msg.size * b
        ber[i_snr] = errors / total
    return snr_dbs, ber


def save(output_dir: Path, snr_dbs: np.ndarray, ber: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "ber.dat", np.column_stack([snr_dbs, ber]), header="SNRdB BER")
    plt.semilogy(snr_dbs, ber, "^-")
    plt.xlabel("SNR [dB]")
    plt.ylabel("BER")
    plt.grid(True, which="both")
    plt.tight_layout()
    plt.savefig(output_dir / "ber.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/pre_mmse"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
