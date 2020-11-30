"""
mdi_mechanic.py
A tool for testing and developing MDI-enabled projects.

Handles the primary functions
"""

####
import os
import traceback
from . import report
from . import install
from .utils import utils as ut

def get_calling_path():
    # Get the name of the file that called the calling function
    caller_name = traceback.extract_stack()[-3][0]

    # Get the path to the file that called this function
    caller_path = os.path.realpath( caller_name )
    caller_directory = os.path.dirname( caller_path )
    
    return caller_directory
    


def command_report():
    print("Starting a report")
    report_dir = os.getcwd()
    report.generate_report( report_dir )



def command_build():
    print("Starting the installation")
    report_dir = os.getcwd()
    install.install_all( report_dir )



def canvas(with_attribution=True):
    """
    Placeholder function to show example docstring (NumPy format)

    Replace this function and doc string for your own project

    Parameters
    ----------
    with_attribution : bool, Optional, default: True
        Set whether or not to display who the quote is from

    Returns
    -------
    quote : str
        Compiled string including quote and optional attribution
    """

    quote = "The code is but a canvas to our imagination."
    if with_attribution:
        quote += "\n\t- Adapted from Henry David Thoreau"
    return quote

def ci():
    # This function should only be run in the context of a Continuous Integration test
    mdimech_ci = os.getenv('MDIMECH_CI')
    is_ci = False
    if mdimech_ci is not None:
        if mdimech_ci == 'true':
            is_ci = True
    print("is_ci: " + str(mdimech_ci))
    if not is_ci:
        raise Exception("The ci function should only be used within the context of a Continuous Integration test.")

    print("Running CI")

    base_path = os.getcwd()

    # Configure Git
    os.system("git config --global user.email 'action@github.com'")
    os.system("git config --global user.email 'action@github.com'")
    os.system("git config pull.ff only")

    # Confirm that the build can push
    os.system("git remote -v")
    os.system("git push -v > /dev/null 2>&1")

    # Pull, in case this build was restarted
    os.system("git pull")

    # Set the CI Badge
    badge_path = os.path.join( base_path, ',mdimechanic', 'ci_badge.md' )
    badge_text = "[![Build Status](${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/workflows/CI/badge.svg)](${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/)"
    with open( badge_path, 'w' ) as badge_file:
        badge_file.write( badge_text )

if __name__ == "__main__":
    # Do something if this file is invoked on its own
    print(canvas())
