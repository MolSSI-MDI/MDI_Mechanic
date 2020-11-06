import os
import pickle
import subprocess
import yaml

def get_base_path():
    # Get the base directory
    raise Exception("Should not call get_base_path anymore")
    file_path = os.path.dirname(os.path.realpath(__file__))
    base_path = os.path.dirname( os.path.dirname( os.path.dirname( file_path ) ) )
    return base_path

def get_package_path():
    file_path = os.path.dirname(os.path.realpath(__file__))
    package_path = os.path.dirname( os.path.dirname( file_path ) )
    #package_path = os.path.dirname( file_path )
    return package_path

def get_compose_path( method ):
    package_path = get_package_path()
    compose_path = os.path.join( package_path, "mdimechanic", "docker", method )
    return compose_path

def format_return(input_string):
    my_string = input_string.decode('utf-8')

    # remove any \r special characters, which sometimes are added on Windows
    my_string = my_string.replace('\r','')

    return my_string

def insert_list( original_list, insert_list, pos ):
    for ielement in range(len(insert_list)):
        element = insert_list[ielement]
        original_list.insert( pos + ielement + 1, element )

def docker_error( docker_tup, error_message ):
    docker_out = format_return(docker_tup[0])
    docker_err = format_return(docker_tup[1])
    print("-------- BEGIN DOCKER OUTPUT --------")
    print( str(docker_out) )
    print("-------- END DOCKER OUTPUT ----------")
    print("-------- BEGIN DOCKER ERROR ---------")
    print( str(docker_err) )
    print("-------- END DOCKER ERROR -----------")
    raise Exception(error_message)

def get_mdi_standard( base_path ):
    # Path to the file where the standard will be written
    package_path = get_package_path()
    standard_file = os.path.join( base_path, ".mdimechanic", ".temp", "standard.pickle" )
    
    parse_proc = subprocess.Popen( ["docker", "run", "--rm",
                                    "-v", str(base_path) + ":/repo",
                                    "-v", str(package_path) + ":/MDI_Mechanic",
                                    "mdi_mechanic/mdi_mechanic",
                                    "bash", "-c",
                                    "cd /MDI_Mechanic/mdimechanic/utils && python parse_standard.py"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    parse_tup = parse_proc.communicate()
    if parse_proc.returncode != 0:
        docker_error( parse_tup, "Parse process returned an error." )

    with open(standard_file, 'rb') as handle:
        standard = pickle.load(handle)
    return standard

def get_mdimechanic_yaml( base_path ):
    yaml_path = os.path.join( base_path, "mdimechanic.yml" )
    with open(yaml_path, "r") as yaml_file:
        mdimechanic_yaml = yaml.load(yaml_file, Loader=yaml.FullLoader)
    return mdimechanic_yaml
