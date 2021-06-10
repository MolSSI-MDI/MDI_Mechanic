import os
import subprocess
import shutil
from .utils import format_return, insert_list, docker_error, get_mdi_standard, get_compose_path, get_package_path, get_mdimechanic_yaml



def test_validate( base_path ):
    # Get the base directory
    package_path = get_package_path()

    # Get the MDI YAML
    mdimechanic_yaml = get_mdimechanic_yaml( base_path )

    # Read the yaml script for validating the engine build
    mdimechanic_yaml = get_mdimechanic_yaml( base_path )
    validate_engine_lines = mdimechanic_yaml['docker']['validate_engine']
    validate_engine_script = "#!/bin/bash\nset -e\ncd /repo\n"
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
                                   mdimechanic_yaml['docker']['image_name'],
                                   "bash", "-c",
                                   "cd /repo && bash .mdimechanic/.temp/validate_engine.sh"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    test_tup = test_proc.communicate()
    test_out = format_return(test_tup[0])
    test_err = format_return(test_tup[1])

    if test_proc.returncode != 0:
        docker_error( test_tup, "Build validation script returned non-zero value." )


def test_min( base_path ):
    # Get the path to the docker-compose file
    docker_path = get_compose_path( "tcp" )

    # Write the run script for MDI Mechanic
    docker_file = os.path.join( base_path, ".mdimechanic", ".temp", "docker_mdi_mechanic.sh" )
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
    # NOTE: NEED TO LOOP OVER ALL AVAIALBLE TEST SCRIPTS
    mdimechanic_yaml = get_mdimechanic_yaml( base_path )
    script_lines = mdimechanic_yaml['engine_tests']['script']
    script = "#!/bin/bash\nset -e\ncd /repo\n"
    script += "export MDI_OPTIONS=\'-role ENGINE -name TESTCODE -method TCP -hostname mdi_mechanic -port 8021\'\n"
    for line in script_lines:
        script += line + '\n'

    # Write the script to run the test
    script_path = os.path.join( base_path, ".mdimechanic", ".temp", "docker_mdi_engine.sh" )
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    with open(script_path, "w") as script_file:
        script_file.write( script )

    # Prepare the working directory
    #src_path = os.path.join( base_path, "user", "mdi_tests", "test1" )
    #dst_path = os.path.join( base_path, "user", "mdi_tests", ".work" )
    #if os.path.isdir( dst_path ):
    #    shutil.rmtree( dst_path )
    #shutil.copytree( src_path, dst_path )

    # Create the docker environment
    docker_env = os.environ
    docker_env['MDIMECH_WORKDIR'] = base_path
    docker_env['MDIMECH_PACKAGEDIR'] = get_package_path()
    docker_env['MDIMECH_ENGINE_NAME'] = mdimechanic_yaml['docker']['image_name']

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

    if up_proc.returncode != 0:
        docker_error( up_tup, "Minimal MDI functionality test returned non-zero exit code." )

    if down_proc.returncode != 0:
        docker_error( down_tup, "Minimal MDI functionality test returned non-zero exit code on docker down." )

def test_unsupported( base_path ):
    # Get the path to the docker-compose file
    docker_path = get_compose_path( "tcp" )

    # Write the run script for MDI Mechanic
    docker_file = os.path.join( base_path, ".mdimechanic", ".temp", "docker_mdi_mechanic.sh" )
    docker_lines = [ "#!/bin/bash\n",
                     "\n",
                     "# Exit if any command fails\n",
                     "\n",
                     "cd /MDI_Mechanic/mdimechanic/drivers\n",
                     "python min_driver.py -command \'<UNSUPPORTED\' -nreceive \'MDI_NAME_LENGTH\' -rtype \'MDI_CHAR\' -mdi \'-role DRIVER -name driver -method TCP -port 8021\'\n"]
    os.makedirs(os.path.dirname(docker_file), exist_ok=True)
    with open(docker_file, 'w') as file:
        file.writelines( docker_lines )

    # Write the run script for the engine
    #docker_file = str(base_path) + '/MDI_Mechanic/.temp/docker_mdi_engine.sh'
    #docker_lines = [ "#!/bin/bash\n",
    #                 "\n",
    #                 "# Exit if any command fails\n",
    #                 "\n",
    #                 "cd /repo/user/mdi_tests/.work\n",
    #                 "export MDI_OPTIONS=\'-role ENGINE -name TESTCODE -method TCP -hostname mdi_mechanic -port 8021\'\n",
    #                 "./run.sh\n"]
    #os.makedirs(os.path.dirname(docker_file), exist_ok=True)
    #with open(docker_file, 'w') as file:
    #    file.writelines( docker_lines )
    # NOTE: NEED TO LOOP OVER ALL AVAIALBLE TEST SCRIPTS
    mdimechanic_yaml = get_mdimechanic_yaml( base_path )
    script_lines = mdimechanic_yaml['engine_tests']['script']
    script = "#!/bin/bash\nset -e\ncd /repo\n"
    script += "export MDI_OPTIONS=\'-role ENGINE -name TESTCODE -method TCP -hostname mdi_mechanic -port 8021\'\n"
    for line in script_lines:
        script += line + '\n'

    # Write the script to run the test
    script_path = os.path.join( base_path, ".mdimechanic", ".temp", "docker_mdi_engine.sh" )
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    with open(script_path, "w") as script_file:
        script_file.write( script )
        
    # Prepare the working directory
    #src_path = os.path.join( base_path, "user", "mdi_tests", "test1" )
    #dst_path = os.path.join( base_path, "user", "mdi_tests", ".work" )
    #if os.path.isdir( dst_path ):
    #    shutil.rmtree( dst_path )
    #shutil.copytree( src_path, dst_path )

    # Create the docker environment
    docker_env = os.environ
    docker_env['MDIMECH_WORKDIR'] = base_path
    docker_env['MDIMECH_PACKAGEDIR'] = get_package_path()
    docker_env['MDIMECH_ENGINE_NAME'] = mdimechanic_yaml['docker']['image_name']

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

    #assert up_proc.returncode != 0
    #assert down_proc.returncode == 0

    if up_proc.returncode == 0:
        docker_error( up_tup, "Test for correct error functionality returned zero exit code." )

    if down_proc.returncode != 0:
        docker_error( down_tup, "Test for correct error functionality returned non-zero exit code on docker down." )

def test_driver( driver_name, base_path ):
    mdimechanic_yaml = get_mdimechanic_yaml( base_path )

    # Get the path to the docker-compose file
    docker_path = get_compose_path( "tcp" )

    # Write the run script for MDI Mechanic
    docker_file = os.path.join( base_path, ".mdimechanic", ".temp", "docker_mdi_mechanic.sh" )
    docker_lines = [ "#!/bin/bash\n",
                     "set -e\n",
                     "\n",
                     "cd /repo\n"]

    driver_script = mdimechanic_yaml['test_drivers'][driver_name]['script']
    for line in driver_script:
        docker_lines.append( line + '\n' )
    os.makedirs(os.path.dirname(docker_file), exist_ok=True)
    with open(docker_file, 'w') as file:
        file.writelines( docker_lines )

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
    with open(script_path, "w") as script_file:
        script_file.write( script )

    # Create the docker environment
    docker_env = os.environ
    docker_env['MDIMECH_WORKDIR'] = base_path
    docker_env['MDIMECH_PACKAGEDIR'] = get_package_path()
    docker_env['MDIMECH_ENGINE_NAME'] = mdimechanic_yaml['docker']['image_name']

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
