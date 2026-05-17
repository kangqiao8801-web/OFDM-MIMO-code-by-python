import numpy as np

from ofdm_mimo.channel_estimation import ls_ce, mmse_ce


def test_ls_channel_estimation_interpolates_all_subcarriers():
    nfft = 8
    nps = 2
    pilot_loc = np.array([0, 2, 4, 6])
    h = np.array([1 + 0.5j, 0.2 - 0.1j])
    h_freq = np.fft.fft(h, nfft)
    xp = np.ones(len(pilot_loc), dtype=complex)
    y = np.zeros(nfft, dtype=complex)
    y[pilot_loc] = h_freq[pilot_loc] * xp

    estimated = ls_ce(y, xp, pilot_loc, nfft, nps, "linear")

    assert estimated.shape == (nfft,)
    assert np.isfinite(estimated).all()
    np.testing.assert_allclose(estimated[pilot_loc], h_freq[pilot_loc])


def test_mmse_channel_estimation_is_finite_and_reasonable():
    nfft = 16
    nps = 4
    pilot_loc = np.array([0, 4, 8, 12])
    h = np.array([0.9 + 0.1j, 0.25 - 0.2j])
    h_freq = np.fft.fft(h, nfft)
    xp = np.ones(len(pilot_loc), dtype=complex)
    y = np.zeros(nfft, dtype=complex)
    y[pilot_loc] = h_freq[pilot_loc]

    estimated = mmse_ce(y, xp, pilot_loc, nfft, nps, h, snr_db=30)

    assert estimated.shape == (nfft,)
    assert np.isfinite(estimated).all()
    assert np.mean(np.abs(h_freq - estimated) ** 2) < 0.2
