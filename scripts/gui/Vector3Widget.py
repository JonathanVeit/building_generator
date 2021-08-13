from PySide2 import QtWidgets
from PySide2.QtCore import Signal


# widget to get input for vector 3 types
class Vector3Widget(QtWidgets.QWidget):

    # Signals
    on_value_changed = Signal(tuple)

    _main_layout = None

    def __init__(self, value=(0, 0, 0)):
        QtWidgets.QWidget.__init__(self)

        self._value = value

        # main layout
        self._main_layout = QtWidgets.QGridLayout()
        self._main_layout.setSpacing(0)
        self.setLayout(self._main_layout)

        # input fields
        self._unit_1_field = None
        self._unit_2_field = None
        self._unit_3_field = None

        self._create_ui()

    def _create_ui(self):
        # field for value x
        self._unit_1_field = QtWidgets.QSpinBox()
        self._unit_1_field.setValue(self._value[0])
        self._unit_1_field.editingFinished.connect(self._on_field_value_changed)

        # field for value y
        self._unit_2_field = QtWidgets.QSpinBox()
        self._unit_2_field.setValue(self._value[1])
        self._unit_2_field.editingFinished.connect(self._on_field_value_changed)

        # field for value z
        self._unit_3_field = QtWidgets.QSpinBox()
        self._unit_3_field.setValue(self._value[2])
        self._unit_3_field.editingFinished.connect(self._on_field_value_changed)

        # add to layout
        self._main_layout.addWidget(self._unit_1_field, 1, 2)
        self._main_layout.addWidget(self._unit_2_field, 1, 3)
        self._main_layout.addWidget(self._unit_3_field, 1, 4)

    def _on_field_value_changed(self, value=0):
        self.on_value_changed.emit(self.get_value())

    def get_value(self):
        return (self._unit_1_field.value(), self._unit_2_field.value(), self._unit_3_field.value())