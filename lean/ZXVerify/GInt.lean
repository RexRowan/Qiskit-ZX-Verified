/-
  GInt.lean

  Exact arithmetic on Gaussian integers ℤ[i] = {a + bi : a, b ∈ ℤ}.

  Why Gaussian integers, not ℝ or ℂ? Formalizing the real/complex numbers
  requires Mathlib (Cauchy sequences, limits, etc.), which is a large
  dependency with a long build time. But the ZX-calculus rewrite rules we
  care about first -- spider fusion, identity removal -- are already
  *exactly* true, with no approximation, on the "Clifford fragment" of
  ZX diagrams, where every spider phase is a multiple of π/2. The complex
  phase factors that show up there are exactly the four fourth roots of
  unity {1, i, -1, -i}, which live inside ℤ[i] -- no real-number theory
  needed, no floating point, no `decide` timeouts from irrational
  arithmetic. This lets us get real, checked, zero-admitted-sorry proofs
  quickly, with a documented, honest scope: Clifford phases now, general
  continuous phases (which do need Mathlib's `Complex`) as a follow-up.
-/

structure GInt where
  re : Int
  im : Int
deriving DecidableEq, Repr

namespace GInt

instance : Add GInt := ⟨fun a b => ⟨a.re + b.re, a.im + b.im⟩⟩
instance : Neg GInt := ⟨fun a => ⟨-a.re, -a.im⟩⟩
instance : Sub GInt := ⟨fun a b => ⟨a.re - b.re, a.im - b.im⟩⟩

/-- Complex multiplication: (a+bi)(c+di) = (ac - bd) + (ad + bc)i -/
instance : Mul GInt := ⟨fun a b => ⟨a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re⟩⟩

instance : Zero GInt := ⟨⟨0, 0⟩⟩
instance : One GInt := ⟨⟨1, 0⟩⟩

/-- The imaginary unit. -/
def i : GInt := ⟨0, 1⟩

@[simp] theorem add_def (a b : GInt) : a + b = ⟨a.re + b.re, a.im + b.im⟩ := rfl
@[simp] theorem mul_def (a b : GInt) :
    a * b = ⟨a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re⟩ := rfl

theorem i_mul_i : i * i = -1 := by decide

end GInt
