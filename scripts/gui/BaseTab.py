from EditorWindow import *
from PySide2.QtCore import Qt


# Base class for Tabs, containing the BuildingGenerator and the EditorWindow
class BaseTab(QtWidgets.QWidget):

    def __init__(self, generator, window=None):
        QtWidgets.QWidget.__init__(self)

        self._main_layout = QtWidgets.QVBoxLayout()
        self._main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self._main_layout)
        self._generator = generator
        self._window = window