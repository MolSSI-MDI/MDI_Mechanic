"""
MDI_Mechanic
A tool for testing and developing MDI-enabled projects.
"""

# Add imports here
from .commands import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
