from PySide2 import QtWidgets
from PySide2 import QtCore


# Widget which can be folded and unfolded
class CollapsibleWidget(QtWidgets.QWidget):

    on_changed_folding = QtCore.Signal(bool)

    def __init__(self, title="", parent=None):
        super(CollapsibleWidget, self).__init__(parent)

        # create folding button
        self.folding_button = QtWidgets.QToolButton(
            text=title, checkable=True, checked=False
        )
        self.folding_button.setStyleSheet("QToolButton { border: none; }")
        self.folding_button.setToolButtonStyle(
            QtCore.Qt.ToolButtonTextBesideIcon
        )
        self.folding_button.setArrowType(QtCore.Qt.RightArrow)
        self.folding_button.pressed.connect(self.on_pressed)

        # animation for folding
        self.toggle_animation = QtCore.QParallelAnimationGroup(self)

        # content area
        self.content_area = QtWidgets.QScrollArea(maximumHeight=0, minimumHeight=0)
        self.content_area.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.content_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        # main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # add widgets to layout
        layout.addWidget(self.folding_button)
        layout.addWidget(self.content_area)

        # add animations
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        )

    @QtCore.Slot()
    def on_pressed(self):
        # is folded?
        folded = self.folding_button.isChecked()

        # change arrow
        self.folding_button.setArrowType(
            QtCore.Qt.DownArrow if not folded else QtCore.Qt.RightArrow
        )

        # set animation direction
        self.toggle_animation.setDirection(
            QtCore.QAbstractAnimation.Forward
            if not folded
            else QtCore.QAbstractAnimation.Backward
        )

        # start animation
        self.toggle_animation.start()

        # emit signal
        self.on_changed_folding.emit(folded)

    def set_content_layout(self, layout):
        # delete layout
        lay  = self.content_area.layout()
        del lay

        # add layout
        self.content_area.setLayout(layout)

        # set height for folding
        folded_height = (
            self.sizeHint().height() - self.content_area.maximumHeight()
        )
        content_height = layout.sizeHint().height()

        # set animation
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(0)
            animation.setStartValue(folded_height)
            animation.setEndValue(folded_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(0)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)