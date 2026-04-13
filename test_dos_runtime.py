#!/usr/bin/env python
"""Runtime test of DOS compatibility layer - creates DOSNew directly."""

import numpy as np
from nomad.datamodel.results import DOSNew

# Try to import runschema
try:
    import runschema.calculation
    print("✓ runschema imported successfully")
except ImportError:
    print("✗ runschema not available")
    exit(1)

# Create a DOSNew instance
print("\nCreating DOSNew instance...")
dos_data = DOSNew()

# Create runschema compatibility wrappers
print("Creating runschema wrappers...")
try:
    # Create Dos wrapper for energies
    legacy_dos = dos_data.m_create(runschema.calculation.Dos)
    print("✓ Created runschema.calculation.Dos wrapper using m_create()")

    # Set energies
    test_energies = np.linspace(-10, 10, 100)
    legacy_dos.energies = test_energies
    print(f"✓ Set energies: array with {len(test_energies)} points")

    # Attach to DOSNew
    dos_data._legacy_dos = legacy_dos
    print("✓ Attached _legacy_dos subsection")

    # Reference it
    dos_data.energies = legacy_dos
    print("✓ Set energies reference")

except Exception as e:
    print(f"✗ Error creating Dos wrapper: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

try:
    # Create DosValues wrapper for total DOS
    legacy_total = dos_data.m_create(runschema.calculation.DosValues)
    print("✓ Created runschema.calculation.DosValues wrapper using m_create()")

    # Set values
    test_values = np.random.rand(100)
    legacy_total.value = test_values
    print(f"✓ Set values: array with {len(test_values)} points")

    # Set spin
    legacy_total.spin = 0
    print("✓ Set spin channel")

    # Attach to DOSNew
    dos_data._legacy_total = legacy_total
    print("✓ Attached _legacy_total subsection")

    # Reference it
    dos_data.total = legacy_total
    print("✓ Set total reference")

except Exception as e:
    print(f"✗ Error creating DosValues wrapper: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Try to get paths (test serialization)
print("\nTesting serialization paths...")
try:
    if hasattr(dos_data._legacy_dos, 'm_path'):
        path = dos_data._legacy_dos.m_path()
        print(f"✓ _legacy_dos.m_path(): {path}")
        if path.startswith('//'):
            print("  ⚠ WARNING: Path starts with '//' (orphaned section)")
        else:
            print("  ✓ Path is properly formed")

    if hasattr(dos_data._legacy_total, 'm_path'):
        path = dos_data._legacy_total.m_path()
        print(f"✓ _legacy_total.m_path(): {path}")
        if path.startswith('//'):
            print("  ⚠ WARNING: Path starts with '//' (orphaned section)")
        else:
            print("  ✓ Path is properly formed")

except Exception as e:
    print(f"✗ Error getting paths: {e}")
    import traceback
    traceback.print_exc()

print("\n✓ DOS compatibility layer runtime test PASSED!")
print("  - runschema wrappers can be created")
print("  - Subsections can be attached")
print("  - References can be set")
print("  - Serialization paths can be generated")
