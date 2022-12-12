import os
import subprocess
import shutil
from .utils import utils as ut


def start( base_path ):
    mdimechanic_yaml = ut.get_mdimechanic_yaml( base_path )

    # Name of the image to run
    image_name = mdimechanic_yaml['docker']['image_name']

    # Find the location of .gitconfig file
    gitconfig_line = ""
    host_home_dir = os.path.expanduser('~')
    linux_location = os.path.join(host_home_dir, '.gitconfig')
    found_file = os.path.exists( linux_location )
    if found_file:
        gitconfig_line = " -v " + linux_location + ":/root/.gitconfig"
    else: # Check if this is Windows
        windows_location = os.path.join( str( os.environ['USERPROFILE'] ), ".gitconfig" )
        found_file = os.path.exists( windows_location )
        if found_file:
            gitconfig_line = " -v " + windows_location + ":/root/.gitconfig"
    if not found_file:
        print("WARNING: MDI Mechanic was unable to locate a .gitconfig file.  Git will not be fully functional within this interactive session.")

    # Find the location of the .ssh directory
    ssh_line = ""
    host_home_dir = os.path.expanduser('~')
    linux_location = os.path.join(host_home_dir, '.ssh')
    found_file = os.path.exists( linux_location )
    if found_file:
        ssh_line = " -v " + linux_location + ":/root/.ssh"
    else: # Check if this is Windows
        windows_location = os.path.join( str( os.environ['USERPROFILE'] ), ".ssh" )
        found_file = os.path.exists( windows_location )
        if found_file:
            ssh_line = " -v " + windows_location + ":/root/.ssh"
    if not found_file:
        print("WARNING: MDI Mechanic was unable to locate a .ssh directory.  Git will not be fully functional within this interactive session.")

    # This script will be executed on entry to the image
    interactive_entry_script = '''#!/bin/bash
set -e
cd /repo
bash
'''

    # Write the entry script into the mounted volume
    interactive_entry_path = os.path.join( base_path, "docker", ".temp", "interactive_entry.sh" )
    os.makedirs(os.path.dirname(interactive_entry_path), exist_ok=True)
    ut.write_as_bytes( interactive_entry_script, interactive_entry_path )

    # Construct the command line to launch docker interactively
    run_line = "docker run --rm"
    run_line += " -v " + str( base_path ) + ":/repo"
    run_line += gitconfig_line
    run_line += ssh_line
    run_line += " -it " + str(image_name) + " bash /repo/docker/.temp/interactive_entry.sh"
    os.system(run_line)
