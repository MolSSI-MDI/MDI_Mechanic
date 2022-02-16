import os
import subprocess
import shutil
from .utils.utils import format_return, insert_list, docker_error, get_mdi_standard, get_compose_path, get_package_path, get_mdimechanic_yaml


def run( script_name, base_path ):
    mdimechanic_yaml = get_mdimechanic_yaml( base_path )

    # Get the path to the docker-compose file
    docker_path = get_compose_path( "run" )

    # Write the run script for the engine
    #script_lines = mdimechanic_yaml['engine_tests']['script']
    script_lines = mdimechanic_yaml['run_scripts'][script_name]['containers']['container1']['script']
    script = "#!/bin/bash\nset -e\ncd /repo\n"
    script += "export MDI_OPTIONS=\'-role ENGINE -name TESTCODE -method TCP -hostname mdi_mechanic -port 8021\'\n"
    for line in script_lines:
        script += line + '\n'

    # Write the script to run the test
    script_path = os.path.join( base_path, ".mdimechanic", ".temp", "docker_mdi_engine.sh" )
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    with open(script_path, "wb") as script_file:
        script_file.write( bytes(script, "UTF-8") )

    # Create the docker environment
    docker_env = os.environ
    docker_env['MDIMECH_WORKDIR'] = base_path
    docker_env['MDIMECH_PACKAGEDIR'] = get_package_path()
    if 'image' in mdimechanic_yaml['run_scripts'][script_name]['containers']['container1']:
        docker_env['MDIMECH_ENGINE_NAME'] = mdimechanic_yaml['run_scripts'][script_name]['containers']['container1']['image']
    else:
        raise Exception("No image was provided for container \"container1\".  Please provide the image name in mdimechanic.yml.")

    # Run "docker-compose up"
    up_proc = subprocess.Popen( ["docker-compose", "up", "--exit-code-from", "engine", "--abort-on-container-exit"],
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
