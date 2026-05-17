from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.channel_models import doppler_psd, doppler_spectrum, fwgn, fwgn_ff, fwgn_tf, jakes_flat


def run(quick: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = 128 if quick else 512
    f0 = np.linspace(0, 0.98, 120)
    psd = np.vstack([doppler_psd("flat", f0), doppler_psd("class", f0), doppler_psd("sui", f0)])
    spec = doppler_spectrum(100, n)
    h, _, _, _ = fwgn(50, 1000, n, rng=np.random.default_rng(1))
    fad_ff, _ = fwgn_ff(2, np.array([30.0, 50.0]), n, 2, "class", rng=np.random.default_rng(2))
    fad_tf, _ = fwgn_tf(2, np.array([30.0, 50.0]), n, 128, 2, "flat", rng=np.random.default_rng(3))
    jakes, _ = jakes_flat(50, 1e-3, n)
    envelope = np.vstack([np.abs(h), np.abs(fad_ff[0]), np.abs(fad_tf[0]), np.abs(jakes)])
    return f0, psd, np.arange(n), spec, envelope


def save(output_dir: Path, f0: np.ndarray, psd: np.ndarray, n: np.ndarray, spec: np.ndarray, envelope: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "doppler_fwgn_models.dat", np.column_stack([n, spec, envelope.T]), header="sample spectrum fwgn fwgn_ff fwgn_tf jakes")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for label, row in zip(["flat", "class", "sui"], psd):
        axes[0].plot(f0, row, label=label)
    for label, row in zip(["FWGN", "FWGN-FF", "FWGN-TF", "Jakes"], envelope):
        axes[1].plot(n, row, label=label)
    axes[0].set_xlabel("f/fm")
    axes[0].set_ylabel("PSD")
    axes[1].set_xlabel("sample")
    axes[1].set_ylabel("envelope")
    for ax in axes:
        ax.grid(True)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "doppler_fwgn_models.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/doppler_fwgn_models"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
