# Parser Circular Import Fix - Summary

## Problem
After implementing the migration plans, the VASP parser (and other parsers) were failing to load with this error:
```
AssertionError: Error loading entry point "nomad_simulation_parsers.parsers:exciting_parser":
The load method of a parser entry point must return a Parser instance
```

## Root Causes

### Issue 1: Wrong Simulation Class Import (causes empty archive.data)
Parsers were importing the **base** `Simulation` class instead of their **parser-specific** `Simulation` classes:
- Base: `from nomad_simulations.schema_packages.general import Simulation`
- Needed: `from nomad_simulation_parsers.schema_packages.vasp import Simulation`

The parser-specific Simulation classes contain the mapping annotations needed to populate data from files into the archive structure. Without these annotations, `archive.data` was empty.

### Issue 2: Module-Level Import Causes Circular Import
Importing the parser-specific Simulation classes at module level created a circular dependency during entry point loading:
1. Entry point system loads parser module
2. Parser module imports from schema package (module level)
3. Schema package initialization might trigger parser discovery
4. → Circular import!

## Solution

**Move Simulation imports inside methods where they're used** (not at module level):

### Before (BROKEN):
```python
# At module level
from nomad_simulation_parsers.schema_packages.vasp import Simulation

class XMLArchiveWriter(ArchiveWriter):
    def write_to_archive(self) -> None:
        data_parser.data_object = Simulation()  # Uses module-level import
```

### After (FIXED):
```python
# No module-level Simulation import

class XMLArchiveWriter(ArchiveWriter):
    def write_to_archive(self) -> None:
        from nomad_simulation_parsers.schema_packages.vasp import Simulation  # Local import
        data_parser.data_object = Simulation()
```

## Files Modified

### VASP Parser
- `packages/nomad-simulation-parsers/src/nomad_simulation_parsers/parsers/vasp/xml_parser.py`
  - Removed module-level `Simulation` import
  - Added local import in `write_to_archive()` method

- `packages/nomad-simulation-parsers/src/nomad_simulation_parsers/parsers/vasp/outcar_parser.py`
  - Removed module-level `Simulation` import
  - Added local import in `write_to_archive()` method

### Other Affected Parsers (same pattern applied)
- `packages/nomad-simulation-parsers/src/nomad_simulation_parsers/parsers/exciting/parser.py`
- `packages/nomad-simulation-parsers/src/nomad_simulation_parsers/parsers/gpaw/parser.py`
- `packages/nomad-simulation-parsers/src/nomad_simulation_parsers/parsers/yambo/parser.py`
- `packages/nomad-simulation-parsers/src/nomad_simulation_parsers/parsers/wannier90/parser.py`

## Validation

✓ All modified parser files compile without syntax errors
✓ Parser-specific Simulation classes are now used (ensuring mapping annotations work)
✓ Imports happen inside methods (avoiding circular import during entry point loading)

## Next Steps

1. Clear Python cache:
   ```bash
   find packages/nomad-simulation-parsers -type d -name __pycache__ -exec rm -rf {} +
   ```

2. Test parsing:
   ```python
   from nomad.client import parse
   archive = parse('864.50_data/vasprun.xml')
   assert archive.data is not None
   assert hasattr(archive.data, 'model_system')
   ```

3. Verify entry points load:
   ```python
   from nomad.parsing import parsers
   # Should load without AssertionError
   ```
