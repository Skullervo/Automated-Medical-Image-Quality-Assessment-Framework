
import sys
import os

def addPathToSysPath(newPath):
    """Lisää uuden polun Pythonin sys.path -muuttujaan, ellei se jo ole listassa."""
    if newPath not in sys.path:
        sys.path.insert(0, newPath)
        print(f"Added {newPath} to sys.path")
    else:
        print(f"{newPath} is already in sys.path")

def setupIqToolPath():
    """Konfiguroi ja lisää 'Automated IQ Tool' -kansion polun sys.pathiin."""
    currentDirectory = os.getcwd()
    toolPath = os.path.join(currentDirectory, 'Automated IQ Tool')
    addPathToSysPath(toolPath)
    


