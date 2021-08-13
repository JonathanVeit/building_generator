import inspect
import json
import os
import random
from functools import partial
from PySide2.QtCore import Qt, Signal
from PySide2 import QtGui
from maya.OpenMaya import MEventMessage

from BaseTab import *

# floor types
floor, highest_floor, lowes_floor, ground, roof = range(5)


# tab for editing the bulding
class BuildingEditorTab(BaseTab):
    # sizes
    top_height = 90

    floor_height = 100
    floor_width = 250
    floor_spacing = 5

    roof_height = 50
    ground_height = 100
    add_button_size = (25, 25)

    # currently edited building
    _current_building = None
    _selected_floor_level = None
    _block_floor_deselection = False

    def __init__(self, generator, window=None):
        BaseTab.__init__(self, generator, window)

        # align to bottom
        self._main_layout.setAlignment(Qt.AlignBottom)

        # for information
        self._top_layout = None
        # for editor
        self._editor_layout = None
        # for helper
        self._helper_layout = None

        # widget for scroll area
        self._scroll_area = None
        # layout of scroll area
        self._scroll_layout = None
        # widget to be scrolled
        self._scroll_widget = None

        # number next to floor
        self._floor_level_layout = None
        # floor
        self._floor_layout = None
        # buttons to add new floors
        self._floor_add_btn_layout = None

        self._try_load_cur_building()
        self._create_ui()

        # subscribe to event
        MEventMessage.addEventCallback("SelectionChanged", self._selection_changed)

    def __del__(self):
        # unsubscribe
        MEventMessage.removeCallback("SelectionChanged", self._selection_changed)

    # region UI Creation
    def _create_ui(self):
        # layout for upper part
        self._top_layout = QtWidgets.QHBoxLayout()

        # layout for editor
        self._editor_layout = QtWidgets.QHBoxLayout()
        self._editor_layout.setAlignment(Qt.AlignBottom)

        # layout for helper
        self._helper_layout = QtWidgets.QGridLayout()

        # add layouts
        self._main_layout.addLayout(self._top_layout)
        self._main_layout.addLayout(self._editor_layout)
        self._main_layout.addLayout(self._helper_layout)

        self._create_top_menu()
        self._create_editor_ui()
        self._create_helper_ui()

        if self._current_building is not None:
            self._refresh_editor()

    def _create_top_menu(self):
        # background widget
        self._top_widget = QtWidgets.QLabel()
        self._top_widget.setFixedHeight(self.top_height)
        self._top_widget.setStyleSheet("QLabel { "
                                "font-size: 20; "
                                "border: 2px solid #2e2e2e;"
                                "border-radius: 4;"
                                "}")

        # add to top layout
        self._top_layout.addWidget(self._top_widget)

        # set layout
        layout = QtWidgets.QGridLayout()
        self._top_widget.setLayout(layout)

        # name caption
        self._building_name_caption = QtWidgets.QLabel("Building: ")
        self._building_name_caption.setStyleSheet("QLabel {"
                                                "font-size: 20px; "
                                                "font-weight:bold;"
                                                "border: 0px solid #2e2e2e;"
                                                "border-radius: 0;"
                                                "}")

        # add to layout
        layout.addWidget(self._building_name_caption, 1, 1)

        # name label
        self._building_name_label = QtWidgets.QLabel()
        self._building_name_label.setStyleSheet("QLabel { "
                                "font-size: 20px;"
                                "font-weight:bold;"
                                "border: 2px solid #2e2e2e;"
                                "border-radius: 2;"
                                "background-color: #303030;"
                                "}")

        if self._current_building is not None:
            self._building_name_label.setText(self._current_building.get_object())
        else:
            self._building_name_label.setText("No building selected.")

        # add to layout
        layout.addWidget(self._building_name_label, 1, 2)

        # open button
        open_button = QtWidgets.QPushButton("Open Selected")
        open_button.clicked.connect(self._open_selected_building)
        layout.addWidget(open_button, 2, 1)

        # new button
        create_button = QtWidgets.QPushButton("New Building")
        create_button.clicked.connect(self._create_new_building)
        layout.addWidget(create_button, 2, 2)

    def _create_editor_ui(self):
        # layout for floor numbers
        self._floor_level_layout = QtWidgets.QVBoxLayout()
        self._floor_level_layout.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        self._floor_level_layout.setSpacing(0)
        self._floor_level_layout.setMargin(0)

        # layout for floors
        self._floor_layout = QtWidgets.QVBoxLayout()
        self._floor_layout.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        self._floor_layout.setSpacing(0)
        self._floor_layout.setMargin(0)

        # layout for floor buttons
        self._floor_add_btn_layout = QtWidgets.QVBoxLayout()
        self._floor_add_btn_layout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        self._floor_add_btn_layout.setSpacing(0)
        self._floor_add_btn_layout.setMargin(0)

        # widget for scroll area
        self._scroll_area = QtWidgets.QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._editor_layout.addWidget(self._scroll_area)

        # layout of scroll are
        self._scroll_layout = QtWidgets.QHBoxLayout()

        # scrollable widget
        self._scroll_widget = QtWidgets.QWidget()
        self._scroll_widget.setLayout(self._scroll_layout)

        # add to scroll layout
        self._scroll_layout.addLayout(self._floor_level_layout)
        self._scroll_layout.addLayout(self._floor_layout)
        self._scroll_layout.addLayout(self._floor_add_btn_layout)

        # set scrollable widget to area
        self._scroll_area.setWidget(self._scroll_widget)

    def _create_helper_ui(self):
        # refresh button
        refresh_button = QtWidgets.QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_building)
        refresh_button.setToolTip("Refresh the current building with the same templates and seeds.")

        # randomize the current building
        randomize_button = QtWidgets.QPushButton("Randomize")
        randomize_button.clicked.connect(self._randomize_building)
        randomize_button.setToolTip("Randomize the current building with the same templates and new seeds.")

        # add to layout
        self._helper_layout.addWidget(refresh_button, 1, 1)
        self._helper_layout.addWidget(randomize_button, 1, 2)
    # endregion

    # region Editor
    def _refresh_editor(self):
        self._clear_editor_layout()

        # create floors
        floor_amount = self._current_building.get_floor_count()

        for i in range(0, floor_amount + 1):
            # floor
            if i == floor_amount:
                self._add_floor_widget(floor_amount - i,
                                       self._current_building.get_floor_at_level(floor_amount - i).get_template_id(),
                                       self.ground_height,
                                       ground,
                                       floor_amount - i == self._selected_floor_level)

                # number
                self._add_floor_number(str(floor_amount - i), self.ground_height)

                # empty space
                self._add_button_spacing(self.ground_height + (self.floor_spacing * 0.75))

            # roof
            elif i == 0:
                # widget
                self._add_floor_widget(floor_amount - i,
                                       self._current_building.get_roof().get_template_id(),
                                       self.roof_height,
                                       roof,
                                       floor_amount - i == self._selected_floor_level)

                # number
                self._add_floor_number(str(floor_amount - i), self.roof_height)

                # empty space
                self._add_button_spacing(self.roof_height + (self.floor_spacing * 0.5))

            # floor
            else:
                # widget
                if i == 1:
                    floor_type = highest_floor
                elif i == floor_amount - 1:
                    floor_type = lowes_floor
                else:
                    floor_type = floor
                self._add_floor_widget(floor_amount - i,
                                       self._current_building.get_floor_at_level(floor_amount - i).get_template_id(),
                                       self.floor_height,
                                       floor_type,
                                       floor_amount - i == self._selected_floor_level)

                # number
                self._add_floor_number(str(floor_amount - i), self.floor_height)

                # empty space
                self._add_button_spacing(self.floor_height + (self.floor_spacing * 0.5))

            # add "add" button
            if i != floor_amount:
                self._add_floor_button(floor_amount - i)

    def _clear_editor_layout(self):
        # clear floors
        while self._floor_layout.count():
            child = self._floor_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # clear add buttons
        while self._floor_add_btn_layout.count():
            child = self._floor_add_btn_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # clear floor level
        while self._floor_level_layout.count():
            child = self._floor_level_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _add_floor_widget(self, level, template_id="my_template", height=100, floor_type=floor, is_selected=False):
        # roof
        if floor_type == roof:
            new_floor = FloorWidget(level,
                                    self._current_building.get_floor_count(),
                                    floor_type,
                                    template_id,
                                    self._window.user_profile.get_cur_template().get_valid_roof_templates(),
                                    self.floor_width,
                                    height,
                                    self.floor_spacing,
                                    is_selected)
        # floor
        else:
            new_floor = FloorWidget(level,
                                    self._current_building.get_floor_count(),
                                    floor_type,
                                    template_id,
                                    self._window.user_profile.get_cur_template().get_valid_floor_templates(),
                                    self.floor_width,
                                    height,
                                    self.floor_spacing,
                                    is_selected)

        # connect signals
        new_floor.on_move_up_pressed.connect(self._move_floor_up)
        new_floor.on_recreate_pressed.connect(self._recreate_floor)
        new_floor.on_move_down_pressed.connect(self._move_floor_down)
        new_floor.on_delete_pressed.connect(self._delete_floor)
        new_floor.on_select_pressed.connect(self._select_floor)

        # add to layout
        self._floor_layout.addWidget(new_floor)

    def _add_floor_number(self, level, height):
        # label
        level = QtWidgets.QLabel(str(level))
        level.setFixedWidth(20)
        level.setFixedHeight(height)

        font = QtGui.QFont("Calibri", 12, QtGui.QFont.Bold)
        level.setFont(font)

        # add to layout
        self._floor_level_layout.addWidget(level)

    def _add_button_spacing(self, height):
        space = QtWidgets.QLabel()
        space.setFixedHeight(height - self.add_button_size[1])
        self._floor_add_btn_layout.addWidget(space)

    def _add_floor_button(self, level):
        # create button
        button = QtWidgets.QPushButton("+")
        button.setToolTip("Add a new floor with the template of the one below.")
        button.clicked.connect(partial(self._add_floor, level))
        button.setFixedSize(self.add_button_size[0], self.add_button_size[1])

        font = QtGui.QFont("Calibri", 15, QtGui.QFont.Bold)
        button.setFont(font)

        # add to layout
        self._floor_add_btn_layout.addWidget(button)

    # endregion

    # region Signals
    def _create_new_building(self):
        # enough floor templates?
        if len(self._window.user_profile.get_cur_template().get_valid_floor_templates()) == 0:
            mc.confirmDialog(message="At least 1 valid floor template is required.")
            return

        # enough roof templates?
        if len(self._window.user_profile.get_cur_template().get_valid_roof_templates()) == 0:
            mc.confirmDialog(message="At least 1 valid roof template is required.")
            return

        # create window
        self._create_window = BuildingCreationWindow(
            self._window.user_profile.get_cur_template().get_valid_floor_templates(True),
            self._window.user_profile.get_cur_template().get_valid_roof_templates(True))

        self._create_window.setWindowModality(Qt.ApplicationModal)
        self._create_window.on_create_pressed.connect(self._on_create_building_pressed)

        self._create_window.show()

    def _on_create_building_pressed(self, building_id="new_building", floor_amount=1,
                                    floor_template_id="floor_template", roof_template_id="roof_template"):
        # building template
        building_template = self._window.user_profile.get_cur_template()

        # create empty building
        self._current_building = self._generator.create_empty_building(building_id, building_template)

        # set cur building in profile
        self._window.user_profile.set_cur_building(self._current_building.get_object())

        # save profile
        self._window.user_profile.save()

        # random templates
        if floor_template_id == "":
            valid_templates = building_template.get_valid_floor_templates()

            for i in range(floor_amount + 1):
                random_template = valid_templates[random.randint(0, len(valid_templates) - 1)]

                self._generator.create_floor(self._current_building,
                                             building_template,
                                             random_template,
                                             i)
        # given floor template
        else:
            for i in range(floor_amount + 1):
                self._generator.create_floor(self._current_building,
                                             building_template,
                                             building_template.get_floor_template(floor_template_id),
                                             i)

        # add roof
        # random template?
        if roof_template_id == "":
            valid_templates = building_template.get_valid_roof_templates()
            roof_template = valid_templates[random.randint(0, len(valid_templates) - 1)]
        # given template
        else:
            roof_template = building_template.get_roof_template(roof_template_id)

        self._generator.create_roof(self._current_building,
                                    building_template,
                                    roof_template)

        # set name label
        self._building_name_label.setText(building_id)

        # refresh
        self._refresh_editor()
        self._save_current_building()

    def _open_selected_building(self):
        selections = mc.ls(sl=True)
        for cur_selected in selections:
            key = Element.get_meta_data_key()

            # has meta data?
            if mc.attributeQuery(key, node=cur_selected, exists=True):
                # deserialize
                attr_value = mc.getAttr(cur_selected + '.' + key)
                serializable = json.loads(attr_value)
                self._current_building = Building.get_from_serializable(serializable)
                self._selected_floor_level = None

                # refresh
                self._refresh_editor()
                self._building_name_label.setText(cur_selected)

                # deselect
                mc.select(cl=True)
                return

        mc.confirmDialog(message="No valid building selected.")

    def _refresh_building(self):
        # no building?
        if self._current_building is None:
            return

        # loop floors
        for level in range(self._current_building.get_floor_count()):
            floor_at_level = self._current_building.get_floor_at_level(level)
            template_id = floor_at_level.get_template_id()

            # recreate with same seed
            self._recreate_floor(level, floor, template_id, floor_at_level.get_seed())

        # recreate roof
        current_roof = self._current_building.get_roof()
        template_id = current_roof.get_template_id()

        self._recreate_floor(0, roof, template_id, current_roof.get_seed())

    def _randomize_building(self):
        # no building?
        if self._current_building is None:
            return

        # confirm
        result = mc.confirmDialog(message="Are you sure you want to randomize the whole building?",
                                  button=["Confirm", "Abort"],
                                  defaultButton="Abort")

        if result == "Abort":
            return

        # loop floors
        for level in range(self._current_building.get_floor_count()):
            floor_at_level = self._current_building.get_floor_at_level(level)
            template_id = floor_at_level.get_template_id()

            # recreate with random seed
            self._recreate_floor(level, floor, template_id, None)

        # recreate roof
        current_roof = self._current_building.get_roof()
        template_id = current_roof.get_template_id()

        self._recreate_floor(0, roof, template_id, None)

    def _move_floor_up(self, level=0):
        self._generator.swap_floors(self._current_building,
                                    self._window.user_profile.get_cur_template(),
                                    level,
                                    level + 1)

        # move selected up?
        if level == self._selected_floor_level:
            self._selected_floor_level += 1

        # move up to selected?
        elif self._selected_floor_level is not None and level == self._selected_floor_level - 1:
            self._selected_floor_level -= 1

        # refresh
        self._refresh_editor()
        self._save_current_building()

    def _recreate_floor(self, level=0, floor_type=0, template="my_template", seed=None):
        # block deselection
        self._block_floor_deselection = True

        # recreate roof
        if floor_type is roof:
            self._generator.create_roof(self._current_building,
                                        self._window.user_profile.get_cur_template(),
                                        self._window.user_profile.get_cur_template().get_roof_template(template),
                                        seed)
        # recreate floor
        else:
            self._generator.create_floor(self._current_building,
                                         self._window.user_profile.get_cur_template(),
                                         self._window.user_profile.get_cur_template().get_floor_template(template),
                                         level,
                                         seed)

        # refresh
        self._refresh_editor()
        self._save_current_building()

        # select again
        if self._selected_floor_level is not None:
            self._select_floor(self._selected_floor_level, False)
        # deselect
        else:
            mc.select(cl=True)

        # unblock deselection
        self._block_floor_deselection = False

    def _move_floor_down(self, level=0):
        self._generator.swap_floors(self._current_building,
                                    self._window.user_profile.get_cur_template(),
                                    level,
                                    level - 1)

        # move selected?
        if level == self._selected_floor_level:
            self._selected_floor_level -= 1

        # move down to selected?
        elif self._selected_floor_level is not None and level == self._selected_floor_level + 1:
            self._selected_floor_level += 1

        # refresh
        self._refresh_editor()
        self._save_current_building()

    def _add_floor(self, level=0):
        # block deselection
        self._block_floor_deselection = True

        building_template = self._window.user_profile.get_cur_template()
        floor = self._current_building.get_floor_at_level(level - 1)
        floor_template = building_template.get_floor_template(floor._template_id)

        self._generator.insert_floor(self._current_building,
                                     self._window.user_profile.get_cur_template(),
                                     floor_template,
                                     level)

        # refresh
        self._refresh_editor()
        self._save_current_building()

        # move selected up?
        if level <= self._selected_floor_level:
            self._selected_floor_level += 1

        # select again
        if self._selected_floor_level is not None:
            self._select_floor(self._selected_floor_level, False)
        else:
            mc.select(cl=True)

        # unblock deselection
        self._block_floor_deselection = False

    def _delete_floor(self, level=0):
        # destroy floor
        self._generator.destroy_floor(self._current_building,
                                      self._window.user_profile.get_cur_template(),
                                      level)

        # unselect
        if level == self._selected_floor_level:
            self._selected_floor_level = None

        # move selected up?
        elif level < self._selected_floor_level:
            self._selected_floor_level -= 1

        # refresh
        self._refresh_editor()
        self._save_current_building()

    def _select_floor(self, level=0, auto_unselect=True):
        # block deselection
        self._block_floor_deselection = True

        # deselect
        if auto_unselect and level == self._selected_floor_level:
            mc.select(cl=True)
            self._selected_floor_level = None
            self._refresh_editor()
            return

        # select roof
        if level == self._current_building.get_floor_count():
            floor_root = self._current_building.get_roof().get_object()
        # select floor
        else:
            floor_root = self._current_building.get_floor_at_level(level).get_object()

        mc.select(floor_root)
        self._selected_floor_level = level
        self._refresh_editor()

        # unblock deselection
        self._block_floor_deselection = False

    def _selection_changed(self, selection):
        # blocked?
        if self._block_floor_deselection:
            return

        # no floor selected?
        if self._selected_floor_level is None:
            return

        selections = mc.ls(sl=True)

        # nothing selected?
        if len(selections) == 0:
            self._selected_floor_level = None
            self._refresh_editor()
            return

        # another object selected?
        if selections[0] != self._current_building.get_floor_at_level (self._selected_floor_level).get_object():
            self._selected_floor_level = None
            self._refresh_editor()
    # endregion

    # region Helper
    def _try_load_cur_building(self):
        id = self._window.user_profile.get_cur_building()
        key = Element.get_meta_data_key()

        # add selected
        all_objects = mc.ls(sl=False)
        for cur_object in all_objects:
            if cur_object == id:
                if mc.attributeQuery(key, node=cur_object, exists=True):
                    attr_value = mc.getAttr(cur_object + '.' + key)
                    serializable = json.loads(attr_value)
                    self._current_building = Building.get_from_serializable(serializable)
                    return

    def _save_current_building(self):
        if self._current_building is None:
            return

        serializable = self._current_building.get_serializable()
        self._current_building.write_metadata(json.dumps(serializable))
    # endregion


