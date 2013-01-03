"""
shenv.py - Show environment variables.

Ned Batchelder, http://www.nedbatchelder.com
"""

import os, sys

def showVar(varName, indent=''):
    val = os.environ[varName]
    for p in val.split(';'):
        print indent, p

def showVars(prefix):
    varNames = os.environ.keys()
    varNames.sort()
    for varName in varNames:
        if varName.lower().startswith(prefix.lower()):
            print varName
            showVar(varName, '   ')
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        showVars(sys.argv[1])
    else:
        showVars('')
