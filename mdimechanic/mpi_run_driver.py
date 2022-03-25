#import mdi
import os
import sys
import utils.utils as ut

# Path to this file
file_path = os.path.dirname(os.path.realpath(__file__))

# Path to the top-level directory
base_path = file_path + "/../.."
compose_path = ut.get_compose_path( "mpi" )

docker_file = str(base_path) + '/MDI_Mechanic/.temp/docker_mdi_mechanic.sh'

#docker_lines = [ "#!/bin/bash\n",
#                 "\n",
#                 "cd /repo\n",
#                 "cd user/dummy\n",
#                 "python min_driver.py -mdi \'-role DRIVER -name driver -method MPI\'\n"]
script = '''#!/bin/bash

cd /repo
cd user/dummy
python min_driver.py -mdi \'-role DRIVER -name driver -method MPI\'
'''

os.makedirs(os.path.dirname(docker_file), exist_ok=True)
ut.write_as_bytes( script, docker_file )

docker_file = str(base_path) + '/MDI_Mechanic/.temp/docker_mdi_engine.sh'
#docker_lines = [ "#!/bin/bash\n",
#                 "\n",
#                 "cd /repo\n",
#                 "cd user/mdi_tests/.work\n",
#                 "export MDI_OPTIONS='-role ENGINE -name TESTCODE -method MPI'\n",
#                 "./run.sh\n"]
script = '''#!/bin/bash

cd /repo
cd user/mdi_tests/.work
export MDI_OPTIONS='-role ENGINE -name TESTCODE -method MPI'
./run.sh
'''
os.makedirs(os.path.dirname(docker_file), exist_ok=True)
ut.write_as_bytes( script, docker_file )

# Copy the files
working_dir = str(base_path) + "/user/mdi_tests/test1"
os.system("rm -rf " + str(base_path) + "/user/mdi_tests/.work")
os.system("cp -r " + str(working_dir) + " " + str(base_path) + "/user/mdi_tests/.work")

#os.chdir(str(base_path) + "/MDI_Mechanic/docker_mpi")
os.chdir( compose_path )
os.system("docker-compose down")
os.system("docker-compose up -d")
os.system("docker-compose exec --user mpiuser mdi_mechanic mpiexec -configfile /repo/MDI_Mechanic/docker/mpi/mdi_appfile")
os.system("docker-compose down")

#working_dir = str(base_path) + "/user/mdi_tests/test1"
#os.system("rm -rf " + str(base_path) + "/user/mdi_tests/.work")
#os.system("cp -r " + str(working_dir) + " " + str(base_path) + "/user/mdi_tests/.work")
#os.chdir(str(base_path) + "/MDI_Mechanic/docker")

#ret = os.system("docker-compose up --exit-code-from mdi_mechanic --abort-on-container-exit")
#assert ret == 0

#ret = os.system("docker-compose down")
#assert ret == 0
