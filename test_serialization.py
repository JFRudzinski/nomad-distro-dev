#!/usr/bin/env python3
"""Test serialization of VASP parse results"""

import sys
from nomad.datamodel import EntryArchive
from nomad_simulation_parsers.parsers.vasp.xml_parser import XMLArchiveWriter
from nomad.utils import get_logger

logger = get_logger(__name__)

print("Test: VASP serialization")
print("=" * 60)

# Create archive
archive = EntryArchive()

# Create parser
parser = XMLArchiveWriter()
parser.mainfile = "864.50_data/vasprun.xml"
parser.archive = archive
parser.logger = logger

# Parse
print("1. Parsing...")
try:
    parser.write_to_archive()
    print(f"   ✓ Parse successful")
    print(f"   Outputs: {len(archive.data.outputs) if archive.data else 0}")
except Exception as e:
    print(f"   ✗ Parse failed: {e}")
    sys.exit(1)

# Try to serialize
print("2. Serializing...")
try:
    result = archive.m_to_dict()
    print(f"   ✓ Serialization successful")

    # Check if we have data
    if 'data' in result:
        outputs = result['data'].get('outputs', [])
        print(f"   Outputs in dict: {len(outputs)}")
        if outputs:
            first_output = outputs[0]
            has_model_system_ref = 'model_system_ref' in first_output
            print(f"   First output has model_system_ref: {has_model_system_ref}")

except Exception as e:
    print(f"   ✗ Serialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 60)
print("All tests passed!")
