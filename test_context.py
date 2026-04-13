#!/usr/bin/env python3
"""Quick test to check context"""

from nomad.datamodel import EntryArchive
from nomad_simulations.schema_packages.general import Simulation
from nomad_simulations.schema_packages.outputs import Outputs
from nomad_simulations.schema_packages.model_system import ModelSystem

# Test structure like parser creates
sim = Simulation()
ms = ModelSystem()
out = Outputs()

sim.model_system = [ms]
sim.outputs = [out]

print(f"Simulation.m_context: {sim.m_context}")
print(f"Simulation.m_root(): {sim.m_root()}")
print(f"ModelSystem.m_root(): {ms.m_root()}")
print(f"Outputs.m_root(): {out.m_root()}")
print(f"Outputs.m_root() == ModelSystem.m_root(): {out.m_root() == ms.m_root()}")
print()
print(f"HasContext (Outputs): {getattr(out.m_root(), 'm_context', None) is not None}")
print(f"HasContext (ModelSystem): {getattr(ms.m_root(), 'm_context', None) is not None}")
