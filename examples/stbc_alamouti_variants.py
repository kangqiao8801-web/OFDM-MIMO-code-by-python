from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.mimo import alamouti_decode_2x1, alamouti_encode, stbc_3x4_code
from ofdm_mimo.modulation import qam_demod, qam_mod


def _simulate(nrx: int, snr_dbs: np.ndarray, nframe: int, npackets: int, rng: np.random.Generator) -> np.ndarray:
    ber = np.zeros_like(snr_dbs, dtype=float)
    for i, snr_db in enumerate(snr_dbs):
        sigma = np.sqrt(0.5 / 10 ** (snr_db / 10))
        errors = 0
        total = 0
        for _ in range(npackets):
            idx = rng.integers(0, 4, size=(nframe, 2))
            x = qam_mod(idx, 4)
            code = alamouti_encode(x)
            h = (rng.normal(size=(nframe, 2, nrx)) + 1j * rng.normal(size=(nframe, 2, nrx))) / np.sqrt(2)
            r1 = np.einsum("bt,btn->bn", code[:, 0], h) + sigma * (rng.normal(size=(nframe, nrx)) + 1j * rng.normal(size=(nframe, nrx)))
            r2 = np.einsum("bt,btn->bn", code[:, 1], h) + sigma * (rng.normal(size=(nframe, nrx)) + 1j * rng.normal(size=(nframe, nrx)))
            if nrx == 1:
                dec = alamouti_decode_2x1(r1[:, 0], r2[:, 0], h[:, :, 0])
            else:
                from ofdm_mimo.mimo import alamouti_combine_2rx

                dec = alamouti_combine_2rx(r1, r2, h)
            errors += np.count_nonzero(qam_demod(dec, 4) != idx)
            total += idx.size
        ber[i] = errors / total
    return ber


def run(quick: bool = False, seed: int = 11) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    snr = np.array([0, 5, 10, 15, 20])
    nframe = 80 if quick else 200
    npackets = 40 if quick else 300
    ber21 = _simulate(1, snr, nframe, npackets, rng)
    ber22 = _simulate(2, snr, nframe, npackets, rng)
    g3_energy = np.mean(np.abs(stbc_3x4_code(qam_mod(rng.integers(0, 4, size=(16, 4)), 4))) ** 2)
    return snr, np.vstack([ber21, ber22, np.full_like(ber21, g3_energy)])


def save(output_dir: Path, snr: np.ndarray, curves: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "stbc_alamouti_variants.dat", np.column_stack([snr, curves.T]), header="SNR_dB alamouti_2x1 alamouti_2x2 stbc_3x4_energy")
    plt.figure(figsize=(7, 4))
    plt.semilogy(snr, curves[0], "o-", label="Alamouti 2x1")
    plt.semilogy(snr, curves[1], "s-", label="Alamouti 2x2")
    plt.xlabel("SNR [dB]")
    plt.ylabel("symbol error rate")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "stbc_alamouti_variants.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/stbc_alamouti_variants"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
