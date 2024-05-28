import os
import subprocess
import shutil
from .utils import utils as ut


def start( image_name, base_path ):
    mdimechanic_yaml = ut.get_mdimechanic_yaml( base_path )

    # Name of the image to run
    if image_name is None:
        # The user did not supply an image name, so try using a ":dev" tag
        image_name = mdimechanic_yaml['docker']['image_name'] + ":dev"

    # Find the location of .gitconfig file
    gitconfig_line = ""
    host_home_dir = os.path.expanduser('~')
    linux_location = os.path.join(host_home_dir, '.gitconfig')
    found_file = os.path.exists( linux_location )
    if found_file:
        gitconfig_line = " -v " + linux_location + ":/root/.gitconfig"
    else: # Check if this is Windows
        windows_location = os.path.join( str( os.getenv('USERPROFILE') ), ".gitconfig" )
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
        windows_location = os.path.join( str( os.getenv('USERPROFILE')), ".ssh" )
        found_file = os.path.exists( windows_location )
        if found_file:
            ssh_line = " -v " + windows_location + ":/root/.ssh"
    if not found_file:
        print("WARNING: MDI Mechanic was unable to locate a .ssh directory.  Git will not be fully functional within this interactive session.")

    # This script will be executed on entry to the image
    interactive_entry_script = '''#!/bin/bash -l
set -e
if [ ! -d "/repo" ]; then
  ln -s /mdi_shared /repo
fi
cd /repo
bash
'''

    # Write the entry script into the mounted volume
    interactive_entry_path = os.path.join( base_path, "docker", ".temp", "interactive_entry.sh" )
    os.makedirs(os.path.dirname(interactive_entry_path), exist_ok=True)
    ut.write_as_bytes( interactive_entry_script, interactive_entry_path )

    # Construct the command line to launch docker interactively
    run_line = "docker run --rm"
    run_line += " -v " + str( base_path ) + ":/mdi_shared"
    run_line += gitconfig_line
    run_line += ssh_line
    if 'gpu' in mdimechanic_yaml['docker']:
        run_line += " --gpus all"
    if 'extra_launch_options' in mdimechanic_yaml['docker']:
        run_line += " " + str(mdimechanic_yaml['docker']['extra_launch_options'])
    run_line += " -it " + str(image_name) + " bash /mdi_shared/docker/.temp/interactive_entry.sh"
    print("Interactive session run command: " + str(run_line))
    os.system(run_line)
