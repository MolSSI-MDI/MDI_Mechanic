import os
import shutil
from .utils import get_package_path, get_mdimechanic_yaml, insert_list

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

    # Get the README.md file locations
    src_location = os.path.join( package_path, "mdimechanic", "report", "README.base" )
    dst_location = os.path.join( base_path, "README.md")

    # Get header information for the README
    code_name = mdimechanic_yaml['code_name']
    readme_data = ["# MDI Mechanic " + str(code_name) + " report\n",
                    "\n",
                    "This repo presents test results for the MDI interface implementation in the " + str(code_name) + " code.\n",
                    "\n"]

    # Get the body information for the README
    with open( src_location, 'r' ) as base_file:
        body = base_file.readlines()

    # Add any prepended information from the mdimechanic.yml file
    prepend_iline = 0
    prepend_data = []
    for iline in range(len(body)):
        line = body[iline]
        sline = line.split()
        if len(sline) > 3:
            if sline[0] == '[yaml]:':
                instruction = sline[3]
                if instruction == "prepend":
                    prepend_iline = iline
    if 'report' in mdimechanic_yaml:
        if 'prepend' in mdimechanic_yaml['report']:
            prepend_data = mdimechanic_yaml['report']['prepend']
            for iline in range(len(prepend_data)):
                if prepend_data[iline] == None:
                    prepend_data[iline] = ""
                prepend_data[iline] = prepend_data[iline] + "\n"
            insert_list( body, prepend_data, prepend_iline)

    # Combine the header data with the body of the README
    readme_data.extend( body )

    # Write the README.md file
    with open( dst_location, 'w' ) as new_file:
        new_file.writelines( readme_data )

if __name__ == "__main__":
    reset_report()
