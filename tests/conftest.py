"""
Global pytest configuration and fixtures.
This file is automatically discovered by pytest and runs before any tests.
"""
import os

# Set environment variables for testing
os.environ["ENV"] = "test"

# Import any test fixtures that should be available to all tests
# from tests.fixtures import *  # Uncomment if you have common test fixtures
