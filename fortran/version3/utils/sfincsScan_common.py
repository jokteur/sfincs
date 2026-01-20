#!/usr/bin/env python

import os
import math
import string
import time

# This python file contains several subroutines that are used both in launching and processing parameter scans in sfincs.

INPUT_FILENAME = "input.namelist"
OUTPUT_FILENAME = "sfincsOutput.h5"
DEFAULT_VARIABLES_FILENAME = "globalVariables.F90" 
COMMENT_CODE = "!ss"

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
    return uniq(list(map(int,map(round,logspace(min,max,nn)))))

def logspace_odd(min,max,nn):
    temp = list(map(int,logspace(min,max,nn)))
    temp2 = []
    for x in temp:
        if (x % 2 == 0):
            temp2.append(x+1)
        else:
            temp2.append(x)
    return uniq(temp2)

def namelistLineContains(line,varName):
    line2 = line.strip().lower()
    varName = varName.lower()
    # We need enough characters for the varName, =, and value: 
    if len(line2)<len(varName)+2:
        return False

    if line2[0]=="!":
        return False

    nextChar = line2[len(varName)]
    if line2[:len(varName)]==varName and (nextChar==" " or nextChar=="="):
        return True
    else:
        return False

def namelistLineContainsSS(line,varName):
    # Same as namelistLineContains, but looking for !ss directives.
    line2 = line.strip().lower()
    varName = varName.lower()
    if len(line2)<len(COMMENT_CODE):
        return False

    if line2[:len(COMMENT_CODE)] != COMMENT_CODE:
        return False

    # If we got this far, the line must begin with !ss, so strip this part out.
    line2 = line2[len(COMMENT_CODE):].strip()

    # We need enough characters for the varName, =, and value: 
    if len(line2)<len(varName)+2:
        return False

    if line2[0]=="!":
        return False

    nextChar = line2[len(varName)]
    if line2[:len(varName)]==varName and (nextChar==" " or nextChar=="="):
        return True
    else:
        return False

def readScanVariable(inputFile, varName, intOrFloatOrString, required=True, stringValueCaseSensitive=False, inputFilename=INPUT_FILENAME):
    # This subroutine reads the special scan commands in the input.namelist that are hidden from fortran:
    # inputFilename is passed mainly for error messages.
    # inputFile is a list of strings (lines)

    if (intOrFloatOrString != "int") and (intOrFloatOrString != "float") and (intOrFloatOrString != "string"):
        print ("intOrFloatOrString must be int, float, or string.")
        exit(1)

    originalVarName = varName
    varName = varName.lower()
    returnValue = None
    numValidLines = 0
    for line in inputFile:
        if not stringValueCaseSensitive:
            line2 = line.strip().lower()
        else:
            line2 = line.strip()

        # We need enough characters for the comment code, varName, =, and value:        
        if len(line2)<len(COMMENT_CODE)+3:
            continue

        if not line2[:len(COMMENT_CODE)]==COMMENT_CODE:
            continue

        line3 = line2[len(COMMENT_CODE):].strip()

        if len(line3) < len(varName)+2:
            continue

        if not line3[:len(varName)].lower()==varName:
            continue

        line4 = line3[len(varName):].strip()

        if not line4[0] =="=":
            continue

        line5 = line4[1:].strip();

        if intOrFloatOrString != "string":
            # python does not recognize fortran's 1d+0 scientific notation
            line5 = line5.replace('d','e').replace('D','e')
        
        # Remove any comments:
        if "!" in line5:
            try:
                line5 = line5[:line5.find("!")]
            except:
                pass
        line5 = line5.strip();

        if intOrFloatOrString=="int":
            try:
                returnValue = int(line5)
                numValidLines += 1
            except:
                print ("Warning! I found a definition for the variable "+originalVarName+" in "+inputFilename+" but I was unable to parse the line to get an integer.")
                print ("Here is the line in question:")
                print (line)
        elif intOrFloatOrString=="float":
            try:
                returnValue = float(line5)
                numValidLines += 1
            except:
                print ("Warning! I found a definition for the variable "+originalVarName+" in "+inputFilename+" but I was unable to parse the line to get a float.")
                print ("Here is the line in question:")
                print (line)
        elif intOrFloatOrString=="string":
            returnValue = line5
            numValidLines += 1

    if required and returnValue==None:
        print ("Error! Unable to find a valid setting for the scan variable "+originalVarName+" in "+inputFilename+".")
        print ("A definition should have the following form:")
        if intOrFloatOrString == "int":
            print (COMMENT_CODE+" "+originalVarName+" = 1")
        elif intOrFloatOrString == "float":
            print (COMMENT_CODE+" "+originalVarName+" = 1.5")
        elif intOrFloatOrString == "string":
            print (COMMENT_CODE+" "+originalVarName+" = nuPrime")
        exit(1)

    if numValidLines > 1:
        print ("Warning! More than 1 valid definition was found for the variable "+originalVarName+". The last one will be used.")

    print ("Read "+originalVarName+" = "+str(returnValue))
    return returnValue