class FloorWidget(QtWidgets.QWidget):
    # signals
    on_move_up_pressed = Signal(int)
    on_recreate_pressed = Signal(int, int, str)
    on_move_down_pressed = Signal(int)
    on_delete_pressed = Signal(int)
    on_select_pressed = Signal(int)

    # sizes
    _button_size = (25, 25)
    _template_dropdown_width = 125

    def __init__(self, level=1, floor_count=1, floor_type=floor, template_id="floor_template",
                 templates=[], width=100, height=100, spacing=10, is_selected=False):
        QtWidgets.QWidget.__init__(self)

        # store values
        self._level = level
        self._floor_count = floor_count
        self._floor_type = floor_type
        self._template_id = template_id
        self._templates = templates
        self.height = height
        self.width = width
        self.spacing = spacing
        self._is_selected = is_selected

        # main layout
        self._main_layout = None
        # for widgets
        self._box_layout = None

        # widget of the floor
        self._floor_widget = None
        # layout of the floor
        self._floor_layout = None
        # dropdown for templates
        self._template_dropdown = None

        # set icon directory
        self._icon_dir = ""
        file_name = inspect.getfile(inspect.currentframe())
        dir_name = os.path.dirname(file_name)
        self._icon_dir = dir_name + "/../icons/"

        self.setMaximumHeight(self.height)

        self._create_ui()

    def _create_ui(self):
        # main layout
        self._main_layout = QtWidgets.QHBoxLayout()
        self._main_layout.setSpacing(0)
        self._main_layout.setMargin(0)
        self.setLayout(self._main_layout)

        self._create_basic_layout()

        # create edit ui depending on the floor type
        if self._floor_type is ground:
            self._create_edit_ui(True, False, False)
        elif self._floor_type is lowes_floor:
            self._create_edit_ui(True, True, True)
        elif self._floor_type is floor:
            self._create_edit_ui(True, True, True)
        elif self._floor_type is highest_floor:
            self._create_edit_ui(False, True, True)
        elif self._floor_type is roof:
            self._create_edit_ui(False, False, False)

    def _create_basic_layout(self):
        # main layout
        self._box_layout = QtWidgets.QVBoxLayout()
        self._box_layout.setSpacing(0)
        self._box_layout.setMargin(0)

        self._box_layout.setAlignment(Qt.AlignCenter)
        self._main_layout.addLayout(self._box_layout)

        # center
        self._floor_widget = QtWidgets.QLabel()
        if self._floor_type != roof:
            self._floor_widget.setFixedSize(self.width, self.height - self.spacing)
        else:
            self._floor_widget.setFixedSize(self.width, self.height)

        if self._is_selected:
            self._floor_widget.setStyleSheet("QLabel {"
                                             "background-color: grey;"
                                             "border: 2px solid #29ff6d;"
                                             "border-radius: 4;"
                                             "}")
        else:
            self._floor_widget.setStyleSheet("QLabel {"
                                             "background-color: grey;"
                                             "border: 2px solid #2e2e2e;"
                                             "border-radius: 4;"
                                             "}")

        # spacing
        space = QtWidgets.QLabel()
        space.setFixedHeight(self.spacing)

        # add widgets to layouts
        if self._floor_type != roof:
            self._box_layout.addWidget(space)
        self._box_layout.addWidget(self._floor_widget)

        # floor layout
        self._floor_layout = QtWidgets.QGridLayout()
        self._floor_widget.setLayout(self._floor_layout)

    def _create_edit_ui(self, move_up=True, move_down=True, delete=True):
        # up button
        if move_up and self._floor_count > 1:
            up_button = QtWidgets.QPushButton("")
            up_button.setToolTip("Move the floor one level up.")
            up_button.setFixedSize(self._button_size[0], self._button_size[1])
            up_button.clicked.connect(self._up_pressed)

            # icon
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(self._icon_dir + "arrow_up.png"))
            up_button.setIcon(icon)

            self._floor_layout.addWidget(up_button, 1, 1)

        # recreate button
        recreate_button = QtWidgets.QPushButton("")
        recreate_button.setToolTip("Recreate the floor with the given template and random seed.")
        recreate_button.setFixedSize(self._button_size[0], self._button_size[1])
        recreate_button.clicked.connect(self._recreated_pressed)

        # icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self._icon_dir + "refresh.png"))
        recreate_button.setIcon(icon)

        # add to layout
        self._floor_layout.addWidget(recreate_button, 2, 1)

        # template dropdown
        self._template_dropdown = QtWidgets.QComboBox()
        self._template_dropdown.setFixedSize(self._template_dropdown_width, self._button_size[1])
        for i in range(len(self._templates)):
            template_id = self._templates[i].id
            self._template_dropdown.addItem(template_id)

            if template_id == self._template_id:
                self._template_dropdown.setCurrentIndex(i)
        self._floor_layout.addWidget(self._template_dropdown, 2, 2, Qt.AlignLeft | Qt.AlignCenter)

        # down button
        if move_down:
            # button
            down_button = QtWidgets.QPushButton("")
            down_button.setToolTip("Move the floor one level down.")
            down_button.setFixedSize(self._button_size[0], self._button_size[1])
            down_button.clicked.connect(self._down_pressed)

            # icon
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(self._icon_dir + "arrow_down.png"))
            down_button.setIcon(icon)

            self._floor_layout.addWidget(down_button, 3, 1)
        elif self._floor_type is ground:
            empty = QtWidgets.QWidget()
            empty.setFixedSize(self._button_size[0], self._button_size[1])

            self._floor_layout.addWidget(empty, 3, 1)

        # delete button
        if delete:
            delete_button = QtWidgets.QPushButton("")
            delete_button.setToolTip("Delete the floor.")
            delete_button.setFixedSize(self._button_size[0], self._button_size[1])
            delete_button.clicked.connect(self._delete_pressed)

            # set icon
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(self._icon_dir + "delete.png"))
            delete_button.setIcon(icon)

            self._floor_layout.addWidget(delete_button, 1, 3, Qt.AlignRight | Qt.AlignTop)
        elif self._floor_type is ground:
            empty = QtWidgets.QWidget()
            empty.setFixedSize(self._button_size[0], self._button_size[1])

            self._floor_layout.addWidget(empty, 1, 3, Qt.AlignRight | Qt.AlignTop)
        elif self._floor_type is roof:
            empty = QtWidgets.QWidget()
            empty.setFixedSize(self._button_size[0], self._button_size[1])

            self._floor_layout.addWidget(empty, 2, 3, Qt.AlignRight | Qt.AlignTop)

        # select button
        select_button = QtWidgets.QPushButton("")
        select_button.setToolTip("Select the floor.")
        select_button.setFixedSize(self._button_size[0], self._button_size[1])
        select_button.clicked.connect(self._select_pressed)

        # icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self._icon_dir + "select.png"))
        select_button.setIcon(icon)

        # add to layout
        if self._floor_type is roof:
            self._floor_layout.addWidget(select_button, 2, 3, Qt.AlignRight | Qt.AlignTop)
        else:
            self._floor_layout.addWidget(select_button, 3, 3, Qt.AlignRight | Qt.AlignBottom)

    # region Signals
    def _up_pressed(self):
        self.on_move_up_pressed.emit(self._level)

    def _recreated_pressed(self):
        self.on_recreate_pressed.emit(self._level, self._floor_type, self._template_dropdown.currentText())

    def _down_pressed(self):
        self.on_move_down_pressed.emit(self._level)

    def _delete_pressed(self):
        self.on_delete_pressed.emit(self._level)

    def _select_pressed(self):
        self.on_select_pressed.emit(self._level)

    # endregion

    # region Helper
    def _get_part_name(self, part=floor):
        if part == floor:
            return "floor"
        elif part == roof:
            return "roof"
        elif part == ground:
            return "ground"
    # endregion


