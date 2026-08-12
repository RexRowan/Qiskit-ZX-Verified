"""A Qiskit-native phase-gate fusion pass, certified against Lean where possible.

Fuses runs of consecutive single-qubit phase-family gates (``P``, ``Z``,
``S``, ``Sdg``, ``T``, ``Tdg``) acting on the same qubit into a single
``PhaseGate``. Whenever *every* gate in a fused run has a Clifford angle
(a multiple of pi/2), the fusion is additionally checked against
:func:`qiskit_zx.spider_fusion.is_certified_clifford_fusion` -- i.e.
against the exact computation the Lean proof in
``lean/ZXVerify/SpiderFusion.lean`` checked -- and the returned
:class:`FusionResult` records that fact. Runs involving a non-Clifford
angle (e.g. a lone ``T`` gate, angle pi/4) are still fused correctly
(ordinary phase addition is just correct, Lean-certified or not), but
are honestly reported as *not* Lean-certified.

See ``docs/scope.md`` for why the certification currently stops at
Clifford angles.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit.circuit.library import PhaseGate

from .spider_fusion import is_certified_clifford_fusion

_ANGLE_TOLERANCE = 1e-9

# Fixed angles for the standard named phase-family gates, in radians.
_NAMED_GATE_ANGLES = {
    "z": math.pi,
    "s": math.pi / 2,
    "sdg": -math.pi / 2,
    "t": math.pi / 4,
    "tdg": -math.pi / 4,
}


def _gate_angle(instruction: Instruction) -> Optional[float]:
    """Return the phase angle for a phase-family gate, or ``None`` if not one."""
    name = instruction.name
    if name == "p":
        return float(instruction.params[0])
    if name in _NAMED_GATE_ANGLES:
        return _NAMED_GATE_ANGLES[name]
    return None


def _clifford_index(angle: float) -> Optional[int]:
    """Map an angle to a Clifford phase index 0..3, or ``None`` if not Clifford."""
    normalized = angle % (2 * math.pi)
    quarter = normalized / (math.pi / 2)
    nearest = round(quarter)
    if abs(quarter - nearest) < _ANGLE_TOLERANCE / (math.pi / 2):
        return nearest % 4
    return None


@dataclass
class FusedRun:
    """One fused run of phase gates on a single qubit."""

    qubit_index: int
    original_gate_count: int
    total_angle: float
    lean_certified: bool
    clifford_indices: Optional[List[int]] = None


@dataclass
class FusionResult:
    """Result of running :func:`fuse_phase_gates` on a circuit."""

    circuit: QuantumCircuit
    fused_runs: List[FusedRun] = field(default_factory=list)

    @property
    def certified_fusions(self) -> int:
        return sum(1 for r in self.fused_runs if r.lean_certified and r.original_gate_count > 1)

    @property
    def uncertified_fusions(self) -> int:
        return sum(
            1 for r in self.fused_runs if not r.lean_certified and r.original_gate_count > 1
        )

    def summary(self) -> str:
        total = sum(1 for r in self.fused_runs if r.original_gate_count > 1)
        return (
            f"{total} run(s) fused "
            f"({self.certified_fusions} Lean-certified, "
            f"{self.uncertified_fusions} not certified -- non-Clifford angle involved)."
        )


def fuse_phase_gates(circuit: QuantumCircuit) -> FusionResult:
    """Fuse consecutive same-qubit phase-family gates in ``circuit``.

    Non-phase gates act as barriers that end a run: a run is a maximal
    sequence of phase-family gates on one qubit with nothing else (on
    that qubit) in between.
    """
    new_circuit = circuit.copy_empty_like()
    fused_runs: List[FusedRun] = []

    # Track, per-qubit, the angles of the currently-open run and where it
    # started in the new circuit's instruction stream isn't needed since
    # we append lazily: buffer per-qubit angles, flush on interruption.
    pending: dict = {}  # qubit_index -> list[float]

    def flush(qubit_index: int) -> None:
        angles = pending.pop(qubit_index, [])
        if not angles:
            return
        indices = [_clifford_index(a) for a in angles]
        all_clifford = all(i is not None for i in indices)
        total_angle = sum(angles) % (2 * math.pi)

        certified = False
        if all_clifford:
            # Replay the exact pairwise reduction the Lean proof covers:
            # fold left, checking certification at every step.
            acc = indices[0]
            certified = True
            for idx in indices[1:]:
                if not is_certified_clifford_fusion(acc, idx):
                    certified = False  # pragma: no cover - would indicate a bug
                    break
                acc = (acc + idx) % 4

        fused_runs.append(
            FusedRun(
                qubit_index=qubit_index,
                original_gate_count=len(angles),
                total_angle=total_angle,
                lean_certified=certified,
                clifford_indices=indices if all_clifford else None,
            )
        )
        if len(angles) == 1 or abs(total_angle) > _ANGLE_TOLERANCE:
            new_circuit.append(PhaseGate(total_angle), [new_circuit.qubits[qubit_index]])
        # else: total angle is (numerically) the identity -- drop it entirely.

    for instruction in circuit.data:
        op = instruction.operation
        qubits = instruction.qubits
        angle = _gate_angle(op) if len(qubits) == 1 else None

        if angle is not None:
            qidx = circuit.find_bit(qubits[0]).index
            pending.setdefault(qidx, []).append(angle)
            continue

        # Non-phase-gate instruction: flush any open runs on the qubits it touches.
        for q in qubits:
            flush(circuit.find_bit(q).index)
        new_circuit.append(op, qubits, instruction.clbits)

    for qidx in list(pending.keys()):
        flush(qidx)

    return FusionResult(circuit=new_circuit, fused_runs=fused_runs)
