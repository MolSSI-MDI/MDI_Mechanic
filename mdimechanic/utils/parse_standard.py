import os
import pickle
import sys
import yaml

def parse_mdi_standard( ):
    #package_path = get_package_path()
    #file_path = os.path.dirname(os.path.realpath(__file__))
    #package_path = os.path.dirname( os.path.dirname( file_path ) )
    #base_path = os.path.dirname( os.path.dirname( os.path.dirname( file_path ) ) )
    #standard_yaml_path = os.path.join( base_path,"MDI_Mechanic","mdi_standard.yaml")
    #standard_yaml_path = os.path.join( package_path, "mdimechanic", "mdi_standard.yaml")
    #standard_file = os.path.join( base_path, "MDI_Mechanic", ".temp", "standard.pickle" )

    # This is only executed within Docker, so the paths should NOT use os.path.join
    standard_yaml_path = "/MDI_Mechanic/mdimechanic/mdi_standard.yaml"
    standard_file = "/repo/.mdimechanic/.temp/standard.pickle"

    # Read the yaml file
    with open(standard_yaml_path, "r") as yaml_file:
        standard = yaml.load(yaml_file, Loader=yaml.FullLoader)

    # Dump the data using pickle
    #print("FILE: " + str(base_path))
    os.makedirs(os.path.dirname(standard_file), exist_ok=True)
    with open(standard_file, 'wb') as handle:
        pickle.dump(standard, handle, protocol=min(pickle.HIGHEST_PROTOCOL, 4))

if __name__ == "__main__":
    parse_mdi_standard( )
