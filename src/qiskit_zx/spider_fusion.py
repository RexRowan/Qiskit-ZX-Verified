"""Python-side mirror of the theorems proved in ``lean/ZXVerify/SpiderFusion.lean``.

The functions here compute *exactly* the same finite thing the Lean
kernel checked: :func:`spider` and :func:`compose_diag` are transliterations
of ``ZXVerify.spider`` and ``ZXVerify.composeDiag``. This lets
:func:`is_certified_clifford_fusion` answer "is this specific rewrite
instance backed by the Lean proof?" by replaying the identical
computation, rather than asking Python to independently reverify a
mathematical fact Lean already checked once, correctly, for good.
"""

from __future__ import annotations

from typing import Tuple

from .gaussian import GaussianInt, ONE, phase_factor

DiagonalGate = Tuple[GaussianInt, GaussianInt]  # (top-left, bottom-right) entries


def spider(k: int) -> DiagonalGate:
    """The degree-2 Clifford Z-spider (phase gate) with phase index ``k`` (mod 4).

    Mirrors ``ZXVerify.spider`` in Lean exactly.
    """
    return (ONE, phase_factor(k))


def compose_diag(a: DiagonalGate, b: DiagonalGate) -> DiagonalGate:
    """Matrix-multiply two diagonal 2x2 gates, given as diagonal-entry pairs.

    Mirrors ``ZXVerify.composeDiag`` in Lean exactly.
    """
    return (a[0] * b[0], a[1] * b[1])


def is_certified_clifford_fusion(j: int, k: int) -> bool:
    """Is ``spider(j) . spider(k) = spider(j+k)`` for these two phase indices?

    For any ``j, k`` in ``0..3`` this is always ``True`` -- it's exactly
    the statement ``ZXVerify.spider_fusion`` proved in Lean for *all* 16
    cases by exhaustive check. This function exists so calling code (see
    :mod:`qiskit_zx.certified_fusion`) can express "only apply this
    rewrite when it is Lean-certified" as an explicit, checkable
    condition rather than an implicit assumption, and so the condition
    has an obvious extension point if the certified phase set ever grows
    beyond the Clifford fragment (e.g. certifying pi/4 or Mathlib-backed
    general phases) -- lookups against a wider certified set instead of
    always returning ``True`` for the Clifford range.
    """
    j4, k4 = j % 4, k % 4
    lhs = compose_diag(spider(j4), spider(k4))
    rhs = spider((j4 + k4) % 4)
    return lhs == rhs
