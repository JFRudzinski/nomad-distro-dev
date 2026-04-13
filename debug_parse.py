#!/usr/bin/env python3
"""Debug the annotation lookup during parsing."""



# Import the schema
from nomad_simulation_parsers.schema_packages import vasp
from nomad_simulations.schema_packages import general



logger = get_logger(__name__)

print("=" * 60)
print("Debug Annotation Lookup")
print("=" * 60)

print("\n1. Importing vasp schema...")
print(f"   vasp.XML_KEY = {vasp.XML_KEY}")

# Check if annotations are on the base class
print("\n2. Checking general.Simulation.outputs annotations:")
outputs_subsec = general.Simulation.outputs
if hasattr(outputs_subsec, 'm_annotations'):
    annots = outputs_subsec.m_annotations
    print(f"   Annotation keys: {list(annots.keys())}")
    if MAPPING_ANNOTATION_KEY in annots:
        mapping = annots[MAPPING_ANNOTATION_KEY]
        print(f"   Mapping keys: {list(mapping.keys())}")
        if vasp.XML_KEY in mapping:
            print(f"   ✓ {vasp.XML_KEY} -> {mapping[vasp.XML_KEY].mapper}")
        else:
            print(f"   ❌ {vasp.XML_KEY} not found in mapping!")
    else:
        print(f"   ❌ No '{MAPPING_ANNOTATION_KEY}' key!")

# Check if vasp.Simulation has the same outputs subsection
print("\n3. Checking vasp.Simulation.outputs:")
vasp_outputs = vasp.Simulation.outputs
print(f"   same as general.Simulation.outputs? {vasp_outputs is general.Simulation.outputs}")

# Create an instance and check
print("\n4. Creating vasp.Simulation() instance:")
sim = vasp.Simulation()
print(f"   m_def type: {type(sim.m_def).__name__}")
print(f"   m_def.name: {sim.m_def.name}")

# Check subsections on the instance's m_def
print("\n5. Checking subsections on instance m_def:")
for name, subsec in sim.m_def.all_sub_sections.items():
    if name in ['outputs', 'model_system']:
        annots = subsec.m_annotations.get(MAPPING_ANNOTATION_KEY, {})
        print(f"   {name}:")
        if annots:
            print(f"     Mapping keys: {list(annots.keys())}")
        else:
            print("     No mapping annotations")

print("\n" + "=" * 60)
