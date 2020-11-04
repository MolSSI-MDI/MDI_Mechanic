import os
import subprocess
import shutil
from .utils import format_return, insert_list, docker_error, get_mdi_standard, get_compose_path, get_package_path, get_mdimechanic_yaml



def test_validate( base_path ):
    # Get the base directory
    package_path = get_package_path()

    # Read the yaml script for validating the engine build
    mdimechanic_yaml = get_mdimechanic_yaml( base_path )
    validate_engine_lines = mdimechanic_yaml['docker']['validate_engine']
    validate_engine_script = ''
    for line in validate_engine_lines:
        validate_engine_script += line + '\n'

    # Write the script to validate the engine build
    validate_script_path = os.path.join( base_path, ".mdimechanic", ".temp", "validate_engine.sh" )
    os.makedirs(os.path.dirname(validate_script_path), exist_ok=True)
    with open(validate_script_path, "w") as script_file:
        script_file.write( validate_engine_script )

    # Run the test
    test_proc = subprocess.Popen( ["docker", "run", "--rm",
                                   "-v", str(base_path) + ":/repo",
                                   "-v", str(package_path) + ":/MDI_Mechanic",
                                   "-it", "mdi_mechanic/lammps",
                                   "bash", "-c",
                                   "cd /repo && bash .mdimechanic/.temp/validate_engine.sh"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    test_tup = test_proc.communicate()
    test_out = format_return(test_tup[0])
    test_err = format_return(test_tup[1])
    if test_proc.returncode != 0:
        docker_error( test_tup, "Build validation script returned non-zero value." )


def test_engine( base_path ):
    # Get the base directory
    #file_path = os.path.dirname(os.path.realpath(__file__))
    #base_path = os.path.dirname( os.path.dirname( os.path.dirname( file_path ) ) )
    package_path = get_package_path()

    # Prepare the working directory
    src_path = os.path.join( base_path, "user", "engine_tests", "test1" )
    dst_path = os.path.join( base_path, "user", "engine_tests", ".work" )
    if os.path.isdir( dst_path ):
        shutil.rmtree( dst_path )
    shutil.copytree( src_path, dst_path )

    # Run the test
    test_proc = subprocess.Popen( ["docker", "run", "--rm",
                                   "-v", str(base_path) + ":/repo",
                                   "-v", str(package_path) + ":/MDI_Mechanic",
                                   "-it", "mdi_mechanic/lammps",
                                   "bash", "-c",
                                   "cd /repo/user/engine_tests/.work && ./run.sh"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    test_tup = test_proc.communicate()
    test_out = format_return(test_tup[0])
    test_err = format_return(test_tup[1])
    if test_proc.returncode != 0:
        raise Exception("Engine test script returned non-zero value.")

def test_min( base_path ):
    # Get the base directory
    #file_path = os.path.dirname(os.path.realpath(__file__))
    #base_path = os.path.dirname( os.path.dirname( os.path.dirname( file_path ) ) )
    #docker_path = os.path.join( base_path, "MDI_Mechanic", "docker" )
    docker_path = get_compose_path( "tcp" )

    # Write the run script for MDI Mechanic
    docker_file = str(base_path) + '/MDI_Mechanic/.temp/docker_mdi_mechanic.sh'
    docker_lines = [ "#!/bin/bash\n",
                     "\n",
                     "# Exit if any command fails\n",
                     "\n",
                     "cd /MDI_Mechanic/mdimechanic/drivers\n",
                     "python min_driver.py -command \'<NAME\' -nreceive \'MDI_NAME_LENGTH\' -rtype \'MDI_CHAR\' -mdi \'-role DRIVER -name driver -method TCP -port 8021\'\n"]
    os.makedirs(os.path.dirname(docker_file), exist_ok=True)
    with open(docker_file, 'w') as file:
        file.writelines( docker_lines )

    # Write the run script for the engine
    docker_file = str(base_path) + '/MDI_Mechanic/.temp/docker_mdi_engine.sh'
    docker_lines = [ "#!/bin/bash\n",
                     "\n",
                     "# Exit if any command fails\n",
                     "\n",
                     "cd /repo/user/mdi_tests/.work\n",
                     "export MDI_OPTIONS=\'-role ENGINE -name TESTCODE -method TCP -hostname mdi_mechanic -port 8021\'\n",
                     "./run.sh\n"]
    os.makedirs(os.path.dirname(docker_file), exist_ok=True)
    with open(docker_file, 'w') as file:
        file.writelines( docker_lines )

    # Prepare the working directory
    src_path = os.path.join( base_path, "user", "mdi_tests", "test1" )
    dst_path = os.path.join( base_path, "user", "mdi_tests", ".work" )
    if os.path.isdir( dst_path ):
        shutil.rmtree( dst_path )
    shutil.copytree( src_path, dst_path )

    # Create the docker environment
    docker_env = os.environ
    docker_env['MDIMECH_WORKDIR'] = base_path
    docker_env['MDIMECH_PACKAGEDIR'] = get_package_path()

    # Run "docker-compose up"
    up_proc = subprocess.Popen( ["docker-compose", "up", "--exit-code-from", "mdi_mechanic", "--abort-on-container-exit"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                cwd=docker_path, env=docker_env )
    up_tup = up_proc.communicate()
    up_out = format_return(up_tup[0])
    up_err = format_return(up_tup[1])

    # Run "docker-compose down"
    down_proc = subprocess.Popen( ["docker-compose", "down"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  cwd=docker_path, env=docker_env )
    down_tup = down_proc.communicate()
    down_out = format_return(down_tup[0])
    down_err = format_return(down_tup[1])

    assert up_proc.returncode == 0
    assert down_proc.returncode == 0

def test_unsupported( base_path ):
    # Get the base directory
    #file_path = os.path.dirname(os.path.realpath(__file__))
    #base_path = os.path.dirname( os.path.dirname( os.path.dirname( file_path ) ) )
    docker_path = get_compose_path( "tcp" )

    # Write the run script for MDI Mechanic
    docker_file = str(base_path) + '/MDI_Mechanic/.temp/docker_mdi_mechanic.sh'
    docker_lines = [ "#!/bin/bash\n",
                     "\n",
                     "# Exit if any command fails\n",
                     "\n",
                     "cd /MDI_Mechanic/mdimechanic/drivers\n",
                     "python min_driver.py -command \'UNSUPPORTED\' -nreceive \'MDI_NAME_LENGTH\' -rtype \'MDI_CHAR\' -mdi \'-role DRIVER -name driver -method TCP -port 8021\'\n"]
    os.makedirs(os.path.dirname(docker_file), exist_ok=True)
    with open(docker_file, 'w') as file:
        file.writelines( docker_lines )

    # Write the run script for the engine
    docker_file = str(base_path) + '/MDI_Mechanic/.temp/docker_mdi_engine.sh'
    docker_lines = [ "#!/bin/bash\n",
                     "\n",
                     "# Exit if any command fails\n",
                     "\n",
                     "cd /repo/user/mdi_tests/.work\n",
                     "export MDI_OPTIONS=\'-role ENGINE -name TESTCODE -method TCP -hostname mdi_mechanic -port 8021\'\n",
                     "./run.sh\n"]
    os.makedirs(os.path.dirname(docker_file), exist_ok=True)
    with open(docker_file, 'w') as file:
        file.writelines( docker_lines )

    # Prepare the working directory
    src_path = os.path.join( base_path, "user", "mdi_tests", "test1" )
    dst_path = os.path.join( base_path, "user", "mdi_tests", ".work" )
    if os.path.isdir( dst_path ):
        shutil.rmtree( dst_path )
    shutil.copytree( src_path, dst_path )

    # Create the docker environment
    docker_env = os.environ
    docker_env['MDIMECH_WORKDIR'] = base_path
    docker_env['MDIMECH_PACKAGEDIR'] = get_package_path()

    # Run "docker-compose up"
    up_proc = subprocess.Popen( ["docker-compose", "up", "--exit-code-from", "mdi_mechanic", "--abort-on-container-exit"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                cwd=docker_path, env=docker_env )
    up_tup = up_proc.communicate()
    up_out = format_return(up_tup[0])
    up_err = format_return(up_tup[1])

    # Run "docker-compose down"
    down_proc = subprocess.Popen( ["docker-compose", "down"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  cwd=docker_path, env=docker_env )
    down_tup = down_proc.communicate()
    down_out = format_return(down_tup[0])
    down_err = format_return(down_tup[1])

    assert up_proc.returncode != 0
    assert down_proc.returncode == 0
