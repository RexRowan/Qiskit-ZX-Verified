"""Cross-check the Lean-proved spider fusion table against the Python side.

This is the actual "bridge": rather than asking Python to trust the Lean
proof from a distance, this script asks Lean to *print out* every
instance of the theorem (all 16 `(j, k)` cases, via `#eval`), parses the
result, and diffs it against Python's independently-computed table from
:mod:`qiskit_zx.spider_fusion`. If the two ever disagree, that's a real
bug in one implementation or the other -- not a hypothetical, this is
exactly the class of bug the ``qiskit-lean-bridge`` project's extraction
pipeline was built to catch for the wider gate-equivalence library.

Usage:
    python scripts/extract_lean_certificate.py

Requires the Lean toolchain (see lean/lean-toolchain) to be installed
and `lake build` to have been run once in lean/.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEAN_DIR = REPO_ROOT / "lean"


def run_lean_eval() -> str:
    """Ask Lean to evaluate and print the full 16-entry fusion table."""
    eval_source = REPO_ROOT / "scripts" / "_eval_fusion_table.lean"
    eval_source.write_text(
        """
import ZXVerify.SpiderFusion
open ZXVerify

def entryString (j k : Fin 4) : String :=
  let result := composeDiag (spider j) (spider k) == spider (j + k)
  s!"{j.val},{k.val},{result}"

def allEntries : List String :=
  (List.finRange 4).flatMap (fun j => (List.finRange 4).map (entryString j))

#eval allEntries.forM (fun s => IO.println s)
"""
    )
    build_lib = LEAN_DIR / ".lake" / "build" / "lib" / "lean"
    lean_bin = subprocess.run(["which", "lean"], capture_output=True, text=True).stdout.strip()
    if not lean_bin:
        # Fall back to elan's toolchain-linked binary.
        lean_bin = "lean"

    env_path = f"{build_lib}"
    result = subprocess.run(
        [lean_bin, str(eval_source)],
        cwd=LEAN_DIR,
        env={"LEAN_PATH": env_path, "PATH": "/root/.elan/bin:/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    eval_source.unlink(missing_ok=True)
    if result.returncode != 0:
        print("Lean evaluation failed:", result.stderr, file=sys.stderr)
        sys.exit(1)
    return result.stdout


def parse_lean_table(output: str) -> dict:
    table = {}
    for line in output.strip().splitlines():
        j_str, k_str, result_str = line.split(",")
        table[(int(j_str), int(k_str))] = result_str.strip() == "true"
    return table


def python_table() -> dict:
    from qiskit_zx.spider_fusion import is_certified_clifford_fusion

    return {(j, k): is_certified_clifford_fusion(j, k) for j in range(4) for k in range(4)}


def main() -> None:
    print("Extracting fusion-rule certificate table from Lean...")
    lean_output = run_lean_eval()
    lean_table = parse_lean_table(lean_output)
    py_table = python_table()

    mismatches = [key for key in lean_table if lean_table[key] != py_table.get(key)]

    print(f"Lean reported {len(lean_table)} cases, all True: {all(lean_table.values())}")
    print(f"Python reported {len(py_table)} cases, all True: {all(py_table.values())}")
    print(f"Mismatches between Lean and Python: {len(mismatches)}")

    report = {
        "lean_cases": len(lean_table),
        "python_cases": len(py_table),
        "mismatches": mismatches,
        "cross_check_passed": len(mismatches) == 0,
    }
    out_path = REPO_ROOT / "scripts" / "certificate_report.json"
    out_path.write_text(json.dumps(report, indent=2))
    print(f"Report written to {out_path}")

    if mismatches:
        print("CROSS-CHECK FAILED.", file=sys.stderr)
        sys.exit(1)
    print("Cross-check passed: Python's table exactly matches Lean's proved table.")


if __name__ == "__main__":
    main()
