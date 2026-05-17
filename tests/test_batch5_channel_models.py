import numpy as np

from ofdm_mimo.channel_models import (
    channel1,
    channel_coeff,
    convert_uwb_ct,
    doppler_psd,
    doppler_spectrum,
    fwgn,
    fwgn_ff,
    fwgn_tf,
    ieee802_11_model,
    jakes_flat,
    pl_free,
    pl_hata,
    pl_ieee80216d,
    pl_logdist_or_norm,
    ray_fading,
    ray_model,
    ric_model,
    sui_fading,
    sui_parameters,
    sv_model_ct,
    uwb_model_ct,
    uwb_parameters,
)


def test_path_loss_models_match_reference_formulas():
    np.testing.assert_allclose(pl_free(2e9, 100), 78.4623720993283)
    np.testing.assert_allclose(pl_logdist_or_norm(2e9, np.array([100.0]), 1.0, 2.0), np.array([78.4623720993283]))
    assert pl_hata(900e6, np.array([1000.0]), 30, 1.5, "urban").shape == (1,)
    assert pl_ieee80216d(2.5e9, np.array([50.0, 100.0, 500.0]), "A").shape == (3,)


def test_doppler_and_fading_generators_are_normalized():
    spec = doppler_spectrum(100, 32)
    assert spec.shape == (32,)
    assert np.all(spec > 0)
    np.testing.assert_allclose(doppler_psd("flat", np.array([0.0, 0.5])), np.ones(2))

    h, nfft, nifft, coeff = fwgn(50, 1000, 64, rng=np.random.default_rng(0))
    assert h.shape == (64,)
    assert nfft >= 8
    assert nifft >= nfft
    assert coeff.shape == (nfft,)
    np.testing.assert_allclose(np.mean(np.abs(h) ** 2), 1.0, rtol=0.2)

    fad_ff, tf_ff = fwgn_ff(2, np.array([30.0, 50.0]), 128, 2, "class", rng=np.random.default_rng(1))
    fad_tf, tf_tf = fwgn_tf(2, np.array([30.0, 50.0]), 64, 64, 2, "flat", rng=np.random.default_rng(2))
    assert fad_ff.shape == (2, 128)
    assert fad_tf.shape == (2, 64)
    assert tf_ff > 0
    assert tf_tf > 0
    np.testing.assert_allclose(np.mean(np.abs(fad_tf) ** 2, axis=1), np.ones(2), rtol=0.25)


def test_jakes_ray_rician_and_correlated_channels():
    h, tf = jakes_flat(20, 1e-3, 100)
    assert h.shape == (100,)
    assert tf > 0

    ray = ray_model(2000, rng=np.random.default_rng(3))
    ric = ric_model(6, 2000, rng=np.random.default_rng(4))
    assert abs(np.mean(np.abs(ray) ** 2) - 1.0) < 0.1
    assert np.mean(np.abs(ric)) > np.mean(np.abs(ray))

    hh = channel_coeff(2, 2, 8, [1, 0.5], [1, 0.2], "complex", rng=np.random.default_rng(5))
    assert hh.shape == (2, 2, 8)

    sig = np.ones((4, 2, 3), dtype=complex)
    corr, coefs = channel1(sig, 20, 2, rng=np.random.default_rng(6))
    assert corr.shape == (4, 2, 3)
    assert coefs.shape == (2, 2, 3)


def test_profile_and_uwb_models_return_consistent_shapes():
    pdp = ieee802_11_model(50e-9, 10e-9)
    assert pdp.ndim == 1
    np.testing.assert_allclose(np.sum(pdp), 1.0)

    delay, power, k_factor, doppler, corr, fnorm = sui_parameters(3)
    np.testing.assert_allclose(delay, np.array([0.0, 0.4, 0.9]))
    assert power.shape == k_factor.shape == doppler.shape == (3,)
    assert corr > 0
    assert fnorm < 0

    sui, tf = sui_fading(power, k_factor, doppler, fnorm, 64, 64, 2, rng=np.random.default_rng(7))
    assert sui.shape == (3, 64)
    assert tf > 0

    params = uwb_parameters(1)
    assert len(params) == 8
    h, t, t0, np_paths = uwb_model_ct(*params, num_ch=2, rng=np.random.default_rng(8))
    assert h.shape == t.shape
    assert t0.shape == (2,)
    assert np_paths.shape == (2,)

    h_sv, t_sv, _, np_sv = sv_model_ct(0.0233, 2.5, 7.1, 4.3, 2, rng=np.random.default_rng(9))
    h_disc, oversampling = convert_uwb_ct(h_sv, t_sv, np_sv, 2, 0.167)
    assert h_disc.shape[1] == 2
    assert oversampling >= 1


def test_ray_fading_shape_matches_pdp_paths():
    pdp = np.array([0.8, 0.2])
    phases = np.zeros((2, 4))
    angles = np.tile(np.array([0, 90, 180, 270]), (2, 1))
    t = np.linspace(0, 1e-3, 8)

    h = ray_fading(4, pdp, phases, angles, 10.0, 0.0, 0.15, t)

    assert h.shape == (2, 8)
