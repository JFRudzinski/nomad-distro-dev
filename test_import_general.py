#!/usr/bin/env python3
"""Test if importing general.Simulation causes a hang."""

import sys

print("Test: Importing general.Simulation", file=sys.stderr, flush=True)

# This is what we're now doing inside write_to_archive
from nomad_simulations.schema_packages.general import Simulation

print("Success! Simulation imported", file=sys.stderr, flush=True)
print(f"Simulation class: {Simulation}")
