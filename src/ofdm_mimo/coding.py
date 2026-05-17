from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike


CONV_CODE_GEN_POLY = np.array(
    [
        [1, 0, 1, 1, 0, 1, 1],
        [1, 1, 1, 1, 0, 0, 1],
    ],
    dtype=int,
)


@dataclass(frozen=True)
class ViterbiTrellis:
    prev_state: np.ndarray
    prev_state_outbits: np.ndarray


def convolution_encoder(in_bits: ArrayLike) -> np.ndarray:
    bits = np.asarray(in_bits, dtype=int).ravel()
    n_bits = CONV_CODE_GEN_POLY.shape[1] + bits.size - 1
    coded = np.zeros((CONV_CODE_GEN_POLY.shape[0], n_bits), dtype=int)
    for row, poly in enumerate(CONV_CODE_GEN_POLY):
        coded[row] = np.convolve(bits, poly) % 2
    return coded


def conv_encoder(in_bits: ArrayLike) -> np.ndarray:
    return convolution_encoder(in_bits).ravel(order="F")


def trellis_encoder(data: ArrayLike, dlt: ArrayLike, slt: ArrayLike) -> np.ndarray:
    data_arr = np.asarray(data, dtype=int)
    dlt_arr = np.asarray(dlt)
    slt_arr = np.asarray(slt, dtype=int)
    if data_arr.ndim != 3 or data_arr.shape[1] != 1:
        raise ValueError("data must have MATLAB-compatible shape (L_frame, 1, N_frames).")

    l_frame, _, n_frames = data_arr.shape
    output_width = dlt_arr.shape[2] if dlt_arr.ndim == 3 else 1
    encoded = np.empty((l_frame, output_width, n_frames), dtype=dlt_arr.dtype)
    state = 0
    for frame in range(n_frames):
        for idx in range(l_frame):
            symbol = data_arr[idx, 0, frame]
            encoded[idx, :, frame] = dlt_arr[state, symbol, :]
            state = int(np.ravel(slt_arr[state, symbol, :])[0]) - 1
    return encoded


def viterbi_init() -> ViterbiTrellis:
    prev_state = np.zeros((64, 2), dtype=int)
    prev_state_outbits = np.zeros((64, 2, 2), dtype=int)

    for state in range(64):
        state_bits = np.array([(state >> i) & 1 for i in range(6)], dtype=int)
        input_bit = state_bits[0]
        for transition in range(2):
            prev_state_bits = np.r_[state_bits[1:6], transition]
            prev = sum(int(bit) << i for i, bit in enumerate(prev_state_bits))
            prev_state[state, transition] = prev
            reg = np.r_[input_bit, prev_state_bits]
            prev_state_outbits[state, transition, 0] = 2 * (np.sum(CONV_CODE_GEN_POLY[0] * reg) % 2) - 1
            prev_state_outbits[state, transition, 1] = 2 * (np.sum(CONV_CODE_GEN_POLY[1] * reg) % 2) - 1

    return ViterbiTrellis(prev_state=prev_state, prev_state_outbits=prev_state_outbits)


def viterbi_decode(rx_bits: ArrayLike, trellis: ViterbiTrellis | None = None) -> np.ndarray:
    bits = 2 * np.asarray(rx_bits, dtype=int).ravel() - 1
    return _viterbi_decode_metrics(bits, trellis)


def viterbi_decode_soft(rx_bits: ArrayLike, trellis: ViterbiTrellis | None = None) -> np.ndarray:
    metrics = np.asarray(rx_bits, dtype=float).ravel()
    return _viterbi_decode_metrics(metrics, trellis)


def _viterbi_decode_metrics(rx_metrics: np.ndarray, trellis: ViterbiTrellis | None) -> np.ndarray:
    if rx_metrics.size % 2:
        raise ValueError("Viterbi input length must be even.")
    if trellis is None:
        trellis = viterbi_init()

    n_bits = rx_metrics.size // 2
    cum_metrics = np.full(64, -1e6, dtype=float)
    cum_metrics[0] = 0.0
    max_paths = np.zeros((64, n_bits), dtype=int)

    for bit_idx in range(n_bits):
        r0, r1 = rx_metrics[2 * bit_idx : 2 * bit_idx + 2]
        tmp = np.zeros(64, dtype=float)
        for state in range(64):
            metric0 = trellis.prev_state_outbits[state, 0, 0] * r0 + trellis.prev_state_outbits[state, 0, 1] * r1
            metric1 = trellis.prev_state_outbits[state, 1, 0] * r0 + trellis.prev_state_outbits[state, 1, 1] * r1
            score0 = cum_metrics[trellis.prev_state[state, 0]] + metric0
            score1 = cum_metrics[trellis.prev_state[state, 1]] + metric1
            if score0 > score1:
                tmp[state] = score0
                max_paths[state, bit_idx] = 0
            else:
                tmp[state] = score1
                max_paths[state, bit_idx] = 1
        cum_metrics = tmp

    out_bits = np.zeros(n_bits, dtype=int)
    state = 0
    for bit_idx in range(n_bits - 1, -1, -1):
        out_bits[bit_idx] = state % 2
        state = trellis.prev_state[state, max_paths[state, bit_idx]]
    return out_bits
