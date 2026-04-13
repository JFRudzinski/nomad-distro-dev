#!/usr/bin/env python3
"""Quick test to verify ABINIT geometry optimization normalizer fix."""

import sys
from nomad.datamodel import EntryArchive
from nomad.utils import get_logger
from nomad_simulation_parsers.parsers.abinit.parser import AbinitParser
from nomad_topology_normalizer.normalizers.results import ResultsNormalizer

LOGGER = get_logger(__name__)

def test_abinit():
    """Test ABINIT H2 geometry optimization."""
    print("Testing ABINIT H2 geometry optimization...")

    parser = AbinitParser()
    archive = EntryArchive()
    mainfile = 'packages/nomad-simulation-parsers/tests/data/abinit/H2/H2.out'

    try:
        # Parse
        print(f"  Parsing {mainfile}...")
        parser.parse(mainfile, archive, LOGGER)

        # Verify workflow exists
        if not archive.workflow2:
            print("  ❌ No workflow2 found")
            return False

        print(f"  ✅ Parsed workflow: {archive.workflow2.__class__.__name__}")

        # Normalize
        print("  Normalizing...")
        normalizer = ResultsNormalizer(archive)
        normalizer.normalize()

        # Check results
        if not archive.results:
            print("  ❌ No results section")
            return False

        if not hasattr(archive.results, 'properties') or not archive.results.properties:
            print("  ❌ No properties section")
            return False

        if not hasattr(archive.results.properties, 'geometry_optimization'):
            print("  ❌ No geometry_optimization property")
            return False

        geo_opt = archive.results.properties.geometry_optimization
        if not geo_opt:
            print("  ❌ geometry_optimization is None")
            return False

        print(f"  ✅ Created geometry_optimization section")
        print(f"     Type: {geo_opt.type if hasattr(geo_opt, 'type') else 'N/A'}")
        if hasattr(geo_opt, 'final_energy_difference') and geo_opt.final_energy_difference:
            print(f"     Final energy difference: {geo_opt.final_energy_difference}")
        if hasattr(geo_opt, 'final_force_maximum') and geo_opt.final_force_maximum:
            print(f"     Final force maximum: {geo_opt.final_force_maximum}")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_abinit()
    sys.exit(0 if success else 1)
