"""qiskit-zx-verified: a Clifford phase-gate fusion pass for Qiskit,
with the core rewrite rule formally verified in Lean 4.

See ``lean/ZXVerify/SpiderFusion.lean`` for the proof and
``docs/scope.md`` for exactly what is and isn't covered.
"""

from .fusion_pass import FusedRun, FusionResult, fuse_phase_gates
from .gaussian import GaussianInt
from .spider_fusion import compose_diag, is_certified_clifford_fusion, spider

__version__ = "0.1.0"

__all__ = [
    "fuse_phase_gates",
    "FusionResult",
    "FusedRun",
    "GaussianInt",
    "spider",
    "compose_diag",
    "is_certified_clifford_fusion",
    "__version__",
]
