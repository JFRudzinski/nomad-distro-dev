#!/usr/bin/env python3
"""Simple check for mapping annotations."""
import sys
print("Starting imports...", file=sys.stderr)

try:
    print("Importing vasp schema...", file=sys.stderr)
    from nomad_simulation_parsers.schema_packages import vasp
    print(f"✓ vasp.XML_KEY = {vasp.XML_KEY}", file=sys.stderr)
    
    print("Importing general schema...", file=sys.stderr)
    from nomad_simulations.schema_packages import general
    print("✓ general.Simulation imported", file=sys.stderr)
    
    print("\nChecking annotations...", file=sys.stderr)
    outputs_subsec = general.Simulation.outputs
    print(f"Outputs subsection type: {type(outputs_subsec)}", file=sys.stderr)
    print(f"Has m_annotations: {hasattr(outputs_subsec, 'm_annotations')}", file=sys.stderr)
    
    if hasattr(outputs_subsec, 'm_annotations'):
        annots = outputs_subsec.m_annotations
        print(f"Annotation keys: {list(annots.keys())}", file=sys.stderr)
        if 'mapping' in annots:
            mapping = annots['mapping']
            print(f"✓ Mapping annotation found with keys: {list(mapping.keys())}")
        else:
            print("❌ No mapping annotation!")
    else:
        print("❌ No m_annotations attribute!")
        
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
