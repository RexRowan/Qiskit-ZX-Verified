import Lake
open Lake DSL

package «zx-verify» where
  -- no extra config needed; this project deliberately has zero
  -- external dependencies (see GInt.lean for why) so `lake build`
  -- stays fast and doesn't require fetching Mathlib.

@[default_target]
lean_lib «ZXVerify» where
  roots := #[`ZXVerify.GInt, `ZXVerify.SpiderFusion]
