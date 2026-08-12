# Contributing

## Setup

```bash
git clone https://github.com/RexRowan/qiskit-zx-verified.git
cd qiskit-zx-verified
pip install -e ".[dev]"
pytest tests/ -v

# Lean side
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
cd lean && lake build
```

## Before opening a PR

- **If you touch the Lean proof or the Python arithmetic it mirrors**,
  run `python scripts/extract_lean_certificate.py` and make sure it
  still reports a clean cross-check. The whole point of this project is
  that the two sides agree; a PR that makes them diverge silently is the
  one failure mode worth actively guarding against.
- **If you extend the certified phase set beyond Clifford** (see
  `docs/roadmap.md` item 1), update `docs/scope.md` to match -- it's
  meant to always be an accurate, current description of what's proved,
  not a snapshot of v0.1.
- Run `pytest tests/ -v` and `lake build` (from `lean/`) before pushing.
- New Lean theorems: check `#print axioms <theorem_name>` shows nothing
  beyond Lean's own trusted core axioms (`propext`, `Classical.choice`,
  `Quot.sound` are all fine; `sorryAx` means the proof is incomplete).

## Good first contributions

See `docs/roadmap.md` for a full list, roughly ordered by how naturally
each builds on the current proof. The most impactful single next step
is item 1 (general continuous phases via Mathlib's `Complex`) -- it's
mostly plumbing work (adding the Mathlib dependency, `lake exe cache
get`) rather than new mathematics, since the underlying fact
(`e^{i(a+b)} = e^{ia} e^{ib}`) is already in Mathlib as `Complex.exp_add`.

## Code style

Plain, readable Python; Lean proofs should stay `sorry`-free (no
partial/aspirational proofs merged as if complete) and each new theorem
should get a docstring-style comment explaining what it means physically,
not just what it states formally.
