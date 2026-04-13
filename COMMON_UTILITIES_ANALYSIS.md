# Common Parser Utilities - Consolidation Analysis

## Executive Summary

Analysis of `nomad-simulation-parsers` reveals significant code duplication across parsers, particularly in electronic property extraction (band gaps, band structures, DOS). This document proposes consolidated utility functions to reduce redundancy and improve maintainability.

## Current State

### 1. OCCUPATION_THRESHOLD Constant

**Issue:** Defined separately in 8+ parsers
- `abinit/parser.py:37` → `OCCUPATION_THRESHOLD = 0.5`
- `vasp/xml_parser.py:32` → `OCCUPATION_THRESHOLD = 0.5`
- `vasp/outcar_parser.py:35` → `OCCUPATION_THRESHOLD = 0.5`
- `gpaw/parser.py:22` → `OCCUPATION_THRESHOLD = 0.5`
- `ams/parser.py:39` → `OCCUPATION_THRESHOLD = 0.5`
- `octopus/parser.py:20` → `OCCUPATION_THRESHOLD = 0.5`
- `exciting/parser.py:443` → `occupation_threshold = 0.5` (local variable)

**Recommendation:** Move to `parsers/utils/general.py` as a shared constant

---

### 2. Band Gap Extraction from Eigenvalues/Occupations

**Issue:** Nearly identical implementation in 6+ parsers

**Common Pattern:**
```python
def get_band_gaps(self, eigenvalues, occupations):
    # 1. Validate inputs
    if eigenvalues is None or occupations is None:
        return []

    # 2. Extract occupied/unoccupied states
    occupied = eigenvalues[occupations >= OCCUPATION_THRESHOLD]
    unoccupied = eigenvalues[occupations < OCCUPATION_THRESHOLD]

    # 3. Calculate gap
    if occupied.size == 0 or unoccupied.size == 0:
        return []
    gap = float(np.min(unoccupied) - np.max(occupied))

    # 4. Format result
    return [{'value': max(0.0, gap), 'spin_channel': spin_channel}]
```

**Occurrences:**
- `abinit/parser.py:671-693` (with spin channel handling)
- `gpaw/parser.py:129-168` (with unit handling)
- `ams/parser.py:127-187` (more complex with tuple/list fallback)
- `octopus/parser.py:453-479` (similar pattern)
- `vasp/xml_parser.py:161-184` (similar pattern)
- `vasp/outcar_parser.py:464-489` (similar pattern)

**Recommendation:** Create utility function in `parsers/utils/general.py`:

```python
def calculate_band_gap_from_occupations(
    eigenvalues: np.ndarray,
    occupations: np.ndarray,
    occupation_threshold: float = OCCUPATION_THRESHOLD,
    spin_channel: int | None = None,
    energy_units: Any = None,
) -> dict[str, Any] | None:
    """Calculate band gap from eigenvalues and occupation numbers.

    Args:
        eigenvalues: Energy eigenvalues array
        occupations: Occupation numbers (0-2 for spin, 0-1 for spinless)
        occupation_threshold: Threshold to differentiate occupied/unoccupied
        spin_channel: Optional spin channel index
        energy_units: Optional pint units to apply to gap value

    Returns:
        Dictionary with 'value' (and optional 'spin_channel') or None if invalid
    """
    if eigenvalues is None or occupations is None:
        return None

    eigenvalues = np.asarray(eigenvalues, dtype=float)
    occupations = np.asarray(occupations, dtype=float)

    if eigenvalues.size == 0 or occupations.size == 0:
        return None
    if eigenvalues.shape != occupations.shape:
        return None

    occupied = eigenvalues[occupations >= occupation_threshold]
    unoccupied = eigenvalues[occupations < occupation_threshold]

    if occupied.size == 0 or unoccupied.size == 0:
        return None

    gap = float(np.min(unoccupied) - np.max(occupied))
    gap = max(0.0, gap)

    result = {'value': gap if energy_units is None else gap * energy_units}
    if spin_channel is not None:
        result['spin_channel'] = spin_channel

    return result
```

---

### 3. Reference Energy Extraction (Fermi/VBM)

**Issue:** Similar patterns in multiple parsers but with different data sources

**Occurrences:**
- `gpaw/parser.py:93-102` → `get_reference_energy()`
- `octopus/parser.py:414-424` → `get_reference_energy()`
- `quantumespresso/pwscf/parser.py:200-217` → `get_reference_energy()`
- `wannier90/parser.py:456-473` → `get_reference_energy()`, `get_reference_energy_from_win_file()`

