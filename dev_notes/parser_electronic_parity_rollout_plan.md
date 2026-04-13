# Parser Electronic Parity Rollout Plan (Post-Exciting)

## Purpose

Execute the same migration pattern used for exciting across the remaining in-scope parser set so electronic band structure and DOS appear correctly in downstream normalization and GUI usage.

This is the detailed execution plan. Overarching constraints remain in:
- [../.github/copilot-instructions.md](../.github/copilot-instructions.md)

This plan is subordinate to the initial parser migration baseline:
- [mapping_parsers_migration_plan.md](mapping_parsers_migration_plan.md)

Progress and justified deltas must be tracked in:
- [MIGRATION_STATUS.md](MIGRATION_STATUS.md)

## Scope Lock (Steps 6-7)

Remaining parser scope for this rollout:
1. quantumespresso/pwscf
2. yambo
3. gpaw
4. octopus
5. wannier90
6. abinit
7. fhiaims
8. crystal
9. ams
10. vasp (regression guard)

Scope exclusions for this iteration:
1. gromacs (excluded by parser migration plan)
2. lammps and h5md (iteration out of scope)

## Parity Matrix (Steps 8-13)

Mandatory per-parser electronic checks:
1. Band structure presence when relevant.
2. DOS presence when relevant.
3. K-path or k-point plot support when relevant.
4. Reference-energy propagation when relevant (`highest_occupied`, `energies_origin`, or equivalent legacy-aligned quantity).

Legacy baseline references to use for every parser row:
1. /home/jfrudzinski/work/soft/plugins/electronic-parsers
2. /home/jfrudzinski/work/soft/plugins/atomistic-parsers

| Parser | Band Structure Check | DOS Check | K-Path/K-Points Check | Reference Energy Check | Legacy Equivalence Target |
| --- | --- | --- | --- | --- | --- |
| quantumespresso/pwscf | Required when eigenvalues/k-grid available | Required when DOS sidecar or native payload exists | Required for plotted band structures (segment-compatible) | Required when Fermi/highest-occupied baseline exists | Match legacy QE extraction ordering and sidecar fallback behavior before adding new logic |
| yambo | Required when quasiparticle bands are present | Required when DOS payload exists in legacy path | Required when legacy parser exposes path/points for plotting | Required if legacy exposed reference shift fields | Preserve legacy yambo payload semantics; do not invent DOS if legacy did not provide it |
| gpaw | Required from eigenvalue path | Required only where legacy/fixture exposes DOS | Required for band plotting from k-point payload | Required when HOMO/Fermi equivalent can be extracted | Keep eigenvalue-derived parity with legacy, including occupation handling |
| octopus | Required from static eigenvalue outputs | Optional: only if legacy provided DOS in this route | Required for any generated band segments | Required when occupation split can derive highest occupied reference | Keep current DOS-unmapped behavior unless legacy baseline explicitly supports it |
| wannier90 | Required | Required when dos files present | Required (explicit segment/path points) | Required when reference shift appears in legacy output chain | Follow legacy wannier90 path segmentation and band payload completeness |
| abinit | Required | Required | Required when path data exists; otherwise keep legacy-equivalent fallback | Required when Fermi/HOMO available from legacy-equivalent payload | Match legacy abinit occupations and DOS energy-grid treatment |
| fhiaims | Required | Required (+ projected DOS when legacy supported) | Required for mapped band structures | Required when reference energy present in parsed outputs | Preserve legacy fhiaims eigenvalue->band mapping and DOS reference semantics |
| crystal | Required when fort.25-compatible payload exists | Required when DOS payload exists | Required for segment/points when data present | Required when `highest_occupied` or equivalent exists | Keep legacy crystal behavior around optional electronic payloads per fixture availability |
| ams | Optional/conditional: only if legacy route produces bands | Required (primary electronic output) | Only required if band structures are emitted | Required (`energy_highest_occupied` parity) | Preserve legacy ams DOS-first behavior and avoid synthetic band sections |
| vasp (guard) | Required (must not regress existing fallback behavior) | Required (must not regress XML/OUTCAR backfill) | Required for segment plotting compatibility | Required for GUI shift handling | Keep vasp as the regression baseline for parity behavior |

## Execution Order (Step 10)

Process one parser at a time in this order:
1. quantumespresso/pwscf
2. yambo
3. gpaw
4. octopus
5. wannier90
6. abinit
7. fhiaims
8. crystal
9. ams
10. vasp regression hardening

## Implementation Rule Set (Steps 11-13)

For each parser:
1. Implement only extraction/mapping needed to satisfy the four parity checks above.
2. Follow the exciting pattern where relevant:
   - explicit k-path extraction when source data exists,
   - complete DOS value + energy-grid payload,
   - reference-energy propagation for downstream shift behavior.
3. Keep architecture boundaries:
   - helper functions normalize/extract payload only,
   - mapping annotations perform schema population.
4. If a field is unavailable and legacy also did not expose it, keep it unmapped and add a concise TODO in [MIGRATION_STATUS.md](MIGRATION_STATUS.md).
5. Population policy for the remainder of this rollout:
   - default and required path: mapping annotations populate sections,
   - parser code may extract and pre-shape payloads only,
   - parser-side direct `archive.data` electronic output assignments are allowed only as temporary, documented exceptions.

## Completion Gate for Parser Implementation Start

A parser can move from planning to implementation only after:
1. Legacy baseline files for that parser were reviewed in at least one of the two baseline repositories.
2. The parser row above has concrete fixture(s) identified.
3. Expected parity outcomes are listed in the parser's status block in [MIGRATION_STATUS.md](MIGRATION_STATUS.md).
