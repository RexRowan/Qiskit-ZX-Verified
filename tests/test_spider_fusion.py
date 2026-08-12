import pytest

from qiskit_zx.gaussian import GaussianInt, I, ONE, phase_factor
from qiskit_zx.spider_fusion import compose_diag, is_certified_clifford_fusion, spider


def test_i_squared_is_minus_one():
    assert I * I == GaussianInt(-1, 0)


def test_phase_factor_matches_fourth_roots_of_unity():
    assert phase_factor(0) == ONE
    assert phase_factor(1) == I
    assert phase_factor(2) == GaussianInt(-1, 0)
    assert phase_factor(3) == GaussianInt(0, -1)


def test_phase_factor_wraps_mod_4():
    assert phase_factor(4) == phase_factor(0)
    assert phase_factor(5) == phase_factor(1)
    assert phase_factor(-1) == phase_factor(3)


@pytest.mark.parametrize("j", range(4))
@pytest.mark.parametrize("k", range(4))
def test_spider_fusion_matches_lean_for_all_16_cases(j, k):
    # This is the exact same 16-case check the Lean `decide` tactic
    # performed at proof-checking time -- reproduced here in Python so a
    # regression in either implementation is caught by CI without needing
    # the Lean toolchain installed.
    assert compose_diag(spider(j), spider(k)) == spider((j + k) % 4)


def test_is_certified_clifford_fusion_always_true_in_range():
    for j in range(4):
        for k in range(4):
            assert is_certified_clifford_fusion(j, k)


def test_gaussian_int_matches_python_complex_for_clifford_phases():
    import cmath

    for k in range(4):
        exact = phase_factor(k).to_complex()
        approx = cmath.exp(1j * k * cmath.pi / 2)
        assert abs(exact - approx) < 1e-9
