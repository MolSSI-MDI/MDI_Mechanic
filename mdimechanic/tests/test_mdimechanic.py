"""
Unit and regression test for the MDI_Mechanic package.
"""

# Import package, test suite, and other packages as needed
import mdimechanic
import pytest
import sys

def test_mdimechanic_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "mdimechanic" in sys.modules
