from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.modulation import qam_mod
from ofdm_mimo.ofdm import add_cfo, add_cp, add_sto, sto_by_correlation, sto_by_difference


def run(quick: bool = False, seed: int = 1) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    nfft = 128
    ng = nfft // 4
    nofdm = nfft + ng
    nstos = np.array([-3, -3, 2, 2])
    cfos = np.array([0.0, 0.5, 0.0, 0.5])
    nsym = 20 if quick else 100
    max_iter = 4 if quick else 10
    estimates = np.zeros((len(nstos), 2))
    mag_snapshot = None
    for case, (nsto, cfo) in enumerate(zip(nstos, cfos)):
        x = []
        for _ in range(nsym):
            freq = qam_mod(rng.integers(0, 4, size=nfft), 4)
            x.append(add_cp(np.fft.ifft(freq), ng))
        y = add_sto(add_cfo(np.concatenate(x), cfo, nfft), -int(nsto))
        sig = np.mean(np.abs(y) ** 2)
        sigma = np.sqrt(sig / 2 * 10 ** (-30 / 10))
        cor_vals = []
        dif_vals = []
        for _ in range(max_iter):
            obs = y + sigma * (rng.standard_normal(y.size) + 1j * rng.standard_normal(y.size))
            sto_cor, mag_cor = sto_by_correlation(obs, nfft, ng, nofdm // 2)
            sto_dif, mag_dif = sto_by_difference(obs, nfft, ng, nofdm // 2)
            cor_vals.append(sto_cor)
            dif_vals.append(sto_dif)
            mag_snapshot = np.column_stack([mag_cor, mag_dif])
        estimates[case] = [np.mean(cor_vals), np.mean(dif_vals)]
    return nstos, estimates, mag_snapshot


def save(output_dir: Path, nstos: np.ndarray, estimates: np.ndarray, mag: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "sto.dat", np.column_stack([nstos, estimates]), header="nSTO corr diff")
    plt.figure(figsize=(7, 4))
    plt.plot(nstos, estimates[:, 0], "o", label="Correlation")
    plt.plot(nstos, estimates[:, 1], "s", label="Difference")
    plt.plot(nstos, nstos, "k:", label="Target")
    plt.xlabel("True STO [samples]")
    plt.ylabel("Estimated STO")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "sto_estimates.png", dpi=150)
    plt.close()
    np.savetxt(output_dir / "sto_metric.dat", mag, header="correlation difference")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/sto_estimation"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
