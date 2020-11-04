import os
import yaml
from .utils import utils as ut

def install_all( base_path ):
    # Read the yaml file
    yaml_path = os.path.join( base_path, "mdimechanic.yml" )
    with open(yaml_path, "r") as yaml_file:
        mdimechanic_yaml = yaml.load(yaml_file, Loader=yaml.FullLoader)
    build_lines = mdimechanic_yaml['docker']['build_engine']
    build_script = ''
    for line in build_lines:
        build_script += line + '\n'

    script_path = os.path.join( base_path, ".mdimechanic", ".temp", "build_engine.sh" )
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    with open(script_path, "w") as script_file:
        script_file.write( build_script )
    print("YAML: " + str(build_script) )

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

    # Build the engine image
    ret = os.system("docker build -t mdi_mechanic/lammps user/docker")
    if ret != 0:
        raise Exception("Unable to build the engine image")

    # Build the engine, within its Docker image
    docker_string = "docker run --rm -v " + str(base_path) + ":/repo -v " + str(package_path) + ":/MDI_Mechanic -it mdi_mechanic/lammps bash -c \"cd /repo && bash .mdimechanic/.temp/build_engine.sh \""
    os.system(docker_string)
