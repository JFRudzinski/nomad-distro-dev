# Symmetry Migration Plan: v2-first, Legacy-Equivalent, No Double Normalization

## Summary

Current behavior is split and partially duplicated:
- `nomad-simulations` already performs rich bulk symmetry normalization on `ModelSystem` (`GlobalCrystalSymmetry`, `local_symmetry`, primitive/conventional representations).
- The topology normalizer v2 path still relies on legacy-shaped symmetry expectations and MatID recomputation in places.
- Legacy normalization (`nomad-FAIR` results/material/topology) expects cached MatID analyzer artifacts and older symmetry carriers.

Target architecture:
- Simulation plugin owns simulation-specific symmetry extraction/calculation.
- Topology/plugin side owns general-level normalization over abstract system data, consuming simulation symmetry when available.
- Elevation scope deferred: no shared extraction now; only future recommendations as TODOs.

## Implementation Changes

1. Introduce a general symmetry adapter layer (internal first, extraction-agnostic).
- Add a small internal adapter contract (normalized symmetry payload object) that can be populated from:
  - v2 `ModelSystem.symmetry` + `ModelSystem.local_symmetry` + analyzed representations
  - legacy symmetry carrier (`repr_symmetry`/cached analyzer path)
- Adapter outputs only legacy-equivalent fields needed downstream:
  - hall/point/space-group/bravais/crystal-system/prototype fields
  - normalized wyckoff payload for material-id generation
  - optional conventional/primitive cell geometry for topology/material

2. Refactor v2 topology/material path to consume simulation symmetry first.
- In v2 initialization, read representative system symmetry directly from `ModelSystem.symmetry` (not from `results.properties.structures.structure_original`).
- For bulk systems:
  - Prefer already-normalized primitive/conventional representations from `ModelSystem.representations`.
  - Use adapter-mapped symmetry payload to populate `results.material.symmetry` and topology `System.symmetry`.
- Keep MatID computation as strict fallback only when required symmetry inputs are missing/incomplete.

3. Define strict precedence to prevent double normalization.
- Precedence for v2:
  1. Existing simulation-normalized symmetry/representations
  2. Single general fallback computation in topology/material path
  3. Unset + TODO log (no invented support)
- Add explicit guard: if v2 symmetry payload is complete, do not call MatID-based symmetry recomputation in topology/material.
- Preserve legacy fallback branch unchanged.

4. Close legacy parity gaps for system-level symmetry fields only.
- Ensure `results.material.symmetry` field mapping covers all legacy-equivalent fields that are present in v2 source.
- Keep advanced v2-only symmetry details unmapped unless there is a direct legacy-equivalent target.
- Keep `material_id` generation algorithm legacy-compatible (same normalized symmetry string inputs and hashing behavior).

5. Deferred elevation (recommendations only, no implementation now).
- Add TODO recommendations on where mapping utilities could later be elevated.
- Keep all active implementation local to current plugins for this migration phase.

## Deferred Elevation TODOs (Recommendations Only)

- TODO: Consider elevating `symmetry_adapter` field mapping into a shared utility only after `nomad-simulations` and `nomad-FAIR` symmetry field names/stability are finalized.
- TODO: Define a shared `symmetry_data` contract (typed metainfo-oriented object) if at least two plugins consume the same canonical mapping logic.
- TODO: If elevation happens later, keep hashing/material-id generation semantics fully backward compatible with legacy `material_id_bulk` inputs.
- TODO: Add a cross-plugin parity fixture set (legacy vs v2 sources) before any elevation to prevent behavior drift.

## Test Plan

1. v2 consume-without-recompute
- Fixture with representative bulk `ModelSystem` already carrying `GlobalCrystalSymmetry`, local symmetry, and primitive/conventional representations.
- Assert material/topology symmetry and material-id are populated from consumed data.
- Assert MatID symmetry recomputation path is not invoked (mock/spy fail-fast).

2. v2 fallback-on-missing
- Fixture lacking complete simulation symmetry payload.
- Assert fallback computes required legacy-equivalent outputs once and populates material/topology symmetry.

3. legacy parity checks
- For matching bulk fixtures, compare key outputs from legacy and v2 paths:
  - `results.material.symmetry` core fields
  - `material_id`
  - topology conventional-cell symmetry core fields

4. non-bulk and partial data robustness
- Ensure no regressions for 1D/2D/unknown structural types and partial symmetry payloads.
- Assert no double-writing/overwriting when both source and fallback data exist.

## Assumptions and Defaults

- Keep legacy delegation behavior as-is for non-v2 entries.
- No new semantic support beyond legacy-equivalent results fields.
- Simulation plugin remains authoritative for simulation-specific symmetry extraction.
- General/topology layer may compute fallback symmetry only when required inputs are missing.
- Elevation is limited to TODO recommendations in this phase.
