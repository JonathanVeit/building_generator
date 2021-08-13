from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2.QtCore import Signal
from PySide2.QtGui import QIcon
from PySide2.QtGui import QColor
import inspect
import os


# Widget with a list and two buttons (add, remove)
class ListWidget(QtWidgets.QWidget):

    # Signals
    on_add_item_pressed = Signal()
    on_remove_item_pressed = Signal(str)
    on_item_selected = Signal(str)

    def __init__(self, name="new_list", max_height=140):
        QtWidgets.QWidget.__init__(self)

        # define variables
        self._name = name
        self._max_height = max_height
        self._name_label = None
        self._selection_list = None
        self._add_button = None
        self._remove_button = None

        # set maximum height
        self.setMaximumHeight(self._max_height)

        # set icon directory
        self._icon_dir = ""
        file_name = inspect.getfile(inspect.currentframe())
        dir_name = os.path.dirname(file_name)
        self._icon_dir = dir_name + "/../icons/"

        # build ui
        self._main_layout = QtWidgets.QVBoxLayout(self)
        self.create_ui()

    def create_ui(self):
        # create name widget
        self._name_label = QtWidgets.QLabel(self._name)
        self._main_layout.addWidget(self._name_label)

        # create top layout
        list_layout = QtWidgets.QHBoxLayout(self)
        list_layout.setAlignment(QtCore.Qt.AlignTop)

        # add to vertical layout
        self._main_layout.addLayout(list_layout)

        # selection widget
        self._selection_list = QtWidgets.QListWidget()
        self._selection_list.setAlternatingRowColors(True)
        self._selection_list.setDragDropMode(
            QtWidgets.QAbstractItemView.InternalMove
        )
        self._selection_list.itemClicked.connect(self._item_clicked)

        list_layout.addWidget(self._selection_list)

        # create button layout
        button_layout = QtWidgets.QVBoxLayout(self)
        button_layout.setAlignment(QtCore.Qt.AlignTop)

        # add to main layout
        list_layout.addLayout(button_layout)

        # create buttons
        self._add_button = QtWidgets.QPushButton("Add")
        self._add_button.clicked.connect(self._add_pressed)

        self._remove_button = QtWidgets.QPushButton("Remove")
        self._remove_button.clicked.connect(self._remove_pressed)

        # add buttons to the layout
        button_layout.addWidget(self._add_button)
        button_layout.addWidget(self._remove_button)

    # region Modifications
    def set_name_style(self, size=16, bold=False):
        sheet = "QLabel { font-size: " + str(size) + "px; "
        if bold:
            sheet += "font-weight:bold;"
        sheet += "}"
        self._name_label.setStyleSheet(sheet)

    # endregion

    # region Signals
    def _add_pressed(self):
        self.on_add_item_pressed.emit()

    def _remove_pressed(self):
        self.on_remove_item_pressed.emit(self.get_selected_item())

    def _item_clicked(self, item=QtWidgets.QListWidgetItem()):
        self.on_item_selected.emit(item.text())
    # endregion

    # methods
    def get_selected_item(self):
        if len(self._selection_list.selectedItems()) == 0:
            return None

        return self._selection_list.selectedItems()[0].text()

    def select_item(self, at_index=0):
        self._selection_list.item(at_index).setSelected(True)

    def deselect_all_items(self):
        for i in range(self._selection_list.count()):
            self._selection_list.item(i).setSelected(False)

    def get_item_count(self):
        return self._selection_list.count()

    def add_item(self, name="new_item", icon="", color=QColor.fromRgb(255, 255, 255)):
        # create item
        new_item = QtWidgets.QListWidgetItem(name)
        new_item.setSizeHint(QtCore.QSize(new_item.sizeHint().width(), 20))

        # set icon if given
        if icon is not "" and icon is not None:
            new_item.setIcon(QIcon(self._icon_dir + icon))
        new_item.setTextColor(color)

        self._selection_list.addItem(new_item)

    def remove_selected_item(self):
        self._selection_list.takeItem(self._selection_list.indexFromItem(self._selection_list.currentItem()).row())

    def rename_selected_item(self, name="new_name"):
        self._selection_list.currentItem().setText(name)