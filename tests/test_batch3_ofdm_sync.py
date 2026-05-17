import numpy as np

from ofdm_mimo.ofdm import (
    add_cfo,
    add_pilot,
    add_sto,
    ccdf_ofdma,
    cfo_classen,
    cfo_cp,
    cfo_moose,
    clipping,
    ifft_oversampling,
    sto_by_correlation,
    sto_by_difference,
)


def test_add_cfo_and_add_sto_match_matlab_semantics():
    x = np.ones(8, dtype=complex)
    y = add_cfo(x, 0.25, 8)
    np.testing.assert_allclose(y, np.exp(1j * 2 * np.pi * 0.25 * np.arange(8) / 8))

    np.testing.assert_array_equal(add_sto(np.arange(5), 2), np.array([2, 3, 4, 0, 0]))
    np.testing.assert_array_equal(add_sto(np.arange(5), -2), np.array([0, 0, 0, 1, 2]))


def test_add_pilot_and_cfo_estimators_recover_known_offset():
    nfft = 32
    ng = 8
    cfo = 0.125
    freq = add_pilot(np.zeros(nfft, dtype=complex), nfft, 4)
    time = np.fft.ifft(freq)
    symbol = np.r_[time[-ng:], time]
    y = add_cfo(np.r_[symbol, symbol], cfo, nfft)

    assert abs(cfo_cp(y[: nfft + ng], nfft, ng) - cfo) < 1e-12
    assert abs(cfo_moose(add_cfo(np.r_[time, time], cfo, nfft), nfft) - cfo) < 1e-12
    assert abs(cfo_classen(y, nfft, ng, freq) - cfo) < 1e-12


def test_sto_estimators_and_papr_helpers_are_finite():
    rng = np.random.default_rng(0)
    nfft = 32
    ng = 8
    freq = rng.normal(size=nfft) + 1j * rng.normal(size=nfft)
    time = np.fft.ifft(freq)
    symbol = np.r_[time[-ng:], time]
    y = np.r_[np.zeros(nfft // 2, dtype=complex), symbol, symbol, np.zeros(nfft, dtype=complex)]

    sto_cor, mag_cor = sto_by_correlation(y, nfft, ng, (nfft + ng) // 2)
    sto_dif, mag_dif = sto_by_difference(y, nfft, ng, (nfft + ng) // 2)

    assert np.isfinite(sto_cor)
    assert np.isfinite(sto_dif)
    assert mag_cor.shape == (nfft + ng,)
    assert mag_dif.shape == (nfft + ng,)

    os = ifft_oversampling(np.ones(4), 4, 2)
    assert os.shape == (8,)
    clipped = clipping(np.array([0.5, 2.0, -2.0]), 1.0)
    samples = np.array([0.5, 2.0, -2.0])
    threshold = np.sqrt(np.mean((samples - np.mean(samples)) ** 2))
    np.testing.assert_allclose(clipped, np.array([0.5, threshold, -threshold]))

    ccdf = ccdf_ofdma(16, 2, 2, np.arange(0, 8), 8, rng=np.random.default_rng(1))
    assert ccdf.shape == (8,)
    assert np.all((0 <= ccdf) & (ccdf <= 1))
