#!/usr/bin/env python3
"""Check if mapping annotations are present on the Simulation class."""

from nomad_simulation_parsers.schema_packages import vasp
from nomad_simulations.schema_packages import general

print("=" * 60)
print("Mapping Annotations Check")
print("=" * 60)

# Check base class
print("\ngeneral.Simulation.outputs annotations:")
outputs_annotations = general.Simulation.outputs.m_annotations
print(f"  Has 'mapping' key: {'mapping' in outputs_annotations}")
if 'mapping' in outputs_annotations:
    mapping = outputs_annotations['mapping']
    print(f"  Mapping keys: {list(mapping.keys())}")
    if vasp.XML_KEY in mapping:
        print(f"  {vasp.XML_KEY} mapper: {mapping[vasp.XML_KEY].mapper}")

# Check if vasp.Simulation inherits it
print("\nvasp.Simulation class:")
print(f"  Is subclass of general.Simulation: {issubclass(vasp.Simulation, general.Simulation)}")
print(f"  Has 'outputs' subsection: {hasattr(vasp.Simulation, 'outputs')}")

# Create an instance and check
sim = vasp.Simulation()
print("\nvasp.Simulation() instance:")
print(f"  Has outputs attribute: {hasattr(sim, 'outputs')}")
print(f"  outputs value: {sim.outputs}")
print(f"  outputs type: {type(sim.outputs)}")

# Check the m_def
print("\nvasp.Simulation.m_def:")
print(f"  Type: {type(vasp.Simulation.m_def)}")
for subsec_name, subsec in vasp.Simulation.m_def.all_sub_sections.items():
    if subsec_name == 'outputs':
        print("  Found 'outputs' subsection:")
        print(f"    Type: {type(subsec)}")
        print(f"    Annotations: {'mapping' in subsec.m_annotations}")
        if 'mapping' in subsec.m_annotations:
            print(f"    Mapping keys: {list(subsec.m_annotations['mapping'].keys())}")

print("=" * 60)
