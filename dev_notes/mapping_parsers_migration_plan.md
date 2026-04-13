# Mapping-Annotation Parser Migration Plan (Post-VASP Parity)

Detailed execution plan for the current parser electronic parity wave:
- `dev_notes/parser_electronic_parity_rollout_plan.md`

## Summary

Implement VASP-equivalent migration parity across **all mapping-annotation parsers** in `nomad-simulation-parsers`, with **full 3-area parity** (`model_system`, `model_method`, `outputs`) and **no new support beyond legacy-equivalent behavior**.
`gromacs` is explicitly excluded. Non-mapping parsers (`lammps`, `phonopy`) are out of scope.

## Legacy Baseline References (Required)

For every parser migration item, use the legacy plugin implementations below as the
code-side extraction baseline before finalizing mappings:

1. `/home/jfrudzinski/work/soft/plugins/electronic-parsers`
2. `/home/jfrudzinski/work/soft/plugins/atomistic-parsers`

Required rule:

1. Parser migration in `nomad-simulation-parsers` must preserve legacy-equivalent
	extraction outcomes from these repositories while implementing the new
	architecture (`mapping annotations` + `nomad-simulations`).
2. If behavior differs, document the delta in `dev_notes/MIGRATION_STATUS.md` and
	either align to legacy-equivalent behavior or mark an explicit justified TODO.

## Scope Guardrail (Primary Migration Tracks)

This parser plan must remain subordinate to the two primary migration tracks:

1. **Fundamental system quantities handled in normalizer**
- representative-system routing and normalization
- material/topology core fields needed downstream (cell, formulas, fractions, hierarchy)
- stable `archive.results` structural payload compatibility

2. **Outputs handled in normalizer**
- mapping from `archive.data.outputs` into legacy-equivalent `archive.results` payloads
- compatibility-safe references and serialization for downstream UI/consumers
- electronic and non-electronic outputs, within legacy-equivalent scope

Parser-wave work in this document is a supporting track to improve source payload
quality for those two normalizer tracks, not a replacement for them.

In-scope parser families:
- `abinit`, `ams`, `crystal`, `exciting`, `fhiaims`, `gpaw`, `octopus`, `quantumespresso` (`common` + `pwscf` + `gipaw` + `phonon`), `wannier90`, `yambo`, `h5md`, and `vasp` (regression guard only).

## Implementation Changes

### 0. Execution cadence and commit strategy

1. Implement changes **one parser at a time** (in the wave order below).
2. For each parser, complete implementation + validation gates before touching the next parser.
3. Keep all parser changes on the same branch and batch-commit at the end (user handles git/cherry-picking).
4. Record per-parser completion notes in `dev_notes/MIGRATION_STATUS.md` as work progresses.

### 1. Cross-parser migration contract (applies to every in-scope parser)

1. Add a per-parser parity checklist with three mandatory blocks:
- `model_system`: positions frame correctness, lattice vectors, PBC, atom/particle labels.
- `model_method`: legacy-equivalent DFT/method fields that feed results mapping (XC components/type ladder, self-consistency thresholds/units, basis/core treatment only if parser already supports them).
- `outputs`: legacy-equivalent physical outputs needed by current results mapping.

2. Enforce “legacy-equivalent only”:
- Only map quantities supported previously by legacy parser behavior for that code family.
- If unavailable in parser payload, leave unmapped and add concise TODO (no guessed defaults).

3. Standardize electronic outputs contract where applicable:
- `electronic_band_gaps`: direct parser value if available, else derived from eigenvalues+occupations.
- `electronic_dos`: require both DOS `value` and energy grid (`Energy2.points`) when DOS exists.
- `electronic_band_structures`: map `value`, plus `occupation`/spin where available.
- Normalize signed DOS channels when schema requires non-negative values.

### 2. Shared parser utility layer (avoid copy/paste)

Create shared helpers under parser utilities for reusable migration logic:
- eigenvalue payload normalization (spin/channel-shape normalization)
- band-gap derivation from eigenvalues+occupations
- DOS normalization (`energies`, `value`, spin handling, sign normalization)
- common mapper guard helpers (path presence, shape validity, unit-safe conversion)

All target parsers call these helpers instead of re-implementing logic locally.

### 3. Parser-wave implementation plan (decision-complete)

#### Wave A: Parsers already exposing DOS and/or band structures

Parsers: `abinit`, `crystal`, `exciting`, `fhiaims`, `wannier90`
Actions:
1. Ensure DOS mappings include `Energy2.points` (not just DOS values).
2. Add `electronic_band_gaps` mapping:
- use native parsed band-gap payload when present;
- fallback to derived gap from eigenvalues/band structures.
3. Ensure `electronic_band_structures` include occupations/spin metadata when available.
4. Fill model_system/method parity gaps only where parser payload already contains data.

#### Wave B: Eigenvalue-first parsers

