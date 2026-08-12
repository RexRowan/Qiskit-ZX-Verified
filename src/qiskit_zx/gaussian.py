"""Exact Gaussian-integer arithmetic, mirroring ``lean/ZXVerify/GInt.lean``.

This module exists purely so the Python side of the codebase can perform
the *exact same* Clifford-phase arithmetic that the Lean proof checked,
with no floating point involved -- letting
:mod:`qiskit_zx.certified_fusion` certify a rewrite by literally
replaying the same finite computation Lean already verified, rather than
just "trusting" the Lean result from a distance.

If you change the arithmetic here, change ``GInt.lean`` to match (and
vice versa) -- ``tests/test_gaussian.py`` cross-checks the two against
each other via the Lean extraction pipeline (see
``scripts/extract_lean_certificate.py``).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GaussianInt:
    """An element of the Gaussian integers ``Z[i] = {a + bi : a, b in Z}``."""

    re: int
    im: int

    def __add__(self, other: "GaussianInt") -> "GaussianInt":
        return GaussianInt(self.re + other.re, self.im + other.im)

    def __neg__(self) -> "GaussianInt":
        return GaussianInt(-self.re, -self.im)

    def __sub__(self, other: "GaussianInt") -> "GaussianInt":
        return self + (-other)

    def __mul__(self, other: "GaussianInt") -> "GaussianInt":
        return GaussianInt(
            self.re * other.re - self.im * other.im,
            self.re * other.im + self.im * other.re,
        )

    def to_complex(self) -> complex:
        """Exact conversion to a Python complex (Gaussian integers embed exactly)."""
        return complex(self.re, self.im)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"({self.re}+{self.im}i)"


ZERO = GaussianInt(0, 0)
ONE = GaussianInt(1, 0)
I = GaussianInt(0, 1)  # noqa: E741 - matches Lean's `GInt.i`


def phase_factor(k: int) -> GaussianInt:
    """``e^{i k pi/2}`` for Clifford phase index ``k`` (mod 4).

    Exactly mirrors ``ZXVerify.phaseFactor`` in ``SpiderFusion.lean``:
    a lookup table over the 4 fourth roots of unity, not a floating-point
    ``cmath.exp`` call, so there is zero rounding error to reason about.
    """
    table = {0: ONE, 1: I, 2: -ONE, 3: -I}
    return table[k % 4]
