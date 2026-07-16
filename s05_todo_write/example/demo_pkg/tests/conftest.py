"""Pytest configuration for the local demo_pkg example tests."""

import sys
from pathlib import Path


EXAMPLE_ROOT = Path(__file__).resolve().parents[2]
if str(EXAMPLE_ROOT) not in sys.path:
    sys.path.insert(0, str(EXAMPLE_ROOT))
