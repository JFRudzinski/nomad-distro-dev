#!/usr/bin/env python3
"""Diagnose the workflow normalization issue."""

import sys
from nomad.client import parse

print("=" * 60)
print("Workflow Normalization Diagnostic")
print("=" * 60)

try:
    print("\nParsing: 864.50_data/vasprun.xml")
    archive = parse('864.50_data/vasprun.xml')

    print("\n--- Archive Structure ---")
    print(f"✓ archive.data exists: {archive.data is not None}")

    if archive.data:
        # Check outputs
        if hasattr(archive.data, 'outputs'):
            outputs = archive.data.outputs
            print(f"✓ archive.data.outputs exists: {outputs is not None}")
            if outputs:
                print(f"✓ Number of outputs: {len(outputs)}")
                for i, output in enumerate(outputs):
                    print(f"  - Output {i}: {type(output).__name__}")
                    if hasattr(output, 'wall_start'):
                        print(f"    wall_start: {output.wall_start}")
                    if hasattr(output, 'wall_end'):
                        print(f"    wall_end: {output.wall_end}")

        # Check model_system
        if hasattr(archive.data, 'model_system'):
            model_systems = archive.data.model_system
            print(f"✓ archive.data.model_system exists: {model_systems is not None}")
            if model_systems:
                print(f"✓ Number of model_systems: {len(model_systems)}")

    # Check workflow2
    print(f"\n✓ archive.workflow2 exists: {hasattr(archive, 'workflow2') and archive.workflow2 is not None}")
    if hasattr(archive, 'workflow2') and archive.workflow2:
        workflow = archive.workflow2
        print(f"✓ Workflow type: {type(workflow).__name__}")
        print(f"✓ Workflow name: {workflow.name if hasattr(workflow, 'name') else 'N/A'}")

        if hasattr(workflow, 'tasks'):
            print(f"✓ Number of tasks: {len(workflow.tasks) if workflow.tasks else 0}")

        if hasattr(workflow, 'inputs'):
            print(f"✓ Number of inputs: {len(workflow.inputs) if workflow.inputs else 0}")

        if hasattr(workflow, 'outputs'):
            print(f"✓ Number of workflow outputs: {len(workflow.outputs) if workflow.outputs else 0}")

    print("\n" + "=" * 60)
    print("Diagnostic complete - check output above")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
