skipExistingDirectories = False
filename = "input.namelist"
jobFilename = "job.sfincsScan"
commentCode = "!ss"

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
    if len(line2)<len(commentCode):
        return False

    if line2[:len(commentCode)] != commentCode:
        return False

    # If we got this far, the line must begin with !ss, so strip this part out.
    line2 = line2[len(commentCode):].strip()

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