import numpy as np

from ofdm_mimo.metrics import bit_error_rate
from ofdm_mimo.modulation import qam_demod, qam_mod
from ofdm_mimo.ofdm import add_cp, guard_interval, remove_cp, remove_gi


def test_qam16_round_trip_gray_symbols():
    symbols = np.arange(16)

    modulated = qam_mod(symbols, 16, unit_average_power=False)
    detected = qam_demod(modulated, 16, unit_average_power=False)

    np.testing.assert_array_equal(detected, symbols)


def test_cp_guard_interval_round_trip():
    ofdm_symbol = np.arange(8) + 1j * np.arange(8, 16)

    with_cp = guard_interval(2, 8, 1, ofdm_symbol)
    recovered = remove_gi(2, 10, 1, with_cp)

    np.testing.assert_array_equal(with_cp[:2], ofdm_symbol[-2:])
    np.testing.assert_array_equal(recovered, ofdm_symbol)


def test_zero_padding_guard_interval_round_trip_with_offset():
    ofdm_symbol = np.arange(8, dtype=float)

    with_zp = guard_interval(3, 8, 2, ofdm_symbol)
    recovered = remove_gi(3, 11, 2, with_zp)

    np.testing.assert_array_equal(with_zp[-3:], np.zeros(3))
    np.testing.assert_array_equal(recovered, ofdm_symbol)


def test_add_remove_cp_helpers():
    x = np.arange(6)

    y = add_cp(x, 2)

    np.testing.assert_array_equal(y, np.array([4, 5, 0, 1, 2, 3, 4, 5]))
    np.testing.assert_array_equal(remove_cp(y, 2), x)


def test_bit_error_rate_counts_symbol_bits():
    ref = np.array([0, 1, 2, 3])
    got = np.array([0, 2, 2, 1])

    ber, errors, total = bit_error_rate(got, ref, bits_per_symbol=2)

    assert errors == 3
    assert total == 8
    assert ber == 3 / 8
