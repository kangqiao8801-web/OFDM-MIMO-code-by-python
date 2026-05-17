import numpy as np

from ofdm_mimo.ofdm import (
    ccdf_papr_dft_spreading,
    ccdf_pts,
    clipping,
    ifft_oversampling,
    papr,
    raised_cosine_filter,
)


def test_papr_matches_matlab_power_definition():
    x = np.array([1 + 1j, 2 + 0j, 0 + 0j])

    papr_db, avg_db, peak_db = papr(x)

    power = np.array([2.0, 4.0, 0.0])
    np.testing.assert_allclose(peak_db, 10 * np.log10(4.0))
    np.testing.assert_allclose(avg_db, 10 * np.log10(np.mean(power)))
    np.testing.assert_allclose(papr_db, 10 * np.log10(4.0 / np.mean(power)))


def test_ifft_oversampling_inserts_zeros_in_spectrum_middle():
    x = np.array([1, 2, 3, 4], dtype=complex)

    actual = ifft_oversampling(x, 4, 2)
    expected = 2 * np.fft.ifft(np.array([1, 2, 0, 0, 0, 0, 3, 4], dtype=complex), 8)

    np.testing.assert_allclose(actual, expected)


def test_clipping_uses_matlab_sigma_when_not_provided():
    x = np.array([1.0, 2.0, 10.0])

    clipped, sigma = clipping(x, 1.0, return_sigma=True)

    expected_sigma = np.sqrt(np.sum((x - np.mean(x)) ** 2) / x.size)
    np.testing.assert_allclose(sigma, expected_sigma)
    assert np.max(np.abs(clipped)) <= expected_sigma + 1e-12
    np.testing.assert_allclose(clipping(x, 1.0, sigma=2.0), np.array([1.0, 2.0, 2.0]))


def test_batch4_ccdf_helpers_are_valid_distributions():
    rng = np.random.default_rng(0)
    dbs = np.arange(0, 8)

    pts = ccdf_pts(32, 2, 4, 2, dbs, 12, rng=rng)
    dft_ccdf, paprs = ccdf_papr_dft_spreading("LF", 8, 2, 32, dbs, 12, rng=np.random.default_rng(1))

    assert pts.shape == dbs.shape
    assert dft_ccdf.shape == dbs.shape
    assert paprs.shape == (12,)
    assert np.all((0 <= pts) & (pts <= 1))
    assert np.all((0 <= dft_ccdf) & (dft_ccdf <= 1))
    assert np.all(np.diff(pts) <= 1e-12)
    assert np.all(np.diff(dft_ccdf) <= 1e-12)


def test_raised_cosine_filter_is_normalized_and_odd_length():
    taps = raised_cosine_filter(0.4, 3, 4)

    assert taps.size == 25
    np.testing.assert_allclose(np.sqrt(np.sum(taps**2)), 4.0)
