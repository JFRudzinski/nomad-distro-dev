"""Test script to verify ABINIT geometry optimization normalizer mapping."""
from nomad.datamodel import EntryArchive
from nomad.utils import get_logger
from nomad_simulation_parsers.parsers.abinit.parser import AbinitParser
from nomad_topology_normalizer.normalizers.results import ResultsNormalizer

LOGGER = get_logger(__name__)


def test_abinit_file(mainfile: str, description: str):
    """Test parsing and normalization of a single ABINIT file."""
    print(f"\n{'='*80}")
    print(f"Testing: {description}")
    print(f"File: {mainfile}")
    print('='*80)

    # Parse ABINIT file
    parser = AbinitParser()
    archive = EntryArchive()

    print(f"\nParsing {mainfile}...")
    parser.parse(mainfile, archive, LOGGER)

    # Verify workflow2 exists
    if archive.workflow2 is None:
        print("⚠️  workflow2 is None")
        return False

    workflow = archive.workflow2
    print(f"\n--- Workflow Information ---")
    print(f"Workflow type: {workflow.m_def.name}")
    print(f"Workflow class: {workflow.__class__.__name__}")

    is_geo_opt = workflow.__class__.__name__ == 'GeometryOptimization'
    print(f"Is GeometryOptimization: {is_geo_opt}")

    # Check method
    if workflow.method:
        print(f"\n--- Method Information ---")
        print(f"Method type: {workflow.method.m_def.name}")
        print(f"Method class: {workflow.method.__class__.__name__}")
        if hasattr(workflow.method, 'optimization_method'):
            print(f"Optimization method: {workflow.method.optimization_method}")
        if hasattr(workflow.method, 'optimization_type'):
            print(f"Optimization type: {workflow.method.optimization_type}")
        if hasattr(workflow.method, 'type'):
            print(f"Type: {workflow.method.type}")
    else:
        print("\n⚠️  No method section")

    # Check results
    if workflow.results:
        print(f"\n--- Results Information ---")
        print(f"Results type: {workflow.results.m_def.name}")
        print(f"Results class: {workflow.results.__class__.__name__}")
        results_quantities = workflow.results.m_def.all_quantities
        print(f"Results quantities: {sorted(results_quantities.keys())}")

        # Check for convergence values
        if 'final_energy_difference' in results_quantities:
            print(f"  final_energy_difference: {workflow.results.final_energy_difference}")
        if 'final_force_maximum' in results_quantities:
            print(f"  final_force_maximum: {workflow.results.final_force_maximum}")
        if 'final_displacement_maximum' in results_quantities:
            print(f"  final_displacement_maximum: {workflow.results.final_displacement_maximum}")
    else:
        print("\n⚠️  No results section")

    # Check tasks
    if hasattr(workflow, 'tasks') and workflow.tasks:
        print(f"\n--- Tasks Information ---")
        print(f"Number of tasks: {len(workflow.tasks)}")
        if workflow.tasks and workflow.tasks[0].outputs:
            print(f"Task 0 has {len(workflow.tasks[0].outputs)} outputs")
    else:
        print("\n⚠️  No tasks")

    print("\n--- Running topology normalizer ---")

    # Run ResultsNormalizer
    normalizer = ResultsNormalizer(archive)
    normalizer.normalize()

    # Check if results section was populated
    success = False
    if archive.results:
        print("\n✅ Results section populated!")

        if hasattr(archive.results, 'properties') and archive.results.properties:
            if hasattr(archive.results.properties, 'geometry_optimization'):
                geo_opt = archive.results.properties.geometry_optimization
                if geo_opt:
                    print("✅ Geometry optimization section created!")
                    print(f"  Type: {type(geo_opt).__name__}")
                    if hasattr(geo_opt, 'trajectory') and geo_opt.trajectory:
                        print(f"  Trajectory: {len(geo_opt.trajectory)} items")
                    if hasattr(geo_opt, 'system_optimized') and geo_opt.system_optimized:
                        print(f"  System optimized: {geo_opt.system_optimized}")
                    if hasattr(geo_opt, 'final_energy_difference') and geo_opt.final_energy_difference:
                        print(f"  Final energy difference: {geo_opt.final_energy_difference}")
                    if hasattr(geo_opt, 'final_force_maximum') and geo_opt.final_force_maximum:
                        print(f"  Final force maximum: {geo_opt.final_force_maximum}")
                    if hasattr(geo_opt, 'final_displacement_maximum') and geo_opt.final_displacement_maximum:
                        print(f"  Final displacement maximum: {geo_opt.final_displacement_maximum}")
                    success = True
                else:
                    print("❌ geometry_optimization is None!")
            else:
                print("❌ No geometry_optimization in properties!")
        else:
            print("❌ No properties section in results!")
    else:
        print("\n❌ No results section created!")

    print(f"\n--- Test {'PASSED ✅' if success else 'FAILED ❌'} ---")
    return success


if __name__ == '__main__':
    print("Testing ABINIT Geometry Optimization Normalizer")
    print("=" * 80)

    # Test 1: Parser test data (H2 geometry optimization)
    test1 = test_abinit_file(
        'packages/nomad-simulation-parsers/tests/data/abinit/H2/H2.out',
        'Parser Test Data - H2 Geometry Optimization'
    )

    # Test 2: Distribution test data (run.abo)
    test2 = test_abinit_file(
        'test_data/run.abo',
        'Distribution Test Data - Full Cell Optimization'
    )

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Test 1 (H2 parser data): {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"Test 2 (Distribution data): {'✅ PASSED' if test2 else '❌ FAILED'}")
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if (test1 and test2) else '❌ SOME TESTS FAILED'}")