def readVariable(inputFile, varName, intOrFloatOrString, required=True, inputFilename=INPUT_FILENAME):
    # This function reads normal fortran variables from the input.namelist file.
    # inputFile is list of strings

    if (intOrFloatOrString != "int") and (intOrFloatOrString != "float") and (intOrFloatOrString != "string"):
        print ("intOrFloatOrString must be int, float, or string.")
        exit(1)

    originalVarName = varName
    #varName = varName.lower()
    returnValue = None
    numValidLines = 0
    for line in inputFile:
        #line3 = line.strip().lower()
        line3 = line.strip()
        if len(line3)<1:
            continue

        if line3[0]=="!":
            continue

        if len(line3) < len(varName)+2:
            continue

        if not line3[:len(varName)].lower()==varName.lower():
            continue

        line4 = line3[len(varName):].strip()

        if not line4[0] =="=":
            continue

        line5 = line4[1:].strip();
        if intOrFloatOrString != "string":
            # python does not recognize fortran's 1d+0 scientific notation
            line5 = line5.replace('d','e').replace('D','e')

        # Remove any comments:
        if "!" in line5:
            try:
                line5 = line5[:line5.find("!")]
                line5 = line5.strip()
            except:
                pass

        if intOrFloatOrString=="int":
            try:
                returnValue = int(line5)
                numValidLines += 1
            except:
                print ("Warning! I found a definition for the variable "+originalVarName+" in "+inputFilename+" but I was unable to parse the line to get an integer.")
                print ("Here is the line in question:")
                print (line)
        elif intOrFloatOrString=="float":
            try:
                returnValue = float(line5)
                numValidLines += 1
            except:
                print ("Warning! I found a definition for the variable "+originalVarName+" in "+inputFilename+" but I was unable to parse the line to get a float.")
                print ("Here is the line in question:")
                print (line)
        elif intOrFloatOrString=="string":
            returnValue = line5
            numValidLines += 1

    if required and returnValue==None:
        print ("Error! Unable to find a valid setting for the variable "+originalVarName+" in "+inputFilename+".")
        exit(1)

    if numValidLines > 1:
        print ("Warning! More than 1 valid definition was found for the variable "+originalVarName+". The last one will be used.")

    print ("Read "+originalVarName+" = "+str(returnValue))
    return returnValue


def readDefault(varName, intOrFloatOrString, required=True):
    # This function reads the default value of fortran variables defined in globalVariables.F90.
    # If found it returns the last occurence of the variable, otherwise None.

    if (intOrFloatOrString != "int") and (intOrFloatOrString != "float") and (intOrFloatOrString != "string"):
        print ("intOrFloatOrString must be int, float, or string.")
        exit(1)

    originalVarName = varName
    #varName = varName.lower()                                                                                                                      
    returnValue = None
    numValidLines = 0

    try: 
        working_dir = os.getcwd() ##Store current working directory
        os.chdir(os.path.dirname(os.path.abspath(__file__))) ##Go to directory of this file
        defaultVariablesFile = open(os.path.join('../', DEFAULT_VARIABLES_FILENAME), 'r') ##Open file
        os.chdir(working_dir) ##Go back to working directory
    except:
        print ("Error! Unable to open "+DEFAULT_VARIABLES_FILENAME+".")
        if required:
            raise
        else:
            return returnValue

    for line in defaultVariablesFile:

        #line3 = line.strip().lower()                                                                                                               
        line3 = line.strip()
        if len(line3)<1:
            continue

        if line3[0]=="!":
            continue

        if len(line3) < len(varName)+2:
            continue

        begin_index = line3.lower().find(varName.lower())
        
        if begin_index == -1: #Cannot find varName on this line
            continue

        if begin_index != 0 and line3[begin_index-1] != ' ': #If character before varName is not a blank space, this is the wrong variable  
            continue

        line3 = line3.replace(" ", "")

        start_index = line3.lower().find(varName.lower())
                
        line4 = line3[start_index:].strip()

        
        if len(line4) < len(varName)+2:
            continue 

        if not line4[len(varName)] =="=":
            continue

        line5 = line4[len(varName)+1:].strip();
        line5 = line5.split(',')[0] ##Needed if several variables are defined on the same line  

        if intOrFloatOrString != "string":
            # python does not recognize fortran's 1d+0 scientific notation                                                                          
            line5 = line5.replace('d','e').replace('D','e')
 
        # Remove any comments:                                                                                                                      
        if "!" in line5:
            try:
                line5 = line5[:line5.find("!")]
            except:
                pass
           
        if intOrFloatOrString=="int":
            try:
                returnValue = int(line5)
                numValidLines += 1
            except:
                print ("Warning! I found a definition for the variable "+originalVarName+" in "+DEFAULT_VARIABLES_FILENAME+" but I was unable to parse the line to get an integer.")
                print ("Here is the line in question:")
                print (line)
        elif intOrFloatOrString=="float":
            try:
                returnValue = float(line5)
                numValidLines += 1
            except:
                print ("Warning! I found a definition for the variable "+originalVarName+" in "+DEFAULT_VARIABLES_FILENAME+" but I was unable to parse the line to get a float.")
                print ("Here is the line in question:")
                print (line)
        elif intOrFloatOrString=="string":
            returnValue = line5
            numValidLines += 1

    if required and returnValue==None:
        print ("Error! Unable to find a valid setting for the variable "+originalVarName+" in "+DEFAULT_VARIABLES_FILENAME+".")
        exit(1)

    if numValidLines > 1:
        print ("Warning! More than 1 valid definition was found for the variable "+originalVarName+". The last one will be used.")

    print ("Read "+originalVarName+" = "+str(returnValue))
    return returnValue
