# Full Migration to `nomad-simulations` in `nomad-topology-normalizer`

## Summary

- Current package status is clean on `main` (`d51edb2`), with recent fixes for nested `SystemV2` routing and root topology cell/atoms.
- v2 execution is still partial: routing is migrated, but material/method/results population is not fully migrated to `nomad-simulations`.
- Keep both v2 inputs (`Simulation.model_system` and direct `basesections.v2.System`) and keep legacy fallback delegation for non-v2 entries.

## Implementation Changes

1. Refactor the v2 pipeline in `results.py` to explicitly run:
   representative selection -> material normalization -> method normalization -> topology normalization -> supported properties mapping.
2. Keep `_normalize_with_legacy()` as the only non-v2 path and stop using run-schema-style logic in the v2 path (`archive.run`, `section_run`, `m_cache` assumptions).
3. Rewrite representative selection in `normalizer.py` to always return a `ModelSystem`/`SystemV2` (fix workflow-based selection bug and remove noisy warning behavior for direct `SystemV2` entries).
4. Migrate `material.py` to v2-native inputs so it populates `results.material` from `ModelSystem`/`SystemV2` data (formula, dimensionality, structural type, building block, symmetry/material-id when available) without relying on run caches.
5. Migrate `method.py` to read from `Simulation.program`, `model_method`, and workflow refs instead of `archive.run`, with first-class support for DFT/TB/GW/BSE/DMFT mapping into `results.method`.
6. Complete topology v2 enrichment in `topology.py`: preserve current waterfall, keep direct `SystemV2` fallback, and extend node info population (`n_atoms`, formulas, atomic/mass fractions, cell, atom payload where schema-compatible) without reintroducing invalid `atoms_ref` typing.
7. Add a v2 properties mapper from `Simulation.outputs` for currently available properties (band gap, band structure, DOS, eigenvalues, greens functions, key thermo/mechanical fields when present), and leave unavailable quantities explicitly unset with clear TODO logs.

## Public Interfaces and Contracts

- Keep plugin entry point names unchanged.
- Keep `ResultsNormalizerBase` routing contract unchanged externally, but make v2 branch fully self-contained and no longer dependent on legacy-normalizer internals.
- Keep support for both v2 flavors: simulation-style and direct `SystemV2`.
- Keep legacy delegation behavior for non-v2 entries.

## Test Plan

1. Replace duplicated/stale topology tests with one authoritative suite (remove overlap between `test_topology_normalizer.py` and `test_normalizer.py`).
2. Add representative-selection regression tests (workflow ref path, representative index path, direct `SystemV2` path).
3. Add v2 material tests that assert actual populated `results.material` fields, not just no-crash.
4. Add v2 method tests for DFT/TB/GW/DMFT minimal mappings from `model_method`.
5. Extend topology tests for root/subsystem contracts (`cell`, formulas, fractions, hierarchy, direct `SystemV2` import path).
6. Add v2 outputs-to-results tests for mapped properties and explicit "unsupported property remains unset" checks.
7. Validate full fixture routing (`first.archive.yaml`, `second.archive.yaml`, `test.archive.yaml`) and keep legacy delegation assertions.
8. Run package tests in an isolated environment with consistent plugin deps (the current workspace has a broken `nomad-utility-workflows` install causing collection failure).

## Assumptions

- Legacy fallback remains in this plugin and is not removed.
- "Full migration" here means all active module logic (`results/material/method/topology`) uses `nomad-simulations`/v2 schema, not run-schema internals.
- Scope constraint: v2 migration must only carry over functionality that already exists in legacy normalization behavior. Do not introduce new `results.*` support paths that have no direct legacy equivalent.
- Mapping rule: when no direct legacy-equivalent target exists in current `nomad-FAIR` results schema, leave the value unmapped and log a concise TODO instead of introducing semantic fallbacks.
- Unsupported v2 properties (for example fields not yet available in `nomad-simulations`) are documented and intentionally left unmapped until upstream schema support exists.
- Final cleanup task: remove transitional `v2`-specific naming from internal helpers/comments once migration is complete.

## Closeout Status (2026-03-24)

### Completed

1. v2 routing and legacy fallback separation is active in `ResultsNormalizerBase`:
   - simulation/direct-System entries use data-schema path
   - non-simulation custom data uses legacy fallback path
2. `results.material` migration is in place for v2 representative systems:
   - formula/structural metadata from `ModelSystem`
   - symmetry transfer prefers simulation symmetry and falls back only when incomplete
3. Symmetry migration slice completed:
   - adapter layer introduced and integrated
   - bulk topology/material symmetry now prefers simulation-provided symmetry
   - MatID usage constrained to fallback scenarios
4. `results.method` v2 mapping in place for legacy-equivalent method families:
   - DFT, TB, GW, BSE, DMFT populated from `Simulation.model_method`
   - DFT spin/jacobs-ladder transfer added with enum-compatible mapping
   - single `results.method.method_name` now intentionally uses first supported model method
5. v2 outputs-to-results mapping implemented for supported legacy-equivalent properties.
6. Transitional internal helper naming cleanup performed in `results.py`.
7. Topology test overlap reduced:
   - routing tests remain in `test_results_normalizer.py`
   - topology content behavior is kept authoritative in `test_topology_normalizer.py`

### Validation Snapshot

- Full package tests: `47 passed, 1 skipped`.
- Fixture routing checks (`test/archive`, `first.archive.yaml`, `second.archive.yaml`):
  - `test.archive.yaml`: results present, no material/topology (expected for non-structural fixture)
  - `first.archive.yaml`: results present, no material/topology (legacy non-simulation path)
  - `second.archive.yaml`: results material present, topology length `5` (direct `SystemV2` path)

### Deferred / Intentional Follow-up

1. Multi-method search model redesign:
   - keep single `results.method.method_name` for now
   - defer multi-method headline/search semantics to results/search app redesign
2. Possible future elevation of symmetry mapping utilities remains recommendation-only (no shared-tool implementation in this phase).
