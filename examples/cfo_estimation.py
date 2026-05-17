from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.ofdm import add_cfo, add_cp, add_pilot, cfo_classen, cfo_cp, cfo_moose


def run(quick: bool = False, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    cfo = 0.15
    nfft = 128
    ng = nfft // 4
    nsym = 3
    xp = add_pilot(np.zeros(nfft, dtype=complex), nfft, 4)
    frames = []
    for idx in range(nsym):
        freq = xp if idx < 2 else add_pilot(rng.normal(size=nfft) + 1j * rng.normal(size=nfft), nfft, 4)
        frames.append(add_cp(np.fft.ifft(freq, nfft), ng))
    y = np.concatenate(frames)
    y_cfo = add_cfo(y, cfo, nfft)
    sig_power = np.mean(np.abs(y_cfo) ** 2)
    snr_dbs = np.arange(0, 31, 6 if quick else 3)
    max_iter = 20 if quick else 100
    mse = np.zeros((snr_dbs.size, 3))
    for i, snr_db in enumerate(snr_dbs):
        sigma = np.sqrt(sig_power / 2 * 10 ** (-snr_db / 10))
        for _ in range(max_iter):
            noise = sigma * (rng.standard_normal(y_cfo.size) + 1j * rng.standard_normal(y_cfo.size))
            obs = y_cfo + noise
            est = np.array([cfo_cp(obs, nfft, ng), cfo_moose(obs[ng : ng + 2 * nfft], nfft), cfo_classen(obs, nfft, ng, xp)])
            target = np.array([cfo, cfo, cfo * nfft / (nfft + ng)])
            mse[i] += (est - target) ** 2
    return snr_dbs, mse / max_iter


def save(output_dir: Path, snr_dbs: np.ndarray, mse: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "mse.dat", np.column_stack([snr_dbs, mse]), header="SNRdB CP Moose Classen")
    for idx, label in enumerate(["CP", "Moose", "Classen"]):
        plt.semilogy(snr_dbs, mse[:, idx], marker="o", label=label)
    plt.xlabel("SNR [dB]")
    plt.ylabel("MSE")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "mse.png", dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/cfo_estimation"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
