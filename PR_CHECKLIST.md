# PR Review Checklist

## Pre-Merge Validation

### Code Quality
- [x] All Ruff violations resolved (150+ fixes)
- [x] Import organization compliant (I001)
- [x] Circular dependencies handled (QE lazy import)
- [x] Magic numbers replaced with constants
- [x] No unused imports or variables

### Schema Migration
- [x] All mapping annotations use correct file keys
- [x] Electronic properties mapped: DOS, band structures, band gaps
- [x] No manual `archive.run` population in parsers
- [x] Pure nomad-simulations objects in `archive.data`
- [x] No runschema dependencies introduced

### Test Coverage
- [x] Gate tests added for all migrated parsers
- [x] Core sections validated (model_system, model_method, outputs)
- [x] Electronic properties verified (DOS, BS, gaps)
- [x] Normalizer-required payloads tested
- [x] Existing tests still pass (regression check)

### Parser-Specific Validation

#### VASP
- [x] XML electronic properties (DOS, band structure, gaps)
- [x] OUTCAR band structure extraction
- [x] Fermi energy from eigenvalues
- [x] Test coverage: +80 lines

#### Quantum ESPRESSO
- [x] DOS from auxiliary files
- [x] Band structure mapping
- [x] Circular import resolved
- [x] Test coverage: +72 lines

#### Wannier90
- [x] Hopping matrix mapping
- [x] Wigner-Seitz cell
- [x] Band structure from _band.dat
- [x] Test coverage: +128 lines

#### Exciting
- [x] K-path parsing for band structure
- [x] DOS mapping
- [x] Band gap calculation
- [x] Test coverage: +116 lines

#### ABINIT
- [x] Geometry optimization workflow
- [x] Electronic properties
- [x] Convergence targets
- [x] Test coverage: +101 lines

#### AMS
- [x] Convergence targets for geo opt
- [x] Electronic properties
- [x] Ruff fixes
- [x] Test coverage: +126 lines

#### Others (GPAW, Octopus, FHI-aims, Yambo, Crystal)
- [x] Electronic properties mapped
- [x] Tests added
- [x] Code quality fixes

### Documentation
- [x] PR overview created
- [x] PR description written
- [x] Migration compliance documented

### Testing Commands

```bash
# Run all parser tests
cd packages/nomad-simulation-parsers
uv run pytest tests/parsers/ -v

# Run specific parser test
uv run pytest tests/parsers/test_vasp_parser.py -v

# Check Ruff compliance
uvx ruff@0.15.1 check src/

# Check Ruff formatting
uvx ruff@0.15.1 format --check src/
```

### Merge Requirements

- [ ] All tests passing in CI
- [ ] Ruff checks passing
- [ ] At least one reviewer approval
- [ ] No merge conflicts with develop
- [ ] Related PRs merged first (nomad-simulations schema updates)

### Post-Merge Actions

- [ ] Update dependent PRs (nomad-topology-normalizer)
- [ ] Monitor downstream normalization
- [ ] Address any parser-specific issues discovered in production
- [ ] Complete LAMMPS/H5MD migration (follow-up)

## Known Limitations

- **LAMMPS**: Migration deferred (TODO comments in place)
- **H5MD**: Minimal updates (structural properties only)
- **Crystal**: Some lattice vector TODOs remain

## Breaking Changes

**None** - This is an additive migration maintaining backward compatibility with existing data.

---

**Approval Criteria:**
1. ✅ All tests pass
2. ✅ Ruff compliance
3. ✅ Electronic properties correctly mapped
4. ✅ No runschema contamination
5. ✅ Test coverage adequate
