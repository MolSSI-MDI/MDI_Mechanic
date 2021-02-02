"""
mdi_mechanic.py
A tool for testing and developing MDI-enabled projects.

Handles the primary functions
"""

####
import os
import shutil
import traceback
from . import report
from . import install
from .utils import tests as mtests
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



def command_startproject( args ):
    print("Starting a new MDI project")
    project_type = args.pop("projecttype")

    base_path = os.getcwd()
    package_path = ut.get_package_path()

    if project_type == "enginereport":
        project_path = os.path.join( package_path, "mdimechanic", "projects", "enginereport" )

        print("Starting an engine report project")

        yml_path = os.path.join( base_path, "mdimechanic.yml" )
        docker_path = os.path.join( base_path, "docker" )
        workflow_path = os.path.join( base_path, ".github" )
        gitignore_path = os.path.join( base_path, ".gitignore" )
        if os.path.exists( yml_path ) or os.path.exists( docker_path ) or os.path.exists( workflow_path ):
            raise Exception("This already appears to be an MDI project")

        yml_source = os.path.join( project_path, "mdimechanic.yml" )
        docker_source = os.path.join( project_path, "docker" )
        workflow_source = os.path.join( project_path, ".github" )
        gitignore_source = os.path.join( project_path, ".gitignore" )
        shutil.copyfile( yml_source, yml_path )
        shutil.copytree( docker_source, docker_path )
        shutil.copytree( workflow_source, workflow_path )
        shutil.copyfile( gitignore_source, gitignore_path )

    else:
        raise Exception("Unrecognized project type.")



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



def ci_push():
    # Note: These commands should be permitted to have non-zero exits
    os.system("git add ./.mdimechanic/ci_badge.md")
    os.system("git add ./README.md")
    os.system("git add ./report")
    os.system("git commit -m 'CI commit [ci skip]'")

    ret = os.system("git push -v > /dev/null 2>&1")
    if ret != 0:
        raise Exception("Unable to push changes to report")



def ci():
    # This function should only be run in the context of a Continuous Integration test
    mdimech_ci = os.getenv('MDIMECH_CI')
    is_ci = False
    if mdimech_ci is not None:
        if mdimech_ci == 'true':
            is_ci = True
    if not is_ci:
        raise Exception("The ci function should only be used within the context of a Continuous Integration test.")

    base_path = os.getcwd()

    # Configure Git
    ret = os.system("git config --global user.email 'action@github.com'")
    if ret != 0:
        raise Exception("Unable to configure Git user email")
    ret = os.system("git config --global user.name 'GitHub Action'")
    if ret != 0:
        raise Exception("Unable to configure Git user name")
    ret = os.system("git config pull.ff only")
    if ret != 0:
        raise Exception("Unable to configure Git pull")

    # Pull, in case this build was restarted
    ret = os.system("git pull")
    if ret != 0:
        raise Exception("Unable to perform a Git pull")

    # Confirm that the build can push
    ret = os.system("git remote -v")
    if ret != 0:
        raise Exception("Unable to check Git remotes")
    ret = os.system("git push -v > /dev/null 2>&1")
    if ret != 0:
        raise Exception("Unable to test git push")

    # Set the CI Badge
    badge_path = os.path.join( base_path, '.mdimechanic', 'ci_badge.md' )
    github_server_url = os.environ['GITHUB_SERVER_URL']
    github_repository = os.environ['GITHUB_REPOSITORY']
    #badge_text = "[![Build Status](${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/workflows/CI/badge.svg)](${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/)"
    badge_text = "[![Build Status](" + str(github_server_url) + "/" + str(github_repository) + "/workflows/CI/badge.svg)](" + str(github_server_url) + "/" + str(github_repository) + "/actions/)\n\n"
    with open( badge_path, 'w' ) as badge_file:
        badge_file.write( badge_text )

    # Build MDI Mechanic and the Engine
    ret = os.system("mdimechanic build")
    if ret != 0:
        #os.environ["MDI_REPORT_STATUS"] = "1"
        os.system("cat ./.mdimechanic/ci_badge.md ./README.md > temp && mv temp README.md")
        #os.system("bash ./.mdimechanic/push_changes.sh")
        ci_push()
        raise Exception("Unable to build MDI Mechanic and the Engine")

    # Generate the report
    ret = os.system("mdimechanic report")
    if ret != 0:
        #os.environ["MDI_REPORT_STATUS"] = "1"
        os.system("cat ./.mdimechanic/ci_badge.md ./README.md > temp && mv temp README.md")
        #os.system("bash ./.mdimechanic/push_changes.sh")
        ci_push()
        raise Exception("Unable to build MDI Mechanic and the Engine")

    # Push any changes to the report
    #os.environ["MDI_REPORT_STATUS"] = "0"
    #os.system("bash ./.mdimechanic/push_changes.sh")
    ci_push()

def command_rundriver( args ):
    report_dir = os.getcwd()
    print("Running an MDI test driver")
    driver_name = args.pop("driver_name")

    # Test the driver
    try:
        mtests.test_driver( driver_name, report_dir )
        print("Success: The driver ran to completion.")
    except:
        raise Exception("Error: Unable to verify that the engine was built.")

if __name__ == "__main__":
    # Do something if this file is invoked on its own
    print(canvas())
