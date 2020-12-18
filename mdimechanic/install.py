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
    with open(image_script_path, "w") as script_file:
        script_file.write( build_image_script )

    # Read the script to build the engine from the yaml file
    build_engine_lines = mdimechanic_yaml['docker']['build_engine']
    build_engine_script = "#!/bin/bash\nset -e\ncd /repo\n"
    for line in build_engine_lines:
        build_engine_script += line + '\n'

    # Write the script to build the engine
    engine_script_path = os.path.join( base_path, ".mdimechanic", ".temp", "build_engine.sh" )
    os.makedirs(os.path.dirname(engine_script_path), exist_ok=True)
    with open(engine_script_path, "w") as script_file:
        script_file.write( build_engine_script )

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
#                                    "cd /MDI_Mechanic/mdimechanic/docker/ssh && ssh-keygen -t rsa -b 4096 -C \"\" -f id_rsa.mpi -N \'\'"],
                                  "cd /MDI_Mechanic/mdimechanic/docker/ssh && ../../utils/generate_ssh_keys.sh"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ssh_tup = ssh_proc.communicate()
    if ssh_proc.returncode != 0:
        ut.docker_error( ssh_tup, "Error during ssh key generation." )

    # Build the engine image
    build_command = "docker build -t " + mdimechanic_yaml['docker']['image_name'] + " docker"
    ret = os.system( build_command )
    if ret != 0:
        raise Exception("Unable to build the engine image")

    # Build the engine, within its Docker image
    docker_string = "docker run --rm -v " + str(base_path) + ":/repo -v " + str(package_path) + ":/MDI_Mechanic " + mdimechanic_yaml['docker']['image_name'] + " bash -c \"cd /repo && bash .mdimechanic/.temp/build_engine.sh \""
    ret = os.system(docker_string)
    if ret != 0:
        raise Exception("Unable to build the engine")
