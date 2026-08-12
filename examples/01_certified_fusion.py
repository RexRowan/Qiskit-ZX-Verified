"""Demonstrates the Lean-certified Clifford phase-gate fusion pass.

Shows: a certified fusion (all Clifford), an uncertified-but-still-correct
fusion (a T gate is involved), and exact-matrix verification that the
optimized circuit is really equivalent to the original.
"""

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
import numpy as np

from qiskit_zx import fuse_phase_gates


def main() -> None:
    print("=== Example 1: an all-Clifford run (S, S, Z) ===")
    qc1 = QuantumCircuit(1)
    qc1.s(0)
    qc1.s(0)
    qc1.z(0)
    result1 = fuse_phase_gates(qc1)
    print(result1.summary())
    print("Original:")
    print(qc1.draw())
    print("Fused (should have dropped entirely -- S*S*Z = 2pi = identity):")
    print(result1.circuit.draw() or "  (empty circuit)")

    print()
    print("=== Example 2: a run involving a non-Clifford T gate ===")
    qc2 = QuantumCircuit(1)
    qc2.s(0)
    qc2.t(0)
    result2 = fuse_phase_gates(qc2)
    print(result2.summary())
    print("Fused (correct, but honestly NOT Lean-certified):")
    print(result2.circuit.draw())

    print()
    print("=== Verifying exact equivalence for both ===")
    for name, orig, fused in [("Example 1", qc1, result1.circuit), ("Example 2", qc2, result2.circuit)]:
        op1 = Operator(orig)
        op2 = Operator(fused)
        print(f"{name}: exactly equal matrices = {np.allclose(op1.data, op2.data, atol=1e-12)}")


if __name__ == "__main__":
    main()
