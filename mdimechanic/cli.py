"""
Provides a CLI for MDI_Mechanic
"""

import argparse
import sys
from . import mdi_mechanic as mech

def parse_args():
    parser = argparse.ArgumentParser(description="A CLI for the MDI_Mechanic.")

    subparsers = parser.add_subparsers(dest="command")

    build = subparsers.add_parser("build", help="Build containers for MDI_Mechanic and the engine.")
    #build.add_argument("location", type=str, help="The location where the engine is located.")

    report = subparsers.add_parser("report", help="Create a report for the engine.")

    args = vars(parser.parse_args())
    if args["command"] is None:
        parser.print_help(sys.stderr)
        exit(1)

    return args

def main(args=None):
    if args is None:
        args = parse_args()

    command = args.pop("command")
    if command == "build":
        mech.command_build()
    elif command == "report":
        mech.command_report()
