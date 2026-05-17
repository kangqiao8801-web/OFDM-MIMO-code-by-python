import numpy as np

from ofdm_mimo.utils import (
    assign_offset,
    branch_metric,
    compare_vector_norm,
    db2w,
    deci2bin,
    equalpower_subray,
    exp_pdp,
    gen_filter,
    gen_phase,
    interpolate,
    list_length,
    qfunc,
    sort_matrix,
    stage_processing1,
    vector_comparison,
    zero_insertion,
    zero_padding,
)


def test_basic_numeric_helpers_match_matlab_semantics():
    np.testing.assert_allclose(qfunc(np.array([0.0])), np.array([0.5]))
    np.testing.assert_allclose(db2w(np.array([0.0, 10.0])), np.array([1.0, 10.0]))
    np.testing.assert_array_equal(deci2bin([1, 2, 3], 2), np.array([0, 1, 1, 0, 1, 1]))
    np.testing.assert_array_equal(deci2bin([1, 2, 3], 2, kc=1), np.array([1, 1, 0, 1, 1]))


def test_zero_padding_insertion_interpolate_and_pdp():
    x = np.array([[1, 2, 3]])
    np.testing.assert_array_equal(zero_insertion(x, 3), np.array([[1, 0, 0, 2, 0, 0, 3, 0, 0]]))
    np.testing.assert_array_equal(zero_padding(np.array([1, 2, 3, 4]), 2), np.array([1, 2, 0, 0, 3, 4]))

    h = interpolate(np.array([1, 3]), np.array([2, 4]), 5, "linear")
    np.testing.assert_allclose(h, np.array([0, 1, 2, 3, 4]))

    pdp = exp_pdp(1e-6, 0.25e-6, -10, True)
    assert pdp.ndim == 1
    np.testing.assert_allclose(np.sum(pdp), 1.0)


def test_angle_phase_and_filter_helpers_are_finite():
    np.testing.assert_allclose(equalpower_subray(2)[:2], np.array([0.0894, 0.2826]))
    offsets = assign_offset(np.array([10, 20]), 2)
    assert offsets.shape == (2, 20)
    np.testing.assert_allclose(offsets[0, :2], np.array([10.0894, 9.9106]))

    bs, ms, phi = gen_phase(0, 2, np.array([10, 20]), 0, 5, np.array([30, 40]), rng=np.random.default_rng(0))
    assert bs.shape == (2, 20)
    assert ms.shape == (2, 20)
    assert phi.shape == (2, 20)

    filt = gen_filter(50, 100, 128, 2, "flat")
    assert filt.shape == (128,)
    np.testing.assert_allclose(np.sum(filt**2), 1.0)


def test_detection_support_helpers():
    sig = np.array([[1 + 1j, 2 + 0j]])
    q_test = np.array([[1, 0], [0, 1]], dtype=complex)
    ch = np.eye(2, dtype=complex)
    np.testing.assert_allclose(branch_metric(sig, q_test, ch), np.array([5.0, 3.0]))

    sorted_values, sorted_indices = sort_matrix(np.array([[3, 1], [2, 4]]))
    np.testing.assert_array_equal(sorted_values, np.array([1, 2, 3, 4]))
    np.testing.assert_array_equal(sorted_indices, np.array([[1, 0], [0, 1], [0, 0], [1, 1]]))

    assert list_length([1, 2, 0, 4]) == 2
    assert vector_comparison([1, 2], [1, 2]) == 1
    assert vector_comparison([1, 2], [1, 3]) == 0


def test_stateful_detector_helpers_have_explicit_python_inputs():
    flag, transition, x_list, metric, x_pre, x_now = compare_vector_norm(
        1,
        np.zeros((2, 4)),
        np.array([1, 1]),
        np.array([1, 1]),
        np.array([0, 0]),
        np.eye(2),
        4,
    )
    assert flag == 1
    assert transition == 4
    assert x_list.shape == (2, 4)
    assert metric == 4

    replica = np.zeros((2, 2, 2), dtype=int)
    out = stage_processing1(
        replica,
        1,
        np.array([-1, 1]),
        np.eye(2),
        np.array([0, 0]),
        nt=2,
        m_param=2,
    )
    assert out.shape == (2, 2, 2)
