import os
import subprocess
from shutil import copyfile
from .utils import tests as mtests
from .utils import node_analysis as na
from .utils import reset_report as rr
from .utils import utils as ut

# Generate the report
def generate_report( base_path ):

    # Path to this file
    #file_path = os.path.dirname(os.path.realpath(__file__))

    # Path to the top-level directory
    #base_path = os.path.dirname( os.path.dirname( file_path ) )

    # Reset the report
    rr.reset_report( base_path )

    # Ensure that there are no orphaned containers / networks running
    try:
        #docker_path = os.path.join( base_path, "MDI_Mechanic", "docker" )
        compose_path = ut.get_compose_path( "tcp" )
        down_proc = subprocess.Popen( ["docker-compose", "down"],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      cwd=compose_path)
        down_tup = down_proc.communicate()
    except:
        raise Exception("Error: Unable to remove orphaned containers.")
    
    # Verify that the engine has been built / installed correctly
    try:
        mtests.test_validate( base_path )
        print("Success: Able to verify that the engine was built")
        src_location = os.path.join(base_path, "report", "badges", "-working-success.svg")
        dst_location = os.path.join(base_path, "report", "dynamic_badges", "step_engine_build.svg")
        copyfile(src_location, dst_location)
    except:
        raise Exception("Error: Unable to verify that the engine was built.")

    # Verify that the engine supports minimalistic MDI functionality
    try:
        mtests.test_min( base_path )
        print("Success: Engine passed minimal MDI functionality test.")
        src_location = os.path.join(base_path, "report", "badges", "-working-success.svg")
        dst_location = os.path.join(base_path, "report", "dynamic_badges", "step_min_engine.svg")
        copyfile(src_location, dst_location)

    except:
        raise Exception("Error: Engine failed minimal MDI functionality test.")

    # Check if the engine correctly errors upon receiving an unsupported command
    try:
        mtests.test_unsupported( base_path )
        print("Success: Engine errors out upon receiving an unsupported command.")
        src_location = os.path.join(base_path, "report", "badges", "-working-success.svg")
        dst_location = os.path.join(base_path, "report", "dynamic_badges", "step_unsupported.svg")
        copyfile(src_location, dst_location)
    except:
        raise Exception("Error: Engine does not error out upon receiving an unsupported command.")

    # Perform the node analysis
    try:
        na.analyze_nodes( base_path )
        print("Success: Detected MDI nodes.")

        # Copy the success badge for this step
        src_location = os.path.join(base_path, "report", "badges", "-working-success.svg")
        dst_location = os.path.join(base_path, "report", "dynamic_badges", "step_mdi_nodes.svg")
        copyfile(src_location, dst_location)

    except:
        raise Exception("Error: Unable to detect MDI nodes.")

    # Prepend the Travis badge to README.md
    readme_path = os.path.join(base_path, ".mdimechanic", ".temp", "README.temp")
    badge_path = os.path.join(base_path, ".mdimechanic", "ci_badge.md")
    badge = None
    readme = None
    try:
        with open(badge_path, 'r') as original: badge = original.read()
    except FileNotFoundError:
        badge = ""
    with open(readme_path, 'r') as original: readme = original.read()
    with open(readme_path, 'w') as modified: modified.write(badge + readme)
    
    # Copy README.temp over README.md
    src_location = os.path.join(base_path, ".mdimechanic", ".temp", "README.temp")
    dst_location = os.path.join(base_path, "README.md")
    copyfile(src_location, dst_location)
