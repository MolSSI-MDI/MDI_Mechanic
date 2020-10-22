"""
MDI_Mechanic
A tool for testing and developing MDI-enabled projects.
"""

# Add imports here
from .mdi_mechanic import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
