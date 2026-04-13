#!/usr/bin/env python3
"""Validate that the VASP parser now populates archive.data correctly."""

import sys
from nomad.client import parse

print("=" * 60)
print("VASP Parser Fix Validation")
print("=" * 60)

try:
    # Parse the test file
    print("\nParsing: 864.50_data/vasprun.xml")
    archive = parse('864.50_data/vasprun.xml')

    # Check if data exists
    has_data = hasattr(archive, 'data') and archive.data is not None
    print(f"\n✓ archive.data exists: {has_data}")

    if not has_data:
        print("\n❌ FAILED: archive.data is not populated!")
        sys.exit(1)

    # Check data type
    data_type = type(archive.data).__name__
    print(f"✓ Data type: {data_type}")

    # Check model_system
    has_model_system = hasattr(archive.data, 'model_system')
    print(f"✓ Has model_system attribute: {has_model_system}")

    if has_model_system and archive.data.model_system:
        n_systems = len(archive.data.model_system)
        print(f"✓ Number of model_systems: {n_systems}")

    # Check program
    has_program = hasattr(archive.data, 'program')
    print(f"✓ Has program attribute: {has_program}")

    if has_program and archive.data.program:
        prog_name = getattr(archive.data.program, 'name', 'N/A')
        prog_version = getattr(archive.data.program, 'version', 'N/A')
        print(f"✓ Program: {prog_name} {prog_version}")

    # Check outputs
    has_outputs = hasattr(archive.data, 'outputs') and archive.data.outputs
    print(f"✓ Has outputs: {has_outputs}")

    if has_outputs:
        n_outputs = len(archive.data.outputs)
        print(f"✓ Number of outputs: {n_outputs}")

    print("\n" + "=" * 60)
    print("✅ SUCCESS: Parser is now populating archive.data!")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
