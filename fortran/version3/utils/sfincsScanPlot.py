#!/usr/bin/env python

# This python script plots various types of scan in which the sfincs executable is run
# multiple times.  All this script does is check input.namelist to read scanType, and then
# call the appropriate script sfincsScanPlot_X.  You are also welcome to run
# sfincsScanPlot_X directly.

import os
import inspect
import sys
import subprocess
import time
import importlib

try:
    from . import sfincsScan_common
except ImportError:
    import sfincsScan_common

def main():
    # print ("This is "+ inspect.getfile(inspect.currentframe()))

    # If called with any command-line arguments other than 'noplot' or 'pdf', then redirect to sfincsScanPlot_combine.
    if len(sys.argv)>1 and (sys.argv[1] != "noplot") and (sys.argv[1].lower() != "pdf"):
        # We need to call sfincsScanPlot_combine.py
        # It is in the same directory.
        scriptName =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfincsScanPlot_combine.py")
        command = sys.argv
        command[0] = scriptName
        start_time = time.time()
        
        # Use sys.executable to ensure we run with the same python interpreter
        full_command = [sys.executable] + command
        
        subprocess.call(full_command)
        print ("Time for subprocess call to sfincsScanPlot_combine: ", time.time() - start_time)
        sys.exit(0)

    inputFilename = "input.namelist"

    if not os.path.isfile(inputFilename):
        print ("Error! The file "+inputFilename+" must be present in the directory from which you call sfincsScanPlot.")
        sys.exit(1)

    start_time = time.time()
    
    # Load the input file:
    with open(inputFilename, 'r') as f:
        inputFile = f.readlines()

    scanType = sfincsScan_common.readScanVariable(inputFile, "scanType", "int", inputFilename=inputFilename)

    context = {
        'inputFile': inputFile,
        'inputFilename': inputFilename,
        'jobFilename': "job.sfincsScan",
        'sfincsSystem': "unknown",
        'waitBeforeSubmitting': True,
        'submitCommand': "bash",
        'nameJobFile': lambda x,y: x
    }

    scan_module_name = "sfincsScanPlot_" + str(scanType)
    scriptName = os.path.join(os.path.dirname(os.path.abspath(__file__)), scan_module_name + ".py")
    
    if not os.path.isfile(scriptName):
        print ("Error! The file "+scriptName+" does not exist.")
        sys.exit(1)

    try:
        try:
             mod = importlib.import_module("." + scan_module_name, package=__package__ if __package__ else "utils")
        except (ImportError, TypeError):
             mod = importlib.import_module(scan_module_name)
        
        if hasattr(mod, 'run'):
            mod.run(context)
        else:
             print(f"Error: {scan_module_name} does not have a run function.")
             sys.exit(1)

    except ImportError as e:
        print (f"Unable to run {scan_module_name}. Error: {e}")
        raise

if __name__ == "__main__":
    main()
