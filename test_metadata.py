#!/usr/bin/env python3
"""Quick test to check archive metadata"""

from nomad.datamodel import EntryArchive

archive = EntryArchive()
print(f"archive.metadata: {getattr(archive, 'metadata', None)}")
print(f"Has metadata: {getattr(archive, 'metadata', None) is not None}")
print(f"archive.m_context: {getattr(archive, 'm_context', None)}")
print(f"Has m_context: {getattr(archive, 'm_context', None) is not None}")
