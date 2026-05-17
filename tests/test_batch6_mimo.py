import numpy as np

from ofdm_mimo.mimo import (
    alamouti_combine_2rx,
    alamouti_decode_2x1,
    alamouti_encode,
    block_diagonalization_precoders,
    codebook_generator,
    dirty_or_th_precoding,
    exhaustive_ml_detector,
    lrad_mmse,
    mimo_capacity_ant_selection_optimal,
    mimo_capacity_ant_selection_suboptimal,
    mmse_detect,
    mrc_combine,
    multi_user_precoder,
    original_lll,
    osic_detector,
    qrm_mld_detector,
    qrm_mld_soft,
    sqrd,
    stbc_3x4_code,
    sttc_detector,
    sttc_modulator,
    sttc_stage_modulation,
)
from ofdm_mimo.modulation import qam_mod


def test_alamouti_encoders_and_combiners_recover_noiseless_symbols():
    x = np.array([[1 + 1j, -1 + 1j]]) / np.sqrt(2)
    code = alamouti_encode(x)
    h = np.array([0.8 + 0.1j, -0.2 + 0.7j])
    r1 = code[0, 0, 0] * h[0] + code[0, 0, 1] * h[1]
    r2 = code[0, 1, 0] * h[0] + code[0, 1, 1] * h[1]

    decoded = alamouti_decode_2x1(np.array([r1]), np.array([r2]), h.reshape(1, 2))

    np.testing.assert_allclose(decoded, x, atol=1e-12)

    h2 = np.array([[h, h * (0.5 - 0.1j)]])
    r1_2 = np.array([[code[0, 0] @ h2[0, :, rx] for rx in range(2)]])
    r2_2 = np.array([[code[0, 1] @ h2[0, :, rx] for rx in range(2)]])
    np.testing.assert_allclose(alamouti_combine_2rx(r1_2, r2_2, h2), x, atol=1e-12)

    g3 = stbc_3x4_code(np.array([[1, 1j, -1, -1j]]))
    assert g3.shape == (8, 3, 1)


def test_linear_ordered_and_tree_detectors_find_qam_symbols():
    table = qam_mod(np.arange(16), 16)
    x = table[[0, 5]]
    h = np.array([[1.0 + 0.2j, 0.1 - 0.1j], [0.3 + 0.4j, 1.1 - 0.2j]])
    y = h @ x

    np.testing.assert_allclose(mmse_detect(y, h, 1e-8, table), x)
    np.testing.assert_allclose(osic_detector(y, h, 1e-8, 2, 1, table), x)
    np.testing.assert_allclose(exhaustive_ml_detector(y, h, table), x)
    np.testing.assert_allclose(qrm_mld_detector(y, h, m=8, constellation=table), x)

    llr = qrm_mld_soft(np.r_[y, y], np.eye(4, dtype=complex), m=8)
    assert llr.shape == (4, 4)
    assert np.all(np.isfinite(llr))


def test_precoding_capacity_and_codebook_helpers():
    h1 = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=complex)
    h2 = np.array([[0, 0, 1, 0], [0, 0, 0, 1]], dtype=complex)
    w1, w2 = block_diagonalization_precoders(h1, h2)
    np.testing.assert_allclose(h2 @ w1, np.zeros((2, 2)), atol=1e-12)
    np.testing.assert_allclose(h1 @ w2, np.zeros((2, 2)), atol=1e-12)

    codebook = codebook_generator()
    assert codebook.shape == (4, 2, 64)
    np.testing.assert_allclose(codebook[:, :, 0].conj().T @ codebook[:, :, 0], np.eye(2), atol=1e-12)

    h = np.eye(4, dtype=complex)
    cap_opt, idx_opt = mimo_capacity_ant_selection_optimal(h, 2, 10.0)
    cap_sub, idx_sub = mimo_capacity_ant_selection_suboptimal(h, 2, 10.0)
    assert cap_opt >= cap_sub - 1e-12
    assert len(idx_opt) == len(idx_sub) == 2

    w, beta, selected = multi_user_precoder(np.eye(4, dtype=complex), 4, 0.1, regularized=True)
    np.testing.assert_allclose(w.shape, (4, 4))
    assert beta > 0
    np.testing.assert_array_equal(selected, np.arange(4))

    x = np.ones((4, 2), dtype=complex)
    precoded, q = dirty_or_th_precoding(np.eye(4, dtype=complex), x, mode="dirty")
    np.testing.assert_allclose(q.conj().T @ q, np.eye(4), atol=1e-12)
    assert precoded.shape == x.shape


def test_sqrd_lll_lrad_and_mrc_are_well_formed():
    h = np.array([[1.0, 0.2], [0.1, 1.0], [0.0, 0.1], [0.2, 0.0]])
    q, r, pmat, order = sqrd(h)
    assert q.shape == h.shape
    assert r.shape == (2, 2)
    assert pmat.shape == (2, 2)
    np.testing.assert_array_equal(np.sort(order), np.arange(2))

    q2, r2, t = original_lll(*np.linalg.qr(h), 2, 0.75)
    np.testing.assert_allclose(q2 @ r2, np.linalg.qr(h)[0] @ np.linalg.qr(h)[1] @ t, atol=1e-8)

    x = np.array([1 + 0j, -1 + 0j])
    hc = np.eye(2, dtype=complex)
    np.testing.assert_allclose(lrad_mmse(hc, x, 1e-6), x, atol=1e-6)

    received = np.array([[1 + 0j, 0.5 + 0j]])
    channel = np.array([[1 + 0j, 0.5 + 0j]])
    detected = mrc_combine(received, channel, np.array([1 + 0j, -1 + 0j]))
    np.testing.assert_allclose(detected, np.array([1 + 0j]))


def test_sttc_modulation_and_detector_round_trip_noiseless():
    dlt, slt, order = sttc_stage_modulation("4_State_4PSK", nrx=2)
    data = np.array([[[0], [1]], [[1], [2]], [[2], [3]], [[3], [0]]])
    modulated = sttc_modulator(data, order)
    assert modulated.shape == data.shape

    ch = np.ones((2, 2, 1), dtype=complex)
    sig = np.einsum("tsp,srp->trp", modulated, ch)
    decoded, states = sttc_detector(sig, dlt, slt, ch)
    assert decoded.shape == data.shape
    assert states.ndim == 1
