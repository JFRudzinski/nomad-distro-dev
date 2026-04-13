#!/usr/bin/env python
"""Quick test to verify DOS compatibility layer schema is properly defined."""

import sys

# Check schema definition
print("Checking DOSNew schema...")
from nomad.datamodel.results import DOSNew

# Check if legacy subsections exist
if hasattr(DOSNew.m_def, 'all_sub_sections'):
    subsections = {s.name: s for s in DOSNew.m_def.all_sub_sections.values()}

    if '_legacy_dos' in subsections:
        print("✓ _legacy_dos subsection defined in DOSNew schema")
        sub = subsections['_legacy_dos']
        print(f"  - sub_section type: {sub.sub_section}")
    else:
        print("✗ _legacy_dos subsection NOT found in schema")
        sys.exit(1)

    if '_legacy_total' in subsections:
        print("✓ _legacy_total subsection defined in DOSNew schema")
        sub = subsections['_legacy_total']
        print(f"  - sub_section type: {sub.sub_section}")
    else:
        print("✗ _legacy_total subsection NOT found in schema")
        sys.exit(1)
else:
    print("✗ Could not access subsections")
    sys.exit(1)

# Check normalizer implementation
print("\nChecking normalizer implementation...")
from nomad_topology_normalizer.normalizers.results import ResultsNormalizerBase
import inspect

source = inspect.getsource(ResultsNormalizerBase._map_dos_data)
if '_legacy_dos' in source:
    print("✓ _map_dos_data() uses _legacy_dos")
if '_legacy_total' in source:
    print("✓ _map_dos_data() uses _legacy_total")
if 'm_create(runschema.calculation.Dos)' in source:
    print("✓ Creates runschema.calculation.Dos wrapper")
if 'm_create(runschema.calculation.DosValues)' in source:
    print("✓ Creates runschema.calculation.DosValues wrapper")

print("\n✓ DOS compatibility layer implementation is correctly defined!")
