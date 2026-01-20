#!/usr/bin/env python

# This python script launches various types of scan in which the sfincs executable is run
# multiple times.  This file contains definitions that are shared among the various
# types of scan.

import os
import sys
import inspect
import math
import subprocess
import importlib
from sys import argv

try:
    from . import sfincsScan_common
except ImportError:
    import sfincsScan_common


def main():
    # print ("This is "+ inspect.getfile(inspect.currentframe()))

    filename = "input.namelist"
    jobFilename = "job.sfincsScan"
    # commentCode = "!ss"

    try:
        sfincsSystem = os.environ["SFINCS_SYSTEM"]
    except KeyError:
        print("Error! Unable to read the SFINCS_SYSTEM environment variable. Make sure you have set it.")
        sys.exit(1)
    print("I detect SFINCS_SYSTEM = " + sfincsSystem)

    # If there are any command-line arguments, sfincsScan interprets this to mean it should not ask for permission before submitting jobs.
    if len(argv) > 1:
        waitBeforeSubmitting = False
    else:
        waitBeforeSubmitting = True

    if not os.path.isfile(filename):
        print("Error! The file " + filename + " must be present in the directory from which you call sfincsScan.")
        sys.exit(1)

    # For each system,
    if sfincsSystem in ["raven", "viper", "eddy", "stellar", "perlmutter", "marconi"]:
        submitCommand = "sbatch " + jobFilename

        def nameJobFile(original, name):
            # Modify the job.sfincsScan file to change the name that appears in the queue.
            # Insert the new line after the original first line, since the first line is a shebang.
            original.insert(1, "#SBATCH -J " + name + "\n")
            return original

    elif sfincsSystem == "laptop" or sfincsSystem == "macports" or sfincsSystem == "ubuntu16.04" or sfincsSystem == "opensuse":
        submitCommand = "bash " + jobFilename

        def nameJobFile(original, name):
            # No changes needed to the job.sfincsScan file.
            return original

    else:
        print("Error! SFINCS_SYSTEM=" + sfincsSystem + " is not yet recognized by sfincsScan")
        print("You will need to edit sfincsScan to specify a few things for this system.")
        sys.exit(1)

    # Check for job file existence
    if not os.path.isfile(jobFilename):
        print(
            "Error! A "
            + jobFilename
            + " file must be present in the directory from which you call sfincsScan (even for systems with no queue)."
        )
        print("Examples are available in /fortran/version3/utils/job.sfincsScan.xxx")
        sys.exit(1)

    # Load the input file:
    with open(filename, "r") as f:
        inputFile = f.readlines()

    # Read scanType
    scanType = sfincsScan_common.readScanVariable(inputFile, "scanType", "int", inputFilename=filename)

    # Prepare context for the scan module
    context = {
        "inputFile": inputFile,
        "inputFilename": filename,
        "jobFilename": jobFilename,
        "sfincsSystem": sfincsSystem,
        "waitBeforeSubmitting": waitBeforeSubmitting,
        "submitCommand": submitCommand,
        "nameJobFile": nameJobFile,
        "sskipExistingDirectories": False,
    }

    scan_module_name = "sfincsScan_" + str(scanType)
    scriptName = os.path.join(os.path.dirname(os.path.abspath(__file__)), scan_module_name + ".py")

    if not os.path.isfile(scriptName):
        print(
            "Error! The file "
            + scriptName
            + " does not exist, meaning that plots for scanType = "
            + str(scanType)
            + " are not yet supported."
        )
        sys.exit(1)

    try:
        # Import the module dynamically
        try:
            # Try package relative import first
            mod = importlib.import_module("." + scan_module_name, package=__package__ if __package__ else "utils")
        except (ImportError, TypeError):
            # Fallback to absolute import
            mod = importlib.import_module(scan_module_name)

        if hasattr(mod, "run"):
            mod.run(context)
        else:
            print(f"Error: Module {scan_module_name} does not have a 'run' entry point.")
            sys.exit(1)

    except ImportError as e:
        print(f"Unable to run {scan_module_name} even though the file exists. Error: {e}")
        raise

    print("Good bye!")


if __name__ == "__main__":
    main()
