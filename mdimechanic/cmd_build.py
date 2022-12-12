import os
import subprocess
from .utils import utils as ut

def install_all( base_path ):
    # Read the yaml file
    mdimechanic_yaml = ut.get_mdimechanic_yaml( base_path )

    # Read the script to build the image from the yaml file
    build_image_lines = mdimechanic_yaml['docker']['build_image']
    build_image_script = "#!/bin/bash\nset -e\n"
    for line in build_image_lines:
        build_image_script += line + '\n'

    # Write the script to build the image
    image_script_path = os.path.join( base_path, "docker", ".temp", "build_image.sh" )
    os.makedirs(os.path.dirname(image_script_path), exist_ok=True)
    ut.write_as_bytes( build_image_script, image_script_path )

    # Read the script to build the engine from the yaml file
    build_engine_lines = mdimechanic_yaml['docker']['build_engine']
    build_engine_script = "#!/bin/bash\nset -e\ncd /repo\n"
    for line in build_engine_lines:
        build_engine_script += line + '\n'

    # Write the script to build the engine
    engine_script_path = os.path.join( base_path, ".mdimechanic", ".temp", "build_engine.sh" )
    os.makedirs(os.path.dirname(engine_script_path), exist_ok=True)
    ut.write_as_bytes( build_engine_script, engine_script_path )

    # Switch to the package directory
    package_path = ut.get_package_path()
    os.chdir(package_path)

    # Build the MDI base image
    ret = os.system("docker build -t mdi/base mdimechanic/docker/base")
    if ret != 0:
        raise Exception("Unable to build the MDI Mechanic image")

    # Build the MDI Mechanic image
    ret = os.system("docker build -t mdi_mechanic/mdi_mechanic mdimechanic/docker")
    if ret != 0:
        raise Exception("Unable to build the MDI Mechanic image")

    # Switch to the base directory
    os.chdir(base_path)

    # Generate ssh keys within the MDI Mechanic image
    ssh_proc = subprocess.Popen( ["docker", "run", "--rm",
                                    "-v", str(base_path) + ":/repo",
                                    "-v", str(package_path) + ":/MDI_Mechanic",
                                    "mdi_mechanic/mdi_mechanic",
                                    "bash", "-c",
                                    "cd /MDI_Mechanic/mdimechanic/docker/ssh && bash ../../utils/generate_ssh_keys.sh"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ssh_tup = ssh_proc.communicate()
    if ssh_proc.returncode != 0:
        ut.docker_error( ssh_tup, "Error during ssh key generation." )

    # Build the engine image
    build_command = "docker build -t " + mdimechanic_yaml['docker']['image_name'] + " docker"
    ret = os.system( build_command )
    if ret != 0:
        raise Exception("Unable to build the engine image")

    # This script will be executed on entry to the image
    build_entry_script = '''#!/bin/bash
set -e
cd /repo
bash .mdimechanic/.temp/build_engine.sh
'''

    # Write the entry script into the mounted volume
    build_entry_path = os.path.join( base_path, "docker", ".temp", "build_entry.sh" )
    os.makedirs(os.path.dirname(build_entry_path), exist_ok=True)
    ut.write_as_bytes( build_entry_script, build_entry_path )

    # Build the engine, within its Docker image
    docker_string = "docker run --rm -v " + str(base_path) + ":/repo -v " + str(package_path) + ":/MDI_Mechanic " + mdimechanic_yaml['docker']['image_name'] + " bash /repo/docker/.temp/build_entry.sh"
    ret = os.system(docker_string)
    if ret != 0:
        raise Exception("Unable to build the engine")
