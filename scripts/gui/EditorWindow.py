from PySide2 import QtWidgets
import maya.OpenMayaUI as mui
import shiboken2
import maya.cmds as mc
from building_generator import *
from models.UserProfile import *
from TemplateTab import TemplateTab
from BuildingEditorTab import BuildingEditorTab


# main window of the editor
class EditorWindow():

    # elements
    _window = None

    _window_name = 'Building Generator'
    _central_widget = None
    _central_layout = None

    user_profile = None
    _generator = None

    # sizes
    _min_size_x = 400
    _min_size_y = 820

    def __init__(self):
        self.user_profile = UserProfile.load()
        self.create_ui()

    # region UI Creation
    def create_ui(self):

        # get a Pointer to Maya`s Main UI
        window_pointer = mui.MQtUtil.mainWindow()

        # wrap the Pointer into a QWidget
        maya_ui = shiboken2.wrapInstance( long(window_pointer), QtWidgets.QWidget)

        # delete the window if it already exists
        self.delete_ui()

        # create the main window widget
        self._window = QtWidgets.QMainWindow(maya_ui)

        # set title
        self._window.setWindowTitle("Building Generator")

        # name it, so we can delete it later
        self._window.setObjectName(self._window_name)

        # set min size
        self._window.setMinimumSize(self._min_size_x, self._min_size_y)

        # main Layout and Widget
        self._central_widget = QtWidgets.QTabWidget()
        self._central_layout = QtWidgets.QVBoxLayout( self._central_widget )
        self._window.setCentralWidget(self._central_widget)

        # create generator
        self._generator = BuildingGenerator()

        # add tabs
        self._central_widget.addTab(BuildingEditorTab(self._generator, self), "Editor")
        self._central_widget.addTab(TemplateTab(self._generator, self), "Templates")

        # show
        self._window.show()

    def delete_ui(self):
        if mc.window(self._window_name, exists=True):
            mc.deleteUI(self._window_name)
    # endregion