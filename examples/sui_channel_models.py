from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.channel_models import sui_fading, sui_parameters


def run(quick: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = 128 if quick else 512
    params = [sui_parameters(ch) for ch in range(1, 7)]
    table = np.array([[ch, *delay, *power, corr, fnorm] for ch, (delay, power, _, _, corr, fnorm) in enumerate(params, start=1)])
    delay, power, k_factor, doppler, _, fnorm = params[2]
    fad, _ = sui_fading(power, k_factor, doppler, fnorm, n, 128, 2, rng=np.random.default_rng(4))
    return np.arange(1, 7), table, delay, np.abs(fad)


def save(output_dir: Path, channels: np.ndarray, table: np.ndarray, delay: np.ndarray, envelope: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "sui_channel_models.dat", table, header="ch delay0 delay1 delay2 power0 power1 power2 corr fnorm")
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    axes[0].plot(channels, table[:, -1], "o-")
    axes[0].set_xlabel("SUI channel")
    axes[0].set_ylabel("Fnorm [dB]")
    for idx, row in enumerate(envelope):
        axes[1].plot(row, label=f"tap {idx} delay={delay[idx]}us")
    axes[1].set_xlabel("sample")
    axes[1].set_ylabel("envelope")
    for ax in axes:
        ax.grid(True)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "sui_channel_models.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/sui_channel_models"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
