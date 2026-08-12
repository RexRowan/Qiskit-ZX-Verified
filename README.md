# qiskit-zx-verified

A Clifford phase-gate fusion pass for [Qiskit](https://www.ibm.com/quantum/qiskit),
where the core rewrite rule is **formally verified in Lean 4** -- not
tested, not benchmarked against known cases, but machine-checked with a
`sorry`-free, `#print axioms`-clean proof.

This is a first, deliberately small step toward a longer-term goal:
bringing formally verified ZX-calculus rewriting into the Qiskit
ecosystem, distinct from [PyZX](https://github.com/Quantomatic/pyzx)
both in license (Apache 2.0, not GPL -- PyZX's GPL license is the
documented reason ZX-calculus tooling has never been integrated
natively into Qiskit) and in what "correct" means: here, correctness of
the core rule isn't just tested, it's proved.

**Read [`docs/scope.md`](docs/scope.md) before assuming this covers more
than it does.** The short version: one rewrite rule (spider fusion),
proved exactly for Clifford phases (multiples of pi/2), with an honest,
checked distinction in the code between "this specific fusion is
Lean-certified" and "this fusion is just ordinary correct arithmetic."
See [`docs/roadmap.md`](docs/roadmap.md) for how the scope grows from
here (general phases, multi-legged spiders, more rewrite rules).

## What's here

| Path | What it is |
|---|---|
| `lean/ZXVerify/GInt.lean` | Exact Gaussian-integer arithmetic (no Mathlib dependency -- see the file for why). |
| `lean/ZXVerify/SpiderFusion.lean` | The proved theorem: `spider_fusion`, verified by exhaustive case check over all 16 Clifford-phase pairs. |
| `src/qiskit_zx/spider_fusion.py` | Python transliteration of the same computation Lean checked, used to certify individual rewrites. |
| `src/qiskit_zx/fusion_pass.py` | The Qiskit-facing pass: fuses runs of phase-family gates (`P`, `Z`, `S`, `Sdg`, `T`, `Tdg`), reporting which fusions are Lean-certified. |
| `scripts/extract_lean_certificate.py` | Runs Lean's `#eval` on the full 16-case table and diffs it against Python's independently-computed table -- the actual Python <-> Lean bridge. |

## Installation

### Python package

```bash
git clone https://github.com/RexRowan/qiskit-zx-verified.git
cd qiskit-zx-verified
pip install -e ".[dev]"
```

Requires Python >= 3.9, Qiskit >= 2.0, < 3.

### Lean toolchain (only needed to re-check or extend the proof)

```bash
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
cd lean
lake build
```

This project has **zero external Lean dependencies** (no Mathlib) by
design, so `lake build` is fast -- seconds, not the many minutes a
Mathlib-dependent project needs for its first build.

## Quickstart

```python
from qiskit import QuantumCircuit
from qiskit_zx import fuse_phase_gates

qc = QuantumCircuit(1)
qc.s(0)
qc.s(0)
qc.z(0)   # S . S . Z = 2*pi = identity

result = fuse_phase_gates(qc)
print(result.summary())
# "1 run(s) fused (1 Lean-certified, 0 not certified -- non-Clifford angle involved)."

print(result.circuit.draw())   # empty -- the whole run canceled to identity
```

Fusions involving a non-Clifford angle (e.g. a `T` gate, phase pi/4)
are still applied correctly -- ordinary real-number phase addition is
just true -- but honestly reported as **not** Lean-certified:

```python
qc2 = QuantumCircuit(1)
qc2.s(0)
qc2.t(0)
result2 = fuse_phase_gates(qc2)
print(result2.summary())
# "1 run(s) fused (0 Lean-certified, 1 not certified -- non-Clifford angle involved)."
```

See [`examples/`](examples/) for runnable scripts and
[`docs/`](docs/) for the full picture.

## Verifying the proof yourself

```bash
cd lean
lake build
echo 'import ZXVerify.SpiderFusion
#print axioms ZXVerify.spider_fusion' > /tmp/check.lean
LEAN_PATH="$(pwd)/.lake/build/lib/lean" lean /tmp/check.lean
```

Expected output: `'ZXVerify.spider_fusion' depends on axioms: [propext]`
-- `propext` is one of Lean's own trusted core axioms, not something
this project added; there is no `sorryAx` in the list.

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v                              # 34 tests
python scripts/extract_lean_certificate.py    # cross-checks Python against Lean
```

## License

Apache 2.0. See [LICENSE](LICENSE). (Deliberately not GPL -- see the
project description above for why that matters here specifically.)

## References

- Coecke, B. & Duncan, R. (2011). "Interacting quantum observables:
  categorical algebra and diagrammatics." *New Journal of Physics*,
  13(4), 043016. (Original ZX-calculus rewrite rules, including spider
  fusion.)
- van de Wetering, J. (2020). "ZX-calculus for the working quantum
  computer scientist." *arXiv:2012.13966*. (Accessible modern survey.)
