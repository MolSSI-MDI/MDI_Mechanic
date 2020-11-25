import os
import shutil
from .utils import get_package_path, get_mdimechanic_yaml

def reset_report( base_path ):
    # Path to this file
    #file_path = os.path.dirname(os.path.realpath(__file__))

    # Path to the top-level directory
    #base_path = os.path.dirname( os.path.dirname( os.path.dirname( file_path ) ) )

    # Get the MDI YAML
    mdimechanic_yaml = get_mdimechanic_yaml( base_path )

    package_path = get_package_path()

    # Remove the old report
    report_path = os.path.join(base_path, "report")
    if os.path.isdir( report_path ):
        shutil.rmtree( report_path )

    # Copy the base report
    src_location = os.path.join( package_path, "mdimechanic", "report", "base_report" )
    dst_location = os.path.join( base_path, "report")
    shutil.copytree( src_location, dst_location )

    # Reset the README.md file
    src_location = os.path.join( package_path, "mdimechanic", "report", "README.base" )
    dst_location = os.path.join( base_path, "README.md")
    with open( src_location, 'r' ) as base_file: base = base_file.read()
    code_name = mdimechanic_yaml['code_name']
    prepend_data = "# MDI Mechanic " + str(code_name) + " report\n\n" + "This repo presents test results for the MDI interface implementation in the " + str(code_name) + " code.\n\n"
    with open( dst_location, 'w' ) as new_file: new_file.write( prepend_data + base )
    #shutil.copyfile( src_location, dst_location )

if __name__ == "__main__":
    reset_report()
