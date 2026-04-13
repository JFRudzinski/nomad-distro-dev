#!/usr/bin/env python3
"""Check if VASP parser populates outputs correctly."""

from nomad.datamodel import EntryArchive
from nomad_simulation_parsers.parsers.vasp.xml_parser import XMLArchiveWriter
from nomad.utils import get_logger

logger = get_logger(__name__)

print("=" * 60)
print("VASP Outputs Population Test")
print("=" * 60)

archive = EntryArchive()
writer = XMLArchiveWriter()
writer.mainfile = '864.50_data/vasprun.xml'
writer.archive = archive
writer.logger = logger

print("\nRunning parser...")
writer.write_to_archive()

print(f"\n✓ archive.data exists: {archive.data is not None}")

if archive.data:
    print(f"✓ archive.data type: {type(archive.data).__name__}")

    # Check outputs
    if hasattr(archive.data, 'outputs') and archive.data.outputs:
        print(f"✓ Number of outputs: {len(archive.data.outputs)}")
        print(f"  First output type: {type(archive.data.outputs[0]).__name__}")
    else:
        print("❌ No outputs found!")

    # Check model_system
    if hasattr(archive.data, 'model_system') and archive.data.model_system:
        print(f"✓ Number of model_systems: {len(archive.data.model_system)}")
    else:
        print("❌ No model_systems found!")

# Check workflow2
if hasattr(archive, 'workflow2') and archive.workflow2:
    wf = archive.workflow2
    print(f"\n✓ workflow2 type: {type(wf).__name__}")
    if hasattr(wf, 'tasks'):
        print(f"  tasks attr exists, value: {wf.tasks}")
        if wf.tasks:
            print(f"  Number of tasks: {len(wf.tasks)}")
    else:
        print("  No tasks attribute")
else:
    print("\n❌ workflow2 not created!")

print("\n" + "=" * 60)
