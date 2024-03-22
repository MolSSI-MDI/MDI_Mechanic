import os
import subprocess
import shutil
from .utils.utils import format_return, insert_list, docker_error, get_mdi_standard, get_compose_path, get_package_path, get_mdimechanic_yaml, writelines_as_bytes, write_as_bytes
from .utils.determine_compose import COMPOSE_COMMAND

def test_driver( driver_name, base_path ):
    mdimechanic_yaml = get_mdimechanic_yaml( base_path )

    # Get the path to the docker-compose file
    docker_path = None
    if 'gpu' in mdimechanic_yaml['docker']:
        docker_path = get_compose_path( "nvidia_tcp" )
    else:
        docker_path = get_compose_path( "tcp" )

    # Write the run script for MDI Mechanic
    docker_file = os.path.join( base_path, ".mdimechanic", ".temp", "docker_mdi_mechanic.sh" )
    docker_lines = [ "#!/bin/bash -l\n",
                     "set -e\n",
                     "\n",
                     "cd /repo\n"]

    driver_script = mdimechanic_yaml['test_drivers'][driver_name]['script']
    for line in driver_script:
        docker_lines.append( line + '\n' )
    os.makedirs(os.path.dirname(docker_file), exist_ok=True)
    writelines_as_bytes( docker_lines, docker_file )

    # Write the run script for the engine
    # NOTE: NEED TO LOOP OVER ALL AVAIALBLE TEST SCRIPTS
    script_lines = mdimechanic_yaml['engine_tests']['script']
    script = "#!/bin/bash\nset -e\ncd /repo\n"
    script += "export MDI_OPTIONS=\'-role ENGINE -name TESTCODE -method TCP -hostname mdi_mechanic -port 8021\'\n"
    for line in script_lines:
        script += line + '\n'

    # Write the script to run the test
    script_path = os.path.join( base_path, ".mdimechanic", ".temp", "docker_mdi_engine.sh" )
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    write_as_bytes( script, script_path )

    # Create the docker environment
    docker_env = os.environ
    docker_env['MDIMECH_WORKDIR'] = base_path
    docker_env['MDIMECH_PACKAGEDIR'] = get_package_path()
    docker_env['MDIMECH_ENGINE_NAME'] = mdimechanic_yaml['docker']['image_name'] + ":dev"

    # Run "docker-compose up"
    up_proc = subprocess.Popen( COMPOSE_COMMAND + ["up", "--exit-code-from", "mdi_mechanic", "--abort-on-container-exit"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                cwd=docker_path, env=docker_env )
    up_tup = up_proc.communicate()
    up_out = format_return(up_tup[0])
    up_err = format_return(up_tup[1])


    # Run "docker-compose down"
    down_proc = subprocess.Popen( COMPOSE_COMMAND + ["down"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  cwd=docker_path, env=docker_env )
    down_tup = down_proc.communicate()
    down_out = format_return(down_tup[0])
    down_err = format_return(down_tup[1])

    if up_proc.returncode != 0:
        docker_error( up_tup, "Driver test returned non-zero exit code." )

    elif down_proc.returncode != 0:
        docker_error( down_tup, "Driver test returned non-zero exit code on docker down." )

    else:
        print("====================================================")
        print("================ Output from Docker ================")
        print("====================================================")
        print(up_out)
        print("====================================================")
        print("============== End Output from Docker ==============")
        print("====================================================")
