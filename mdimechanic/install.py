import os
from .utils import utils as ut

def install_all( base_path ):
    package_path = ut.get_package_path()

    # Switch to the package directory
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
    docker_string = "docker run --rm -v " + str(base_path) + ":/repo -v " + str(package_path) + ":/MDI_Mechanic -it mdi_mechanic/lammps bash -c \"cd /repo/user/docker && ls && ./docker_install.sh\""
    os.system(docker_string)
