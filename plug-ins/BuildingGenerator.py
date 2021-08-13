import maya.api.OpenMaya as om
import inspect
import os
import sys
from gui.MenuEntry import*

# menu to create
menu_entry = None


def maya_useNewAPI():
    pass


def initializePlugin(mobject):
    # define plugin
    mplugin = om.MFnPlugin(mobject, "Jonathan Veit", "1.0", "Any")

    # append directory name
    file_name = inspect.getfile(inspect.currentframe())
    dir_name = os.path.dirname(file_name)
    sys.path.append(dir_name)

    # create menu entry
    global menu_entry
    menu_entry = MenuEntry()
    menu_entry.create()

    print "Loaded Building Generator plugin"


def uninitializePlugin(mobject):
    # destroy menu entry
    global menu_entry
    menu_entry.destroy()

    print "Unloaded Building Generator plugin"
