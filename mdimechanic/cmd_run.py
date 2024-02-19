import os
import subprocess
import shutil
from .utils.utils import format_return, insert_list, docker_error, get_mdi_standard, get_compose_path, get_package_path, get_mdimechanic_yaml, write_as_bytes


def run( script_name, base_path ):
    mdimechanic_yaml = get_mdimechanic_yaml( base_path )

    # Get the path to the docker-compose file
    docker_path = os.path.join( base_path, ".mdimechanic", ".temp" )

    # Get a list of all containers in this calculation
    containers = [ key for key in mdimechanic_yaml['run_scripts'][script_name]['containers'] ]

    # Create the docker-compose.yml file
    docker_compose_text='''version: '3'

services:
'''

    for icontainer in range(len(containers)):
        docker_compose_text += f'  {containers[icontainer]}:'

        container_yaml = mdimechanic_yaml['run_scripts'][script_name]['containers'][containers[icontainer]]

        if not 'image' in container_yaml:
            raise Exception("No image was provided for container \"" + str(containers[icontainer]) + "\".  Please provide the image name in mdimechanic.yml.")

        image_name = container_yaml['image']
        script_file_name = "docker_mdi_" + str(icontainer) + ".sh"

        textargs = {'image_name': container_yaml['image'],
                    'workdir': base_path,
                    'packagedir': get_package_path(),
                    'script_file_name': script_file_name,
                    'icontainer': icontainer,
                    'container_name': containers[icontainer]}
        docker_compose_text += '''
    image: "{image_name}"
    command: bash -l -c "bash -l /mdi_shared/.mdimechanic/.temp/{script_file_name}"
    volumes:
      - '{workdir}:/mdi_shared'
      - '{packagedir}:/MDI_Mechanic'
    networks:
      mdinet:
        aliases:
          - {container_name}
'''.format(**textargs)

        if 'gpu' in mdimechanic_yaml['docker']:
                docker_compose_text += '''deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
'''

    docker_compose_text += '''
networks:
  mdinet:
    driver: "bridge"
'''

    docker_compose_path = os.path.join( base_path, ".mdimechanic", ".temp", "docker-compose.yml" )
    os.makedirs(os.path.dirname(docker_compose_path), exist_ok=True)
    write_as_bytes( docker_compose_text, docker_compose_path )

    # Write the run script for each of the engines
    for icontainer in range(len(containers)):

        container_yaml = mdimechanic_yaml['run_scripts'][script_name]['containers'][containers[icontainer]]

        # Write the run script for the engine
        script_lines = container_yaml['script']
        script = '''#!/bin/bash -l\nset -e
cd /mdi_shared
export MDI_OPTIONS=\'-role ENGINE -name TESTCODE -method TCP -hostname mdi_mechanic -port 8021\'
if [ ! -d "/repo" ]; then
    ln -s /mdi_shared /repo
fi
'''
        #script = "#!/bin/bash\nset -e\ncd /mdi_shared\n"
        #script += "export MDI_OPTIONS=\'-role ENGINE -name TESTCODE -method TCP -hostname mdi_mechanic -port 8021\'\n"
        for line in script_lines:
            script += line + '\n'

        # Write the script to run the test
        script_file_name = "docker_mdi_" + str(icontainer) + ".sh"
        script_path = os.path.join( base_path, ".mdimechanic", ".temp", script_file_name )
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        write_as_bytes( script, script_path )

    # Launch with docker-compose
    docker_env = os.environ
    up_proc = subprocess.Popen( ["docker-compose", "up"],
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
