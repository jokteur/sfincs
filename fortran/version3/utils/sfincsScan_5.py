import os
import sys
import inspect
import shutil
import subprocess
from builtins import input

try:
    from . import sfincsScan_common
except ImportError:
    import sfincsScan_common

def run(context):
    # Unpack context
    inputFile = context['inputFile']
    inputFilename = context['inputFilename']
    jobFilename = context['jobFilename']
    sfincsSystem = context['sfincsSystem']
    waitBeforeSubmitting = context['waitBeforeSubmitting']
    submitCommand = context['submitCommand']
    nameJobFile = context['nameJobFile']

    # Helper functions to bridge new context with old calls
    def readVariable(varName, type, required=True):
         return sfincsScan_common.readVariable(inputFile, varName, type, required, inputFilename)

    def readScanVariable(varName, type, required=True, stringValueCaseSensitive=False):
         return sfincsScan_common.readScanVariable(inputFile, varName, type, required, stringValueCaseSensitive, inputFilename)

    logspace = sfincsScan_common.logspace
    logspace_odd = sfincsScan_common.logspace_odd
    logspace_int = sfincsScan_common.logspace_int
    linspace = sfincsScan_common.linspace
    uniq = sfincsScan_common.uniq
    namelistLineContains = sfincsScan_common.namelistLineContains
    namelistLineContainsSS = sfincsScan_common.namelistLineContainsSS

    
    # This script will not work if called directly.
    # From the command line, you should call sfincsScan instead.
    
    profilesFilename = 'profiles'
    
    import os, inspect
    from builtins import input
    
    #print ("This is "+ inspect.getfile(inspect.currentframe()))
    this_filename = "sfincsScan_5"
    print ("This is "+ this_filename)
    print ("Beginning a scan of Er inside a scan over radius.")
    
    # Determine radii to use, and n & T at those radii:
    skipExistingDirectories = False
    #execfile(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+"/radialScans")
    try:
        from . import radialScans
    except ImportError:
        import radialScans
    radialScans.run(context)
    
    # Unpack variables from radialScans
    radii = context['radii']
    directories = context['directories']
    radiusName = context['radiusName']
    radiusNameForGradients = context['radiusNameForGradients']
    Nspecies = context['Nspecies']
    nHats = context['nHats']
    dnHatdradii = context['dnHatdradii']
    THats = context['THats']
    dTHatdradii = context['dTHatdradii']
    NErs = context['NErs']
    generalErName = context['generalErName']
    generalEr_max = context['generalEr_max']
    generalEr_min = context['generalEr_min']

    # Also make sure filename is set, as it is used below
    filename = inputFilename

    if waitBeforeSubmitting:
        while True:
            #proceed=raw_input("Should I go ahead and launch Er scans at these "+str(len(radii))+" radii? [y/n] ")
            proceed=input("Should I go ahead and launch Er scans at these "+str(len(radii))+" radii? [y/n] ")
            if proceed=="y" or proceed=="n":
                break
            print ("You must enter either y or n.")
    
        if proceed=="n":
            exit(0)
    
    print ("launching jobs...")
    
    # Read in the job.sfincsScan file:
    with open(jobFilename, 'r') as f:
        jobFile = f.readlines()
    
    for runNum in range(len(radii)):
        directory = directories[runNum]
        print ("Beginning to handle radius "+str(runNum+1)+" of "+str(len(radii))+": "+directory)
    
        # To be extra safe, check again to see if the directory exists.
        if os.path.exists(directory):
            print ("Directory "+directory+" already exists.")
        else:
            print ("Creating directory "+directory)
            os.makedirs(directory)
        os.chdir(directory)
    
        # Copy the job.sfincsScan file:
        thisJobFile = list(jobFile)
        ## This next function is defined separately for each system in sfincsScan
        #nameJobFile(thisJobFile,directory)
        f = open(jobFilename,"w")
        f.writelines(thisJobFile)
        f.close()
    
        # Now copy the input.namelist file:
    
        f = open(filename,"w")
        for line in inputFile:
            # Set sfincsScan directives:
            if namelistLineContainsSS(line,"scanType"):
    ##            line = "!ss scanType = 2  ! set by sfincsScan_5.\n"
                continue
            if namelistLineContainsSS(line,"NErs"):
    ##            line = "!ss NErs = "+str(int(NErs[runNum]))+"  ! set by sfincsScan_5.\n"
                continue
            if namelistLineContainsSS(line,generalErName+"Max"):
    ##            line = "!ss dPhiHatd"+radiusNameForGradients+"Max = "+str(dPhiHatdradius_max[runNum])+"  ! set by sfincsScan_5.\n"
                continue
            if namelistLineContainsSS(line,generalErName+"Min"):
    ##            line = "!ss dPhiHatd"+radiusNameForGradients+"Min = "+str(dPhiHatdradius_min[runNum])+"  ! set by sfincsScan_5.\n"
                continue
            # Now set fortran variables:
            if namelistLineContains(line,radiusName+"_wish"):
    ##            line = "  "+radiusName+"_wish = "+str(radii[runNum])+" ! Set by sfincsScan_5.\n"
                continue
            if namelistLineContains(line,"nHats"):
    ##            line = "  nHats ="
    ##            for ispecies in range(Nspecies):
    ##                line += " "+str(nHats[ispecies][runNum])
    ##            line += " ! Set by sfincsScan_5.\n"
                continue
            if namelistLineContains(line,"dnHatd"+radiusNameForGradients+"s"):
    ##            line = "  dnHatd"+radiusNameForGradients+"s ="
    ##            for ispecies in range(Nspecies):
    ##                line += " "+str(dnHatdradii[ispecies][runNum])
    ##            line += " ! Set by sfincsScan_5.\n"
                continue
            if namelistLineContains(line,"THats"):
    ##            line = "  THats ="
    ##            for ispecies in range(Nspecies):
    ##                line += " "+str(THats[ispecies][runNum])
    ##            line += " ! Set by sfincsScan_5.\n"
                continue
            if namelistLineContains(line,"dTHatd"+radiusNameForGradients+"s"):
    ##            line = "  dTHatd"+radiusNameForGradients+"s ="
    ##            for ispecies in range(Nspecies):
    ##                line += " "+str(dTHatdradii[ispecies][runNum])
    ##            line += " ! Set by sfincsScan_5.\n"
                continue
    
            if line.strip().find("&geometryParameters") == 0 :
                line += "  "+radiusName+"_wish = "+str(radii[runNum])+" ! Set by sfincsScan_5.\n"
    
            if line.strip().find("&speciesParameters") == 0 :
                line += "  nHats =" 
                for ispecies in range(Nspecies):
                    line += " "+str(nHats[ispecies][runNum])
                line += " ! Set by sfincsScan_5.\n"    
    
                line += "  dnHatd"+radiusNameForGradients+"s ="
                for ispecies in range(Nspecies):
                    line += " "+str(dnHatdradii[ispecies][runNum])
                line += " ! Set by sfincsScan_5.\n"
    
                line += "  THats ="
                for ispecies in range(Nspecies):
                    line += " "+str(THats[ispecies][runNum])
                line += " ! Set by sfincsScan_5.\n"
    
                line += "  dTHatd"+radiusNameForGradients+"s ="
                for ispecies in range(Nspecies):
                    line += " "+str(dTHatdradii[ispecies][runNum])
                line += " ! Set by sfincsScan_5.\n"    
    
            #######################    
            f.write(line)
    
        line = "!ss scanType = 2  ! set by sfincsScan_5.\n"
        line += "!ss NErs = "+str(int(NErs[runNum]))+"  ! set by sfincsScan_5.\n"
        line += "!ss "+generalErName+"Max = "+str(generalEr_max[runNum])+"  ! set by sfincsScan_5.\n"
        line += "!ss "+generalErName+"Min = "+str(generalEr_min[runNum])+"  ! set by sfincsScan_5.\n"
        f.write(line)
    
        f.close()
    
        #################################################
    
        # Submit the Er scan:
    ##    submitCommand = "sfincsScan -f" 
        #submitCommand = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+"/sfincsScan -f"
        submitCommand = "python " + os.path.dirname(os.path.abspath(__file__))+"/sfincsScan.py -f"
        #############################
        try:
            # We need to include .split(" ") to separate the command-line arguments into an array of strings.   
            # I'm not sure why python requires this. 
            submissionResult = subprocess.call(submitCommand.split(" "))
            #submissionResult=0
        except:
            print ("ERROR! Unable to submit run "+directory+" for some reason.")
            raise
        else:
            if submissionResult==0:
                print ("No errors submitting job "+directory)
            else:
                print ("Nonzero exit code returned when trying to submit job "+directory)
    
        os.chdir("..")
    
    
