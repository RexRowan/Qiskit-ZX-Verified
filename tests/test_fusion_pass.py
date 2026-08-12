import math

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from qiskit_zx import fuse_phase_gates


def assert_exactly_equivalent(qc1: QuantumCircuit, qc2: QuantumCircuit) -> None:
    """Assert two circuits implement the identical unitary -- not just
    equivalent up to global phase, but exactly equal matrices. Phase
    gates carry no ambiguous global phase, so exact equality is the
    right (and strongest available) check here.
    """
    op1 = Operator(qc1)
    op2 = Operator(qc2)
    assert np.allclose(op1.data, op2.data, atol=1e-10)


def test_clifford_run_is_certified_and_exactly_equivalent():
    qc = QuantumCircuit(1)
    qc.s(0)
    qc.s(0)  # S*S = Z
    result = fuse_phase_gates(qc)
    assert result.certified_fusions == 1
    assert result.uncertified_fusions == 0
    assert_exactly_equivalent(qc, result.circuit)


def test_full_clifford_cycle_cancels_to_identity():
    # S^4 = identity; four Clifford quarter-turns should fuse away entirely.
    qc = QuantumCircuit(1)
    for _ in range(4):
        qc.s(0)
    result = fuse_phase_gates(qc)
    assert len(result.circuit.data) == 0
    assert_exactly_equivalent(qc, result.circuit)


def test_non_clifford_gate_is_not_certified_but_still_correct():
    qc = QuantumCircuit(1)
    qc.t(0)  # angle pi/4, not a multiple of pi/2
    result = fuse_phase_gates(qc)
    assert result.certified_fusions == 0
    # A single gate isn't really a "fusion" (nothing to fuse with), so it
    # shouldn't be reported as an uncertified fusion either.
    assert result.uncertified_fusions == 0
    assert_exactly_equivalent(qc, result.circuit)


def test_mixed_clifford_and_non_clifford_run_is_not_certified():
    qc = QuantumCircuit(1)
    qc.s(0)
    qc.t(0)  # breaks the all-Clifford property of the run
    result = fuse_phase_gates(qc)
    assert result.uncertified_fusions == 1
    assert result.certified_fusions == 0
    assert_exactly_equivalent(qc, result.circuit)


def test_two_qubit_gate_ends_a_run():
    qc = QuantumCircuit(2)
    qc.s(0)
    qc.s(0)
    qc.cx(0, 1)
    qc.z(0)
    result = fuse_phase_gates(qc)
    # Two separate runs on qubit 0, split by the cx.
    assert len(result.fused_runs) == 2
    assert_exactly_equivalent(qc, result.circuit)


def test_independent_qubits_do_not_interfere():
    qc = QuantumCircuit(2)
    qc.s(0)
    qc.s(0)
    qc.t(1)
    qc.t(1)
    result = fuse_phase_gates(qc)
    assert_exactly_equivalent(qc, result.circuit)


@pytest.mark.parametrize("num_gates", [1, 2, 3, 5, 8])
def test_random_clifford_runs_are_always_certified_and_correct(num_gates):
    import random

    rng = random.Random(num_gates)
    qc = QuantumCircuit(1)
    clifford_names = ["s", "sdg", "z"]
    for _ in range(num_gates):
        name = rng.choice(clifford_names)
        getattr(qc, name)(0)
    result = fuse_phase_gates(qc)
    assert result.uncertified_fusions == 0
    assert_exactly_equivalent(qc, result.circuit)


def test_p_gate_arbitrary_angle_still_correct_but_uncertified():
    qc = QuantumCircuit(1)
    qc.p(0.37, 0)  # not a multiple of pi/2
    qc.p(1.1, 0)
    result = fuse_phase_gates(qc)
    assert result.uncertified_fusions == 1
    assert_exactly_equivalent(qc, result.circuit)


def test_empty_circuit():
    qc = QuantumCircuit(1)
    result = fuse_phase_gates(qc)
    assert len(result.fused_runs) == 0
    assert_exactly_equivalent(qc, result.circuit)
