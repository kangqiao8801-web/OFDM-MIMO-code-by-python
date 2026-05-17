from __future__ import annotations

from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MATLAB_SOURCE = ROOT / "MIMO-OFDM无线通信技术及MATLAB实现SourceCode  "


def save_dat(path: Path, columns: list[np.ndarray], header: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(path, np.column_stack(columns), header=header)


def load_preamble(index: int) -> np.ndarray:
    path = MATLAB_SOURCE / "Wibro-Preamble" / f"Preamble_sym{index}.dat"
    data = np.loadtxt(path)
    return np.fft.fftshift(np.sign(data[:, 0]))
