#!/usr/bin/env python3
"""Quick validation that geometry optimization normalizer fix works."""

import sys
import logging
from nomad.datamodel import EntryArchive
from nomad_simulations.schema_packages.workflow import GeometryOptimization as SimGeometryOptimizationWorkflow
from nomad_simulations.schema_packages.workflow import GeometryOptimizationMethod as SimGeometryOptimizationMethod
from nomad_simulations.schema_packages.workflow import GeometryOptimizationResults as SimGeometryOptimizationResults
from nomad_simulations.schema_packages.numerical_settings import EnergyConvergenceTarget, ForceConvergenceTarget
from nomad_simulations.schema_packages.outputs import Outputs
from nomad_simulations.schema_packages.model_system import ModelSystem, AtomicCell
from nomad.units import ureg

# Add the normalizer to path
sys.path.insert(0, '/home/jfrudzinski/work/soft/nomad-distro-dev-topology-normalizer-2026-02/packages/nomad-topology-normalizer/src')

from nomad_topology_normalizer.normalizers.results import ResultsNormalizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_geometry_optimization_new_schema():
    """Test that new schema geometry optimization doesn't crash."""
    archive = EntryArchive()
    
    # Create a simple model system
    system = ModelSystem()
    system.cell = [AtomicCell()]
    
    # Create outputs
    output1 = Outputs()
    output1.model_system_ref = system
    output2 = Outputs()
    output2.model_system_ref = system
    
    # Set up archive.data with outputs
    archive.data = type('Data', (), {
        'outputs': [output1, output2],
        'model_system': [system]
    })()
    
    # Create workflow
    workflow = SimGeometryOptimizationWorkflow()
    workflow.method = SimGeometryOptimizationMethod(optimization_type='atomic')
    workflow.method.convergence_targets = [
        EnergyConvergenceTarget(threshold=1e-6 * ureg.eV),
        ForceConvergenceTarget(threshold=1e-5 * ureg.newton),
    ]
    workflow.results = SimGeometryOptimizationResults(
        final_energy_difference=2e-6 * ureg.eV,
        final_force_maximum=4e-5 * ureg.newton,
        final_displacement_maximum=1e-12 * ureg.meter,
    )
    
    archive.workflow2 = workflow
    
    # Normalize
    normalizer = ResultsNormalizer()
    try:
        normalizer.normalize(archive, logger)
        logger.info("✅ Normalization succeeded without crash!")
        
        # Check results
        if archive.results and archive.results.properties:
            geo_opt = archive.results.properties.geometry_optimization
            if geo_opt:
                logger.info(f"✅ geometry_optimization section created")
                logger.info(f"   - type: {geo_opt.type}")
                logger.info(f"   - trajectory: {geo_opt.trajectory if hasattr(geo_opt, 'trajectory') else 'N/A'}")
                logger.info(f"   - system_optimized: {geo_opt.system_optimized if hasattr(geo_opt, 'system_optimized') else 'N/A'}")
            else:
                logger.warning("⚠️  geometry_optimization section not created")
        else:
            logger.warning("⚠️  No results.properties created")
            
    except Exception as e:
        logger.error(f"❌ Normalization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = test_geometry_optimization_new_schema()
    sys.exit(0 if success else 1)