Parsers: `ams`, `gpaw`, `octopus`, `quantumespresso` (`common` + `pwscf`), `yambo`
Actions:
1. Add explicit `electronic_band_structures` mapping from existing eigenvalue payloads when k-point structure exists.
2. Add `electronic_band_gaps` (native value first; derived fallback second).
- `ams`: map existing parsed band-gap payload directly first.
3. Add DOS mapping only when the parser currently exposes DOS in its own payload (otherwise leave TODO).
4. Complete model_system/method parity checks as in Wave A.

#### Wave C: Mapping parsers with non-electronic/domain-specific outputs

Parsers: `quantumespresso/gipaw`, `quantumespresso/phonon`, `h5md`
Actions:
1. Do full 3-area parity audit:
- confirm model_system and model_method mappings are sufficient for material/method population.
- confirm outputs align with current results-normalizer expectations for their domain.
2. Do **not** add electronic outputs unless legacy-equivalent support exists for that parser.
3. Add explicit no-op TODO notes for intentionally unmapped electronic groups.

#### Wave D: VASP regression guard

Parser: `vasp`
Actions:
1. Keep current VASP migration behavior as reference baseline.
2. Add/retain regression tests to ensure future shared-helper refactors do not regress VASP outputs/method/system parity.

## Public APIs / Interfaces / Types

1. No parser entry point names change.
2. No external plugin API changes.
3. Internal additions:
- shared helper module(s) for electronic-output migration logic;
- expanded schema mappings in parser schema packages (`outputs.Outputs.*`, `Energy2`, band-gap sections).
4. No changes to NOMAD results schema semantics; only parser-side population to existing targets.

## Test Plan

### Per-parser mandatory validation gate (must pass before moving to next parser)

1. Run parser-local tests for the parser under migration (`pytest` target + `ruff check` on touched files).
2. Run an end-to-end parse + topology/results normalization flow using the parser fixture(s) (or representative real sample when available).
3. Confirm previously assessed `results` targets are properly populated when source data exists:
- `results.material.topology[0]` chemistry/core fields (`elements`, `chemical_formula_*`, `elemental_composition`) and valid root structure metadata.
- `results.method.simulation.dft` core migrated fields (`basis_set_type`, `core_electron_treatment`, `scf_threshold_energy_change`, `jacobs_ladder`, `xc_functional_type`, `xc_functional_names`) where parser data supports them.
- `results.properties.electronic` sections (`band_gap`, `dos_electronic`, `band_structure_electronic`) for electronic parsers.
4. Confirm no unintended empty placeholder sections are created in `results` (e.g., empty electronic blocks).
5. Only after these checks pass, proceed to the next parser.

1. Upgrade parser tests from smoke-only to parity assertions for every in-scope parser test module:
- `model_system` assertions (positions/lattice/PBC/labels)
- `model_method` assertions (legacy-equivalent method fields when available)
- `outputs` assertions (counts + required fields for mapped outputs)
2. Add a new parser migration parity matrix test (parametrized) that checks, per parser:
- required vs optional outputs expected from fixtures
- absence of unsupported invented mappings
3. Add cross-package integration checks (selected fixtures per wave):
- parse with parser package
- run topology/results normalizer path
- assert mapped `results.properties`/`results.method`/material-critical fields are populated when source data exists
4. Keep parser-specific edge tests:
- spin-polarized DOS handling/sign normalization
- eigenvalue shape normalization
- missing-occupation band-gap fallback behavior
5. Required validation commands:
- parser package: targeted `pytest` modules for each touched parser + `ruff check`
- topology normalizer: `test_results_normalizer.py` plus any parser-driven integration tests

## Assumptions and Defaults

- Scope locked to **all mapping-annotation parsers except `gromacs`**.
- Migration target is **full 3-area parity** (`model_system`, `model_method`, `outputs`).
- Legacy-equivalence rule is strict: no new feature support beyond legacy behavior.
- If parser payload lacks required source data, leave unmapped + TODO (no synthetic defaults).
- `lammps` and `phonopy` are excluded as non-mapping parser paths.

## Mapping-Parser Implementation Guidelines

Hard rule for this migration:

1. Keep mapping logic as small as possible.
2. Prefer direct `add_mapping_annotation(...)` mappings by default.
3. Use helper functions only when direct mapping cannot express the transformation.
4. Helper functions must only extract/organize/normalize source data payloads.
5. Helper functions must not set NOMAD quantities or subsections directly.
6. Section/quantity assignment must happen only through mapping annotations.

1. Prefer direct annotation mappings whenever possible:
- Use direct `add_mapping_annotation(...)` paths over helper functions when source payload already matches the target field shape.

2. Keep helper-function use minimal and justified:
- Introduce helper functions only when direct mapping cannot express the required transformation.
- Keep helper logic narrow, deterministic, and as small as possible.

3. Helper functions must return structured mapping payloads only:
- Functions should prepare and return structured intermediate data for mapping annotations.
- Functions must not instantiate or populate NOMAD schema sections directly.

4. Preserve mapping-parser architecture boundaries:
- Data extraction and lightweight normalization happen in helper functions.
- Schema population happens only through mapping annotations and metainfo parser conversion.

5. Avoid introducing non-legacy logic during migration:
- Do not add new inferred behavior through helper functions.
- If direct legacy-equivalent mapping is unavailable, leave unmapped and add a concise TODO.
