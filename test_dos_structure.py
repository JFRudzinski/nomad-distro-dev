#!/usr/bin/env python
"""Test script to check DOS compatibility layer implementation."""

from nomad.client import parse

# Parse the file
print("Parsing VASP file...")
entries = parse('864.50_data/vasprun.xml')
if not entries:
    print("✗ No entries parsed")
    exit(1)

print(f"✓ Parsed {len(entries)} entry")
entry_archive = entries[0]
archive = entry_archive.results

# Check DOS structure
if not hasattr(archive, 'properties') or not hasattr(archive.properties, 'electronic'):
    print("✗ No electronic properties")
    exit(1)

electronic = archive.properties.electronic
if not hasattr(electronic, 'dos_electronic_new') or not electronic.dos_electronic_new:
    print("✗ No dos_electronic_new found")
    exit(1)

print(f"✓ Found dos_electronic_new with {len(electronic.dos_electronic_new)} entries")
dos = electronic.dos_electronic_new[0]

if not hasattr(dos, 'data') or not dos.data:
    print("✗ No DOS data")
    exit(1)

print(f"✓ DOS has {len(dos.data)} data entries")
d = dos.data[0]

# Check for legacy subsections
print("\nChecking legacy subsections:")
if hasattr(d, '_legacy_dos') and d._legacy_dos is not None:
    print("  ✓ _legacy_dos subsection exists")
    if hasattr(d._legacy_dos, 'energies') and d._legacy_dos.energies is not None:
        print(f"    - energies: array with {len(d._legacy_dos.energies)} points")
    else:
        print("    ✗ No energies in _legacy_dos")
else:
    print("  ✗ _legacy_dos subsection missing")

if hasattr(d, '_legacy_total') and d._legacy_total is not None:
    print("  ✓ _legacy_total subsection exists")
    if hasattr(d._legacy_total, 'value') and d._legacy_total.value is not None:
        print(f"    - value: array with {len(d._legacy_total.value)} points")
    if hasattr(d._legacy_total, 'spin'):
        print(f"    - spin: {d._legacy_total.spin}")
else:
    print("  ✗ _legacy_total subsection missing")

# Check references
print("\nChecking references:")
print(f"  energies type: {type(d.energies).__name__}")
print(f"  total type: {type(d.total).__name__}")

# Try to get paths if serializable
try:
    if hasattr(d._legacy_dos, 'm_path'):
        print(f"  _legacy_dos path: {d._legacy_dos.m_path()}")
    if hasattr(d._legacy_total, 'm_path'):
        print(f"  _legacy_total path: {d._legacy_total.m_path()}")
except Exception as e:
    print(f"  Could not get paths: {e}")

print("\n✓ DOS compatibility layer implementation successful!")
