import numpy as np

from ofdm_mimo.coding import (
    conv_encoder,
    convolution_encoder,
    viterbi_decode,
    viterbi_decode_soft,
    viterbi_init,
    trellis_encoder,
)
from ofdm_mimo.metrics import ber, ber_qam
from ofdm_mimo.modulation import (
    data_generator,
    mapper,
    modulate_carrier,
    modulator,
    modulo,
    qam16_demapper,
    qam16_mod,
    qam16_real_slicer,
    qam16_slicer,
    qam16_slicer_soft,
    qpsk_demapper,
    qpsk_mapper,
    soft_decision_sigma,
    soft_output2x2,
)


def test_qpsk_mapper_and_demapper_match_matlab_table():
    bits = np.array([0, 0, 0, 1, 1, 0, 1, 1])

    symbols = qpsk_mapper(bits)

    np.testing.assert_allclose(
        symbols,
        np.array([1, 1j, -1j, -1]) / np.sqrt(2),
    )
    np.testing.assert_array_equal(qpsk_demapper(symbols), bits)


def test_qam16_mod_demapper_and_slicers_match_matlab_tables():
    bits = np.array(
        [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            1,
        ]
    )

    symbols = qam16_mod(bits)

    np.testing.assert_allclose(
        symbols,
        np.array([-3 + 3j, -1 + 3j, 1 - 1j]) / np.sqrt(10),
    )
    np.testing.assert_array_equal(qam16_demapper(symbols), bits)
    np.testing.assert_allclose(qam16_slicer(symbols + 0.07 - 0.04j), symbols)
    np.testing.assert_allclose(qam16_real_slicer(np.array([-2.5, -0.2, 0.2, 2.5]) / np.sqrt(10)), np.array([-3, -1, 1, 3]) / np.sqrt(10))
    np.testing.assert_array_equal(qam16_slicer_soft(np.array([-3 - 3j]) / np.sqrt(10)), np.array([0, 0, 0, 0]))


def test_modulator_mapper_data_generator_and_modulo():
    bits = np.array([0, 0, 0, 1, 1, 1, 1, 0])

    symbols, table, order = modulator(bits, 2)

    assert order == 4
    np.testing.assert_allclose(symbols, table[[0, 1, 3, 2]])

    full, name = mapper(2)
    assert name == "QPSK"
    assert len(full) == 4

    random_symbols, name = mapper(4, 5, rng=np.random.default_rng(0))
    assert name == "16QAM"
    assert random_symbols.shape == (5,)

    data = data_generator(3, 2, 4, 2, rng=np.random.default_rng(0))
    assert data.shape == (5, 1, 2)
    np.testing.assert_array_equal(data[-2:, :, :], 0)
    assert data[:3].max() <= 3

    np.testing.assert_allclose(modulo(np.array([3 + 3j, -3 - 3j]), 2), np.array([-1 - 1j, 1 + 1j]))


def test_convolution_encoders_and_viterbi_round_trip():
    bits = np.array([1, 0, 1, 1, 0])

    encoded_matrix = convolution_encoder(bits)
    encoded_stream = conv_encoder(bits)

    assert encoded_matrix.shape == (2, len(bits) + 6)
    np.testing.assert_array_equal(encoded_stream, encoded_matrix.ravel(order="F"))

    trellis = viterbi_init()
    decoded = viterbi_decode(encoded_stream, trellis=trellis)
    decoded_soft = viterbi_decode_soft(2 * encoded_stream - 1, trellis=trellis)

    np.testing.assert_array_equal(decoded[: len(bits)], bits)
    np.testing.assert_array_equal(decoded_soft[: len(bits)], bits)


def test_trellis_encoder_uses_state_transition_tables():
    data = np.array([[[0]], [[1]], [[0]]])
    dlt = np.array(
        [
            [[10, 11], [12, 13]],
            [[20, 21], [22, 23]],
        ]
    )
    slt = np.array(
        [
            [[2], [1]],
            [[1], [2]],
        ]
    )

    encoded = trellis_encoder(data, dlt, slt)

    np.testing.assert_array_equal(encoded[:, :, 0], np.array([[10, 11], [22, 23], [20, 21]]))


def test_soft_outputs_and_ber_helpers():
    x = np.array([1 + 3j, -1 - 1j]) / np.sqrt(10)
    h = np.array([1 + 0j, 0.5 + 0.5j])

    assert soft_decision_sigma(x, h).shape == (8,)
    assert soft_output2x2(x).shape == (8,)

    assert ber(reset=True) == (0.0, 0, 0)
    assert ber(np.array([0, 3]), np.array([1, 1]), 2) == (0.5, 2, 4)

    awgn = ber_qam(np.array([0.0, 10.0]), 16, "AWGN")
    rayleigh = ber_qam(np.array([0.0, 10.0]), 16, "Rayleigh")
    assert awgn.shape == (2,)
    assert rayleigh.shape == (2,)
    assert awgn[1] < awgn[0]
    assert rayleigh[1] < rayleigh[0]


def test_modulate_carrier_baseband_shape_and_time():
    symbols = np.array([1 + 1j, -1 + 0j])

    signal, time = modulate_carrier(symbols, ts=1.0, nos=4, fc=1.0)

    assert signal.shape == (8,)
    assert time.shape == (8,)
    np.testing.assert_allclose(time[:4], np.array([0.0, 0.25, 0.5, 0.75]))
