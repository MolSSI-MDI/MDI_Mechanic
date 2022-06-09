"""
mdi_mechanic.py
A tool for testing and developing MDI-enabled projects.

Handles the primary functions
"""

####
import os
import shutil
import traceback
from . import cmd_report
from . import cmd_build
from . import cmd_run
from . import cmd_rundriver
from . import cmd_interactive
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
    cmd_report.generate_report( report_dir )



def command_build():
    print("Starting the installation")
    report_dir = os.getcwd()
    cmd_build.install_all( report_dir )



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
        #workflow_path = os.path.join( base_path, ".github" )
        gitignore_path = os.path.join( base_path, ".gitignore" )
        if os.path.exists( yml_path ) or os.path.exists( docker_path ):
            raise Exception("This already appears to be an MDI project")

        yml_source = os.path.join( project_path, "mdimechanic.yml" )
        docker_source = os.path.join( project_path, "docker" )
        workflow_source = os.path.join( project_path, ".github" )
        gitignore_source = os.path.join( project_path, ".gitignore" )
        shutil.copyfile( yml_source, yml_path )
        shutil.copytree( docker_source, docker_path )
        #shutil.copytree( workflow_source, workflow_path )
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

def command_run( args ):
    run_dir = os.getcwd()
    print("Running a custom calculation with MDI Mechanic.")
    script_name = args.pop("script_name")

    if script_name is None:
        raise Exception("Error: --name argument was not provided.")

    # Test the driver
    try:
        cmd_run.run( script_name, run_dir )
        print("Success: The driver ran to completion.")
    except:
        raise Exception("Error: The script did not complete successfully.")

def command_rundriver( args ):
    report_dir = os.getcwd()
    print("Running an MDI test driver.")
    driver_name = args.pop("driver_name")

    # Test the driver
    try:
        cmd_rundriver.test_driver( driver_name, report_dir )
        print("Success: The driver ran to completion.")
    except:
        raise Exception("Error: The test driver did not complete successfully.")

def command_interactive( ):
    run_dir = os.getcwd()

    try:
        cmd_interactive.start( run_dir )
        print("Success: Interactive session completed successfully.")
    except:
        raise Exception("Error: Interactive session did not complete successfully.")


if __name__ == "__main__":
    # Do something if this file is invoked on its own
    print(canvas())
