from __future__ import annotations

import argparse
from pathlib import Path

import _example_common  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

from ofdm_mimo.channel_models import convert_uwb_ct, sv_model_ct, uwb_model_ct, uwb_parameters


def run(quick: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    params = [uwb_parameters(cm) for cm in range(1, 5)]
    table = np.array([[cm, *p] for cm, p in enumerate(params, start=1)], dtype=float)
    num_ch = 2 if quick else 4
    h, t, _, np_paths = uwb_model_ct(*params[0], num_ch=num_ch, rng=np.random.default_rng(5))
    h_sv, t_sv, _, np_sv = sv_model_ct(params[0][0], params[0][1], params[0][2], params[0][3], num_ch, rng=np.random.default_rng(6))
    h_disc, oversampling = convert_uwb_ct(h_sv, t_sv, np_sv, num_ch, 0.167)
    summary = np.array([[oversampling, h_disc.shape[0], np.mean(np_paths), np.mean(np_sv)]])
    return table, t[:, 0], np.abs(h[:, 0]), summary


def save(output_dir: Path, table: np.ndarray, t: np.ndarray, h_abs: np.ndarray, summary: np.ndarray) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(output_dir / "uwb_parameters.dat", table, header="cm Lam lam Gam gam nlos sdi sdc sdr")
    np.savetxt(output_dir / "uwb_channel_models.dat", np.column_stack([t, h_abs]), header="time_ns abs_h")
    np.savetxt(output_dir / "uwb_discrete_summary.dat", summary, header="oversampling h_len mean_uwb_paths mean_sv_paths")
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    axes[0].plot(table[:, 0], table[:, 1], "o-", label="cluster rate")
    axes[0].plot(table[:, 0], table[:, 2], "s-", label="ray rate")
    markerline, stemlines, baseline = axes[1].stem(t, h_abs, linefmt="k-", markerfmt="ko", basefmt=" ")
    plt.setp(stemlines, linewidth=0.8)
    plt.setp(markerline, markersize=3)
    axes[0].set_xlabel("CM")
    axes[0].set_ylabel("rate [1/ns]")
    axes[1].set_xlabel("time [ns]")
    axes[1].set_ylabel("|h|")
    for ax in axes:
        ax.grid(True)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "uwb_channel_models.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/uwb_channel_models"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    save(args.output_dir, *run(args.quick))


if __name__ == "__main__":
    main()
