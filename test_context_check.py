#!/usr/bin/env python3
"""Test if context check is working"""
import sys
sys.path.insert(0, 'packages/nomad-FAIR')
sys.path.insert(0, 'packages/nomad-simulations/src')

from nomad.datamodel import EntryArchive
from nomad_simulation_parsers.vasp import VASPParser

# Create parser
parser = VASPParser()
archive = EntryArchive()

# Parse the file
parser.parse('864.50_data/vasprun.xml', archive, None)

# Check context
print("=" * 60)
print("Context Check Test")
print("=" * 60)

if hasattr(archive, 'data') and archive.data:
    print(f"1. archive.data exists: True")
    print(f"2. archive.data type: {type(archive.data).__name__}")

    # Check m_root
    data_root = archive.data.m_root()
    print(f"3. archive.data.m_root() type: {type(data_root).__name__}")
    print(f"4. archive.data.m_root() is archive.data: {data_root is archive.data}")

    # Check if root has m_context
    has_m_context_attr = hasattr(data_root, 'm_context')
    print(f"5. data_root has 'm_context' attribute: {has_m_context_attr}")

    if has_m_context_attr:
        m_context_value = data_root.m_context
        print(f"6. data_root.m_context value: {m_context_value}")
        print(f"7. data_root.m_context is None: {m_context_value is None}")

    # Check outputs
    if hasattr(archive.data, 'outputs') and archive.data.outputs:
        output0 = archive.data.outputs[0]
        print(f"\n8. First output type: {type(output0).__name__}")

        output_root = output0.m_root()
        print(f"9. output.m_root() type: {type(output_root).__name__}")
        print(f"10. output.m_root() is archive.data: {output_root is archive.data}")

        has_context = getattr(output_root, 'm_context', None) is not None
        print(f"11. has_context check result: {has_context}")

        # Check if model_system_ref was set
        has_ref = output0.model_system_ref is not None
        print(f"12. model_system_ref is set: {has_ref}")
        if has_ref:
            print(f"    model_system_ref type: {type(output0.model_system_ref).__name__}")

print("=" * 60)
