#!/usr/bin/env python3
"""Test that parser entry points can load without circular import errors."""

import sys

print("=" * 60)
print("Testing Parser Entry Point Loading")
print("=" * 60)

try:
    # Test loading the entry point system
    print("\nImporting nomad.parsing.parsers...")
    from nomad.parsing import parsers

    print("✓ Successfully imported nomad.parsing.parsers")

    # Try to get the exciting parser
    print("\nLooking for exciting parser...")
    exciting_found = False
    for parser_name, parser_instance in parsers.items():
        if 'exciting' in parser_name.lower():
            print(f"✓ Found parser: {parser_name}")
            print(f"  Type: {type(parser_instance)}")
            exciting_found = True
            break

    if not exciting_found:
        print("⚠ Warning: exciting parser not found in loaded parsers")

    print("\n" + "=" * 60)
    print("✅ SUCCESS: No circular import errors!")
    print("=" * 60)

except AssertionError as e:
    print(f"\n❌ ASSERTION ERROR: {str(e)}")
    sys.exit(1)
except ImportError as e:
    print(f"\n❌ IMPORT ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
