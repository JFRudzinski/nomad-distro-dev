#!/usr/bin/env python3
"""Quick test to see where the hang is."""

import sys
print("1. Starting imports...", file=sys.stderr, flush=True)

print("2. Importing nomad.datamodel...", file=sys.stderr, flush=True)
from nomad.datamodel import EntryArchive

print("3. Importing vasp xml_parser...", file=sys.stderr, flush=True)
from nomad_simulation_parsers.parsers.vasp.xml_parser import XMLArchiveWriter

print("4. Importing utils.get_logger...", file=sys.stderr, flush=True)
from nomad.utils import get_logger

print("5. All imports successful!", file=sys.stderr, flush=True)

logger = get_logger(__name__)
archive = EntryArchive()
writer = XMLArchiveWriter()
writer.mainfile = '864.50_data/vasprun.xml'
writer.archive = archive
writer.logger = logger

print("6. Starting parse...", file=sys.stderr, flush=True)
writer.write_to_archive()

print("7. Parse complete!", file=sys.stderr, flush=True)
print(f"Outputs: {len(archive.data.outputs) if archive.data and archive.data.outputs else 0}")
