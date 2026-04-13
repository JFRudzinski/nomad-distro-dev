#!/usr/bin/env python3
from nomad.client import parse

# Parse the test file
archive = parse('864.50_data/vasprun.xml')

# Check if data exists
has_data = hasattr(archive, 'data') and archive.data is not None
print(f'Has data: {has_data}')

if has_data:
    print(f'Data type: {type(archive.data).__name__}')
    if hasattr(archive.data, 'm_def'):
        print(f'Data m_def: {archive.data.m_def.name}')
    if hasattr(archive.data, 'model_system'):
        print(f'Has model_system: {archive.data.model_system is not None}')
        if archive.data.model_system:
            print(f'Number of model_systems: {len(archive.data.model_system)}')
else:
    print('ERROR: No data in archive!')

# Check other archive sections
print(f'\nHas workflow2: {hasattr(archive, "workflow2") and archive.workflow2 is not None}')
print(f'Has results: {hasattr(archive, "results") and archive.results is not None}')
