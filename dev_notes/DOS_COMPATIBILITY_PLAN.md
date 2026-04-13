# DOS Compatibility Layer Plan

## Problem Statement

**Symptom:** GUI DOS visualizer fails with "Cannot read properties of undefined (reading 'match')" at [DOS.js:194](../packages/nomad-FAIR/gui/src/components/visualization/DOS.js#L194)

**Root Cause:** Schema migration incompatibility
- **Parsers (archive.data):** Create `nomad-simulations.ElectronicDensityOfStates` sections
- **GUI (archive.results):** Expects `runschema.calculation.Dos` structure
- **Results schema:** `DOSNew.energies` typed as `runschema.calculation.Dos.energies` reference

**Critical Constraint:** We can NEVER mix runschema with nomad-simulations in `archive.data`. Runschema can only appear in `archive.results` for downstream compatibility.

## Schema Structure Comparison

### nomad-simulations Structure (archive.data)
```
archive.data.outputs[i].electronic_dos[] (ElectronicDensityOfStates)
├── energies (SubSection: Energy2)
│   └── points (Quantity: float array)
├── value (Quantity: float array with units)
├── spin_channel (int)
└── energies_origin (float)
```

### runschema Structure (needed in archive.results)
```
runschema.calculation.Dos
├── energies (Quantity: float array with units)
└── total[] (SubSection: DosValues)
    ├── value (Quantity: float array)
    ├── normalization_factor (float)
    └── spin (int)
```

### results Structure (archive.results)
```
archive.results.properties.electronic.dos_electronic_new[] (DOSElectronicNew)
├── label (str)
├── spin_polarized (bool)
├── has_projected (bool)
└── data[] (DOSNew)
    ├── energies (Quantity → Reference to runschema.calculation.Dos.energies)
    ├── total (Quantity → Reference to runschema.calculation.DosValues)
    ├── spin_channel (int)
    └── energy_ref (float)
```

## Failed Approaches

### Attempt 1: Orphaned Wrappers
**Code:** Created `runschema.calculation.Dos()` sections without parent
```python
legacy_dos = runschema.calculation.Dos()
legacy_dos.energies = energies_points
dos_data.energies = legacy_dos
```
**Result:** ❌ Serialization produced malformed paths: `"energies": "//energies"` (no parent path)

### Attempt 2: Using m_create()
**Code:** Tried attaching wrappers as subsections to DOSNew
```python
legacy_dos = dos_data.m_create(runschema.calculation.Dos)
```
**Result:** ❌ `TypeError: There is no subsection to hold a runschema.calculation.Dos in DOSNew`

### Attempt 3: Direct Reference
**Code:** Referenced ElectronicDensityOfStates directly in DOSNew
```python
dos_data.energies = dos_section  # ElectronicDensityOfStates
```
**Result:** ❌ Type mismatch - ElectronicDensityOfStates has incompatible structure (energies is SubSection not Quantity)

## Correct Solution: Compatibility Subsections in Results

### Strategy
Similar to the `System.atoms` solution where we copy ASE atoms into `results.material.topology[].atoms` for GUI compatibility, we need to:
1. **Create runschema sections in archive.results** (not archive.data)
2. **Copy DOS data** from nomad-simulations ElectronicDensityOfStates into runschema structure
3. **Store sections as subsections** in DOSNew so they have proper parent paths
4. **Reference these subsections** from DOSNew.energies and DOSNew.total quantities

### Implementation Steps

#### Step 1: Extend DOSNew Schema
**File:** `packages/nomad-FAIR/nomad/datamodel/results.py`
**Line:** ~2656 (in DOSNew class definition)

Add subsections to hold runschema compatibility wrappers:
```python
class DOSNew(MSection):
    # ... existing fields ...
    
    # Compatibility subsections - hold runschema data for GUI
    # These subsections are populated by the topology normalizer from nomad-simulations data
    if runschema:
        _legacy_dos = SubSection(
            sub_section=runschema.calculation.Dos.m_def,
            description="""
            Compatibility wrapper holding DOS data in runschema format for GUI visualization.
            Populated from nomad-simulations ElectronicDensityOfStates during normalization.
            """
        )
        _legacy_total = SubSection(
            sub_section=runschema.calculation.DosValues.m_def,
            description="""
            Compatibility wrapper holding total DOS values in runschema format for GUI.
            Populated from nomad-simulations ElectronicDensityOfStates during normalization.
            """
        )
```

#### Step 2: Modify Normalizer to Create Wrappers
**File:** `packages/nomad-topology-normalizer/src/nomad_topology_normalizer/normalizers/results.py`
**Method:** `_map_dos_data()` (~line 595)

```python
def _map_dos_data(self, dos_section) -> tuple[DOSNew, bool] | None:
    """Map one ElectronicDensityOfStates section into results DOSNew.
    
    Creates runschema compatibility wrappers for GUI visualization while keeping
    nomad-simulations data clean in archive.data.
    """
    energies_points = getattr(
        getattr(dos_section, 'energies', None), 'points', None
    )
    values = getattr(dos_section, 'value', None)
    if not valid_array(energies_points) or values is None:
        return None
    try:
        if not valid_array(np.array(values.magnitude)):
            return None
    except Exception:
        return None

    dos_data = DOSNew()
    
    # Create runschema compatibility wrapper sections
    if runschema:
        # Create Dos wrapper for energies
        legacy_dos = dos_data.m_create(runschema.calculation.Dos)
        legacy_dos.energies = energies_points  # Copy energies array
        dos_data._legacy_dos = legacy_dos
        dos_data.energies = legacy_dos  # Reference the subsection
        
        # Create DosValues wrapper for total DOS
        legacy_total = dos_data.m_create(runschema.calculation.DosValues)
        legacy_total.value = values  # Copy DOS values
        legacy_total.spin = getattr(dos_section, 'spin_channel', 0)
        dos_data._legacy_total = legacy_total
        dos_data.total = legacy_total  # Reference the subsection
    
    dos_data.spin_channel = getattr(dos_section, 'spin_channel', None)
    
    energies_origin = getattr(dos_section, 'energies_origin', None)
    if energies_origin is not None:
        dos_data.energy_ref = energies_origin

    has_projected = bool(getattr(dos_section, 'projected_dos', None))
    return dos_data, has_projected
```

### Expected Archive Structure After Fix

```json
{
  "data": {
    "outputs": [{
      "electronic_dos": [{
        "energies": { "points": [...] },
        "value": [...],
        "spin_channel": 0
      }]
    }]
  },
  "results": {
    "properties": {
      "electronic": {
        "dos_electronic_new": [{
          "data": [{
            "_legacy_dos": {
              "energies": [...]
            },
            "_legacy_total": {
              "value": [...],
              "spin": 0
            },
            "energies": "/results/properties/electronic/dos_electronic_new/0/data/0/_legacy_dos",
            "total": "/results/properties/electronic/dos_electronic_new/0/data/0/_legacy_total",
            "spin_channel": 0
          }]
        }]
      }
    }
  }
}
```

### GUI Compatibility Path

**File:** `packages/nomad-FAIR/gui/src/components/visualization/DOS.js`
**Line:** 194

Current code:
```javascript
const match = data.energies.match(pattern)  // data.energies is a reference path
const path = match ? match[2] : data.energies
```

With fix, `data.energies` will be:
- A reference string like `"/results/.../data/0/_legacy_dos"`
- GUI resolves this to `_legacy_dos` subsection
- Accesses `_legacy_dos.energies` array (runschema.calculation.Dos.energies)

## Advantages of This Approach

1. ✅ **Clean separation**: nomad-simulations data stays pure in archive.data
2. ✅ **Proper archive paths**: Subsections have parent paths (not orphaned)
3. ✅ **Type safety**: m_create() ensures proper schema attachment
4. ✅ **GUI compatibility**: Reference paths resolve to valid runschema sections
5. ✅ **Mirrors atoms solution**: Same pattern as System.atoms for GUI visualizer
6. ✅ **Temporary**: Can be removed once GUI migrates to nomad-simulations structure

## Testing Plan

1. **Parse test file:** `uv run nomad parse 864.50_data/vasprun.xml --show-archive`
2. **Verify structure:** Check that `dos_electronic_new[].data[]` has:
   - `_legacy_dos` subsection with energies array
   - `_legacy_total` subsection with value array
   - `energies` reference pointing to `_legacy_dos`
   - `total` reference pointing to `_legacy_total`
3. **Check paths:** Ensure references are proper archive paths (not "//energies")
4. **GUI validation:** Load in GUI and verify DOS visualizer works

## Migration Path

**Short-term (now):**
- Implement compatibility layer in results
- GUI continues to work with runschema structure

**Long-term (future):**
- Update GUI to read nomad-simulations ElectronicDensityOfStates directly
- Remove `_legacy_dos` and `_legacy_total` subsections from DOSNew
- Remove wrapper creation code from normalizer
- Remove runschema dependency from results.py

## Warnings References

Current warnings during parse:
```
WARNING  nomad.client  Exception raised in resolve_p dos_name: name
WARNING  nomad.client  The index of the sibling_section is out of range.
WARNING  nomad.client  Could not resolve the referenced `ModelSystem` in the `Outputs`.
```

These warnings are likely related to the broken DOS references and should be resolved once proper references are established.

---

**Status:** Plan documented, ready for implementation
**Next Steps:** Implement schema changes and normalizer modifications
**Priority:** High - DOS visualizer currently non-functional for all parsed data
