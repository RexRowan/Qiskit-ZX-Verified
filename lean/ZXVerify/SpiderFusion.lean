/-
  SpiderFusion.lean

  Formal statement and proof of the ZX-calculus **spider fusion rule**,
  restricted to Clifford phases (multiples of π/2).

  ## The rule being verified

  In ZX-calculus, a degree-2 Z-spider with phase α is exactly a phase
  gate: the 2x2 diagonal matrix `diag(1, e^{iα})`. The spider fusion
  rule says that connecting two same-colored spiders and merging them
  adds their phases:

      spider(α) ∘ spider(β)  =  spider(α + β)

  For a degree-2 spider this is just phase-gate composition:

      diag(1, e^{iα}) · diag(1, e^{iβ})  =  diag(1, e^{i(α+β)})

  which reduces to a single scalar identity: `e^{iα} · e^{iβ} = e^{i(α+β)}`.

  ## Scope

  We verify this exactly for the 4 Clifford phases
  `α, β ∈ {0, π/2, π, 3π/2}`, represented as `Fin 4` (phase index `k`
  means angle `k * π/2`), using exact Gaussian-integer arithmetic (see
  `GInt.lean`) rather than floating point or Mathlib's `Real`/`Complex`.
  This is a real, checked, `sorry`-free proof -- not a numerical
  approximation -- but it is a proof about the Clifford fragment
  specifically, not the fully general continuous-phase rewrite rule.
  See `docs/scope.md` in the repository root for the honest picture of
  what is and isn't covered yet, and `docs/roadmap.md` for how this
  extends to general phases via Mathlib's `Complex` (a nontrivial but
  well-scoped follow-up: cos/sin instead of the Fin-4 lookup table below).
-/

import ZXVerify.GInt

namespace ZXVerify

open GInt

/-- The complex phase factor `e^{i k π/2}` for Clifford phase index `k`.
    This is exactly the cyclic group of 4th roots of unity, represented
    exactly as Gaussian integers (no rounding). -/
def phaseFactor : Fin 4 → GInt
  | 0 => (1 : GInt)
  | 1 => GInt.i
  | 2 => -(1 : GInt)
  | 3 => -GInt.i

/-- A degree-2 Z-spider with Clifford phase `k`, represented as its 2x2
    diagonal matrix `diag(1, e^{i k π/2})`. We represent a diagonal
    matrix just as the pair of its two diagonal entries, since off
    diagonal entries are always zero for this gate family and carrying
    them around adds nothing to the proof. -/
def spider (k : Fin 4) : GInt × GInt := ((1 : GInt), phaseFactor k)

/-- Composing (matrix-multiplying) two diagonal 2x2 matrices, given as
    diagonal-entry pairs, is just entrywise multiplication. -/
def composeDiag (a b : GInt × GInt) : GInt × GInt := (a.1 * b.1, a.2 * b.2)

/-- **Spider fusion, Clifford case.** Fusing two same-colored degree-2
    spiders with phases `j` and `k` gives a single spider with phase
    `j + k` (phase addition wraps mod 4, i.e. mod 2π, exactly matching
    `Fin 4`'s built-in addition). Verified by exhaustive case check over
    all 16 `(j, k)` pairs -- `decide` is sound here specifically because
    `Fin 4` is finite; see the note in `GInt.lean` about why this
    approach does not extend to general (non-Clifford) phases without
    switching representations. -/
theorem spider_fusion (j k : Fin 4) :
    composeDiag (spider j) (spider k) = spider (j + k) := by
  revert j k
  decide

/-- **Identity removal**, as a corollary: fusing with a phase-0 spider
    (the identity phase gate) changes nothing. This is the other classic
    ZX simplification rule -- a degree-2, phase-0 spider is exactly the
    identity wire and can always be deleted. -/
theorem spider_fusion_identity (k : Fin 4) :
    composeDiag (spider 0) (spider k) = spider k := by
  have h := spider_fusion 0 k
  simpa using h

/-- Sanity check that `spider_fusion` is not vacuously true: phase
    addition genuinely wraps around (3 + 2 = 1 mod 4, not 5), and the
    theorem holds through that wraparound too. This is exactly the case
    that would break a naive (non-modular) implementation. -/
example : (3 : Fin 4) + 2 = 1 := by decide

example : composeDiag (spider 3) (spider 2) = spider 1 := spider_fusion 3 2

end ZXVerify
