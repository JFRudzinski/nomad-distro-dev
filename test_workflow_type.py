#!/usr/bin/env python3
"""Quick test to see what workflow type is being created."""

import sys

# Bypass normal parsing to directly test the workflow building
from nomad_simulation_parsers.parsers.vasp.xml_parser import VasprunParser

print("=" * 60)
print("VASP Workflow Type Test")
print("=" * 60)

try:
    parser = VasprunParser(filepath='864.50_data/vasprun.xml')

    # Get parameters
    nsw = parser._get_parameter('NSW', section='ionic')
    ibrion_raw = parser._get_parameter('IBRION', section='ionic')
    ibrion = -1 if nsw == 0 else ibrion_raw
    if ibrion is None:
        ibrion = -1

    print(f"\nParameters from XML:")
    print(f"  NSW = {nsw}")
    print(f"  IBRION (raw) = {ibrion_raw}")
    print(f"  IBRION (processed) = {ibrion}")
    print(f"  nsw == 0? {nsw == 0}")
    print(f"  int(ibrion) == -1? {int(ibrion) == -1 if ibrion is not None else 'None'}")
    print(f"  int(ibrion) == 0? {int(ibrion) == 0 if ibrion is not None else 'None'}")

    # Build workflow
    workflow = parser.build_workflow()

    print(f"\nWorkflow created:")
    print(f"  Type: {type(workflow).__name__}")
    print(f"  Name: {workflow.name if hasattr(workflow, 'name') else 'N/A'}")

    parser.close()

    print("\n" + "=" * 60)

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
