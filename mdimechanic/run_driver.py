import mdi
import os
import sys
import utils.utils as ut

# Path to this file
file_path = os.path.dirname(os.path.realpath(__file__))

# Path to the top-level directory
base_path = file_path + "/../.."
compose_path = ut.get_compose_path( "tcp" )

docker_file = str(base_path) + '/MDI_Mechanic/.temp/docker_mdi_mechanic.sh'
docker_lines = [ "#!/bin/bash\n",
                 "\n",
                 "# Exit if any command fails\n",
                 "\n",
                 "cd repo/user/dummy\n",
                 "python min_driver.py -mdi \'-role DRIVER -name driver -method TCP -port 8021\'\n"]
os.makedirs(os.path.dirname(docker_file), exist_ok=True)
with open(docker_file, 'w') as file:
    file.writelines( docker_lines )

working_dir = str(base_path) + "/user/mdi_tests/test1"
os.system("rm -rf " + str(base_path) + "/user/mdi_tests/.work")
os.system("cp -r " + str(working_dir) + " " + str(base_path) + "/user/mdi_tests/.work")
#os.chdir(str(base_path) + "/MDI_Mechanic/docker")
os.chdir( compose_path )

ret = os.system("docker-compose up --exit-code-from mdi_mechanic --abort-on-container-exit")
assert ret == 0

ret = os.system("docker-compose down")
assert ret == 0
