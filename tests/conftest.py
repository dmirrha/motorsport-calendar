"""
Global pytest configuration and fixtures.
This file is automatically discovered by pytest and runs before any tests.
"""
import os
import sys
from pathlib import Path

# Add the project root and src to the Python path
project_root = str(Path(__file__).parent.parent)
src_dir = os.path.join(project_root, 'src')

# Add to path if not already there
for path in [project_root, src_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Set environment variables for testing
os.environ["ENV"] = "test"

# Configure PYTHONPATH for tests
os.environ["PYTHONPATH"] = ":".join([
    os.environ.get("PYTHONPATH", ""),
    project_root,
    src_dir
]).strip(":")

# Import any test fixtures that should be available to all tests
# from tests.fixtures import *  # Uncomment if you have common test fixtures
