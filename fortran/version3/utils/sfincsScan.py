#!/usr/bin/env python

# This python script launches various types of scan in which the sfincs executable is run
# multiple times.  This file contains definitions that are shared among the various
# types of scan.

import os, inspect, math, subprocess
from sys import argv
import common

print ("This is "+ inspect.getfile(inspect.currentframe()))

common.filename = "input.namelist"
common.jobFilename = "job.sfincsScan"
common.commentCode = "!ss"

try:
    sfincsSystem = os.environ["SFINCS_SYSTEM"]
except:
    print ("Error! Unable to read the SFINCS_SYSTEM environment variable. Make sure you have set it.")
    raise
print ("I detect SFINCS_SYSTEM = "+sfincsSystem)

# If there are any command-line arguments, sfincsScan interprets this to mean it should not ask for permission before submitting jobs.
if len(argv)>1:
    waitBeforeSubmitting = False
else:
    waitBeforeSubmitting = True

if not os.path.isfile(common.filename):
    print ("Error! The file "+common.filename+" must be present in the directory from which you call sfincsScan.")
    exit(1)

# For each system, 
if sfincsSystem in ["raven", "viper", "eddy", "stellar", "perlmutter", "marconi"]:
    submitCommand = "sbatch "+common.jobFilename
    def nameJobFile(original,name):
        # Modify the job.sfincsScan file to change the name that appears in the queue.
        # Insert the new line after the original first line, since the first line is a shebang.
        original.insert(1,"#SBATCH -J "+name+"\n")
        return original

elif sfincsSystem=="laptop" or sfincsSystem=="macports" or sfincsSystem=='ubuntu16.04' or sfincsSystem=='opensuse':
    submitCommand = "bash "+common.jobFilename
    def nameJobFile(original,name):
        # No changes needed to the job.sfincsScan file.
        return original

else:
    print ("Error! SFINCS_SYSTEM="+sfincsSystem+" is not yet recognized by sfincsScan")
    print ("You will need to edit sfincsScan to specify a few things for this system.")
    exit(1)

#if sfincsSystem=='edison':
#    # Any checks that should be done for SFINCS_SYSTEM=edison can go here.
#    jobfileRequired = True
#elif sfincsSystem=='laptop':
#    # Any checks that should be done for SFINCS_SYSTEM=laptop can go here.
#    jobfileRequired = False
#else:
#    print "Error! This system is not known by sfincsScan"
#    print "You will need to edit sfincsScan"

# Any checks that should be done for other systems can go here.

#if jobfileRequired:
if not os.path.isfile(common.jobFilename):
    print ("Error! A "+common.jobFilename+" file must be present in the directory from which you call sfincsScan (even for systems with no queue).")
    print ("Examples are available in /fortran/version3/utils/job.sfincsScan.xxx")
    exit(1)

# Load the input file:
with open(common.filename, 'r') as f:
    inputFile = f.readlines()

# Next come some functions used in convergence scans which might be useful for other types of scans:

def uniq(seq): 
   checked = []
   for e in seq:
       if e not in checked:
           checked.append(e)
   return checked

def logspace(min,max,nn):
    if nn < 1:
        return []
    elif nn==1:
        return [min]

    if min <= 0:
        print ("Error in logspace! min must be positive.")
        exit(1)
    if max <= 0:
        print ("Error in logspace! max must be positive.")
        exit(1)
    return [math.exp(x/(nn-1.0)*(math.log(max)-math.log(min))+math.log(min)) for x in range(nn)]

def linspace(min,max,nn):
    if nn < 1:
        return []
    elif nn==1:
        return [min]
    return [x/(nn-1.0)*(max-min)+min for x in range(nn)]

def logspace_int(min,max,nn):
    return uniq(map(int,map(round,logspace(min,max,nn))))

def logspace_odd(min,max,nn):
    temp = map(int,logspace(min,max,nn))
    temp2 = []
    for x in temp:
        if (x % 2 == 0):
            temp2.append(x+1)
        else:
            temp2.append(x)
    return uniq(temp2)



# Load some other required subroutines:
#execfile(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+"/sfincsScan_common")
from sfincsScan_common import *

scanType = readScanVariable("scanType","int", inputFile)

if scanType == 1:
    import sfincsScan_1
elif scanType == 2:
    import sfincsScan_2
elif scanType == 3:
    import sfincsScan_3
elif scanType == 4:
    from sfincsScan_4 import make_scan
    make_scan(waitBeforeSubmitting, inputFile, nameJobFile, submitCommand)
elif scanType == 5:
    from sfincsScan_5 import make_scan
    make_scan(waitBeforeSubmitting, inputFile)
    
elif scanType == 21:
    import sfincsScan_21
elif scanType == 22:
    import sfincsScan_22

print ("Good bye!")