**Pattern:**
- Extract Fermi energy or highest occupied from various sources
- Used as reference/alignment for band structures

**Recommendation:** **Less critical** - implementations are data-source specific, but could document common interface pattern

---

### 4. Output-to-System Linking

**Status:** ✅ **Already consolidated** in `parsers/utils/general.py:18-38`

**Function:** `link_outputs_to_model_systems(simulation)`

**Usage:** Already imported and used by:
- `quantumespresso/parser.py:34,674`
- `ams/parser.py:30,335`

**Action:** Ensure all parsers use this utility instead of manual linking

---

### 5. K-Path Handling for Band Structures

**Issue:** Different parsers have k-path parsing logic

**Occurrences:**
- `wannier90/parser.py:137-174` → `get_k_line_path()`
- `phonopy/calculator.py:38-153` → `generate_kpath_parameters()`, `read_kpath()`, `generate_kpath_ase()`

**Recommendation:** **Defer** - k-path handling is complex and parser-specific (different file formats)

---

### 6. DOS Data Formatting

**Issue:** Similar DOS dict construction but with varying input formats

**Occurrences:**
- `wannier90/parser.py:85-100` → `get_dos()` (returns dict with energies/values)
- `abinit/parser.py:706-716` → `get_dos()` (returns list of dicts, spin handling)
- `crystal/parser.py:301-314` → `get_dos()` (returns list of dicts)
- `quantumespresso/pwscf/parser.py:234-253` → `get_dos()` (returns list of dicts)

**Pattern:**
```python
def get_dos(self, source):
    return [{'energies': energy_grid, 'value': dos_values}]
```

**Recommendation:** **Low priority** - input sources vary significantly

---

## Recommended Implementation Priority

### High Priority (Wave 1)

1. **OCCUPATION_THRESHOLD constant** → `parsers/utils/general.py`
   - Impact: 8+ parsers
   - Effort: 10 minutes
   - Risk: None

2. **calculate_band_gap_from_occupations()** utility → `parsers/utils/general.py`
   - Impact: 6+ parsers (VASP, ABINIT, GPAW, Octopus, AMS, Exciting)
   - Effort: 2 hours (implement + refactor callers + test)
   - Risk: Low (well-tested pattern)

### Medium Priority (Wave 2)

3. **Audit link_outputs_to_model_systems() usage**
   - Check if parsers are manually linking instead of using utility
   - Impact: Potentially 5+ parsers
   - Effort: 1 hour (audit + fix)
   - Risk: None

### Low Priority (Future)

4. **Common DOS formatting helpers** (if patterns emerge after more migration work)
5. **Reference energy extraction interface documentation** (common API pattern)

---

## Migration Strategy

### Step 1: Add Utilities (Non-Breaking)

1. Add to `parsers/utils/general.py`:
   ```python
   # Constants
   OCCUPATION_THRESHOLD = 0.5

   # Band gap calculation
   def calculate_band_gap_from_occupations(...): ...
   ```

2. Add comprehensive tests in `tests/parsers/utils/test_general.py`:
   - Test with spin-polarized data
   - Test with units
   - Test edge cases (no gap, all occupied, empty arrays)
   - Test shape mismatches

### Step 2: Refactor Parsers (Incremental)

For each parser:
1. Import utilities at top
2. Replace local OCCUPATION_THRESHOLD with imported constant
3. Replace get_band_gaps() implementation with utility call
4. Run parser-specific tests to ensure behavior unchanged
5. Commit per-parser

**Order:** ABINIT → GPAW → Octopus → AMS → VASP (xml) → VASP (outcar) → Exciting

### Step 3: Remove Duplicates

After all parsers migrated:
- Remove local constant definitions
- Remove local get_band_gaps() implementations
- Final regression test run

---

## Success Criteria

1. All parser tests pass after refactoring
2. Line count reduced by ~150-200 lines across all parsers
3. No change in output behavior (legacy parity maintained)
4. New utility has >95% test coverage
5. All parsers using shared OCCUPATION_THRESHOLD constant

---

## Follow-up Opportunities

After this consolidation:
1. Look for DOS/band structure value extraction patterns
2. Consider eigenvalue normalization utilities (unit handling)
3. Review convergence target extraction patterns across workflows