class BuildingCreationWindow(QtWidgets.QMainWindow):
    on_create_pressed = Signal(str, int, str, str)

    def __init__(self, floor_templates=[], roof_templates=[]):
        QtWidgets.QMainWindow.__init__(self)

        # set title of the window
        self.setWindowTitle("New Building")

        # set size
        self.setMinimumSize(350, 200)

        # save available templates
        self._floor_templates = floor_templates
        self._roof_templates = roof_templates

        # create central widgets
        central_widget = QtWidgets.QWidget()

        # central layout
        self._main_layout = QtWidgets.QGridLayout()

        central_widget.setLayout(self._main_layout)
        self.setCentralWidget(central_widget)

        # input fields
        self._id_field = None
        self.add_button = None
        self.abort_button = None

        self._create_ui()

    def _create_ui(self):
        # column in grid
        column = 1

        # id label
        self._input_label = QtWidgets.QLabel("Name:")
        self._main_layout.addWidget(self._input_label, column, 1)

        # add id field
        self._id_field = QtWidgets.QLineEdit()
        self._main_layout.addWidget(self._id_field, column, 2)

        column += 1

        # floor count label
        self._floor_count_label = QtWidgets.QLabel("Floors:")
        self._main_layout.addWidget(self._floor_count_label, column, 1)

        # floor count field
        self._floor_count_field = QtWidgets.QSpinBox()
        self._floor_count_field.setMinimum(1)
        self._main_layout.addWidget(self._floor_count_field, column, 2)

        column += 1

        # default floor template label
        self._floor_template_label = QtWidgets.QLabel("Floor template:")
        self._main_layout.addWidget(self._floor_template_label, column, 1)

        # default floor template dropdown
        self._floor_template_dropdown = QtWidgets.QComboBox()
        self._floor_template_dropdown.addItem("Random")
        for template_id in self._floor_templates:
            self._floor_template_dropdown.addItem(template_id)
        self._main_layout.addWidget(self._floor_template_dropdown, column, 2)
        column += 1

        # default roof template label
        self._roof_template_label = QtWidgets.QLabel("Roof template:")
        self._main_layout.addWidget(self._roof_template_label, column, 1)

        # default floor template dropdown
        self._roof_template_dropdown = QtWidgets.QComboBox()
        self._roof_template_dropdown.addItem("Random")
        for template_id in self._roof_templates:
            self._roof_template_dropdown.addItem(template_id)
        self._main_layout.addWidget(self._roof_template_dropdown, column, 2)

        column += 1

        # add button
        self._add_button = QtWidgets.QPushButton("Create")
        self._add_button.clicked.connect(self._on_create_pressed)
        self._main_layout.addWidget(self._add_button, column, 1)

        # abort button
        self._abort_button = QtWidgets.QPushButton("Abort")
        self._abort_button.clicked.connect(self._on_abort_pressed)
        self._main_layout.addWidget(self._abort_button, column, 2)

    # region Signals
    def _on_create_pressed(self):
        # no name?
        if self._id_field.text() == "" or self._id_field.text() is None:
            mc.confirmDialog(message="Please enter valid name.")
            return

        # already exists?
        if mc.objExists(self._id_field.text()):
            result = mc.confirmDialog(message="There is already a building with name \"" + self._id_field.text() + "\". It will be deleted.",
                                      button=["Ok", "Abort"],
                                      defaultButton="Abort")

            if result == "Abort":
                return

        # floor template id
        floor_template_id = None
        if self._floor_template_dropdown.currentText() != "Random":
            floor_template_id = self._floor_template_dropdown.currentText()

        # roof template id
        roof_template_id = None
        if self._roof_template_dropdown.currentText() != "Random":
            roof_template_id = self._roof_template_dropdown.currentText()

        # emit signal
        self.on_create_pressed.emit(self._id_field.text(),
                                    self._floor_count_field.value(),
                                    floor_template_id,
                                    roof_template_id)

        # hide
        self.hide()

    def _on_abort_pressed(self):
        self.hide()
    # endregion
