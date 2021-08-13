from BaseTab import *
from ListWidget import *
from CollapsibleWidget import *
from Vector3Widget import Vector3Widget
from maya.OpenMaya import MEventMessage


# tab for managing the templates
class TemplateTab(BaseTab):

    def __init__(self, generator, window=None):
        BaseTab.__init__(self, generator, window)

        # layouts
        self._top_layout = None
        self._edit_layout = None

        # elements
        self._template_list = None
        self._wall_list = None
        self._edge_list = None
        self._corner_list = None
        self._tile_list = None

        # working values
        self.settings_collapsed = True
        self.blueprints_collapsed = False

        self._displayed_template = None
        self._template_creation_window = None

        self._create_ui()

        # subscribe to event
        MEventMessage.addEventCallback("SceneOpened", self._scene_changed)

    def __del__(self):
        # unsubscribe events
        MEventMessage.removeCallback("SceneOpened", self._scene_changed)

    # region UI Creation
    def _create_ui(self):
        # layout for the template selection
        self._top_layout = QtWidgets.QVBoxLayout()
        self._main_layout.addLayout(self._top_layout)

        # layout for the template and blueprint editing
        self._edit_layout = QtWidgets.QVBoxLayout()
        self._main_layout.addLayout(self._edit_layout)

        self._main_layout.addStretch(1)

        # create ui
        self._create_template_selection()

    def _scene_changed(self, scene):
        self._select_template(self._displayed_template.id, False)

    def _create_template_selection(self):
        # template selection list
        self._template_list = ListWidget("Templates")
        self._template_list.set_name_style(20, True)

        # add blueprints
        for floor_template in self._window.user_profile.get_cur_template().get_all_floor_templates():
            self._template_list.add_item(floor_template.id, "icon_f")

        for roof_template in self._window.user_profile.get_cur_template().get_all_roof_templates():
            self._template_list.add_item(roof_template.id, "icon_r")

        # connect to signals
        self._template_list.on_add_item_pressed.connect(self._add_new_template)
        self._template_list.on_remove_item_pressed.connect(self._remove_template)
        self._template_list.on_item_selected.connect(self._select_template)

        # add template to layout
        self._top_layout.addWidget(self._template_list)

        # select template
        if self._template_list.get_item_count() > 0:
            self._template_list.select_item(0)
            self._select_template(self._template_list.get_selected_item())

    def _create_template_settings(self, template=None):
        if template is None:
            return

        column = 1
        lay = QtWidgets.QGridLayout()

        # name field
        id_caption = QtWidgets.QLabel("Name:")
        id_field = QtWidgets.QLineEdit()
        id_field.setText(template.id)
        id_field.textChanged.connect(self._set_template_id)

        lay.addWidget(id_caption, column, 1)
        lay.addWidget(id_field, column, 2)

        column += 1

        # unit fields
        unit_caption = QtWidgets.QLabel("Unit:")
        unit_field = Vector3Widget(template.unit)
        unit_field.on_value_changed.connect(self._set_template_unit)

        lay.addWidget(unit_caption, column, 1)
        lay.addWidget(unit_field, column, 2)

        column += 1

        # width fields
        width_caption = QtWidgets.QLabel("Width:")
        width_field = QtWidgets.QSpinBox()
        width_field.setMinimum(1)
        width_field.setValue(template.width)
        width_field.valueChanged.connect(self._set_template_width)

        lay.addWidget(width_caption, column, 1)
        lay.addWidget(width_field, column, 2)

        column += 1

        # depth field
        depth_caption = QtWidgets.QLabel("Depth:")
        depth_field = QtWidgets.QSpinBox()
        depth_field.setMinimum(1)
        depth_field.setValue(template.depth)
        depth_field.valueChanged.connect(self._set_template_depth)

        lay.addWidget(depth_caption, column, 1)
        lay.addWidget(depth_field, column, 2)

        # create collapsible widget
        box = CollapsibleWidget("Settings")
        self._edit_layout.addWidget(box)

        box.set_content_layout(lay)
        box.on_changed_folding.connect(self._on_settings_folded)
        if not self.settings_collapsed:
            box.on_pressed()

        self._main_layout.addStretch(1)

    def _create_blueprint_selection(self, template=None):
        if template is None:
            return

        if isinstance(template, FloorTemplate) == True:
            # wall list
            self._wall_list = ListWidget("Walls")
            self._wall_list.set_name_style(16, True)

            # add wall blueprints
            for wall in template.walls:
                color = QColor(255, 255, 255)
                if not Element.does_exist(wall):
                    color = QColor(255, 0, 0)
                self._wall_list.add_item(wall, None, color)

            # connect to signals
            self._wall_list.on_add_item_pressed.connect(self._add_wall_to_floor_template)
            self._wall_list.on_remove_item_pressed.connect(self._remove_wall_from_floor_template)
            self._wall_list.on_item_selected.connect(self._wall_item_selected)

            # corners list
            self._corner_list = ListWidget("Corners")
            self._corner_list.set_name_style(16, True)

            # add corner blueprints
            for corner in template.corners:
                color = QColor(255, 255, 255)
                if not Element.does_exist(corner):
                    color = QColor(255, 0, 0)
                self._corner_list.add_item(corner, None, color)

            # connect to signals
            self._corner_list.on_add_item_pressed.connect(self._add_corner_to_floor_template)
            self._corner_list.on_remove_item_pressed.connect(self._remove_corner_from_floor_template)
            self._corner_list.on_item_selected.connect(self._corner_item_selected)

            # create layout
            lay = QtWidgets.QVBoxLayout()
            lay.addWidget(self._wall_list)
            lay.addWidget(self._corner_list)

            # add layout to collapsible
            box = CollapsibleWidget("Blueprints")
            self._edit_layout.addWidget(box)

            box.set_content_layout(lay)
            box.on_changed_folding.connect(self._on_blueprints_folded)
            if not self.blueprints_collapsed:
                box.on_pressed()

        elif isinstance(template, RoofTemplate) == True:
            # edge list
            self._edge_list = ListWidget("Edges")
            self._edge_list.set_name_style(16, True)

            # connect to signals
            self._edge_list.on_add_item_pressed.connect(self._add_edge_to_roof_template)
            self._edge_list.on_remove_item_pressed.connect(self._remove_edge_from_roof_template)
            self._edge_list.on_item_selected.connect(self._edge_item_selected)

            # add edge blueprints
            for edge in template.edges:
                color = QColor(255, 255, 255)
                if not Element.does_exist(edge):
                    color = QColor(255, 0, 0)
                self._edge_list.add_item(edge, None, color)

            # corner list
            self._corner_list = ListWidget("Corners")
            self._corner_list.set_name_style(16, True)

            # connect to signals
            self._corner_list.on_add_item_pressed.connect(self._add_corner_to_roof_template)
            self._corner_list.on_remove_item_pressed.connect(self._remove_corner_from_roof_template)
            self._corner_list.on_item_selected.connect(self._corner_item_selected)

            # add corner blueprints
            for corner in template.corners:
                color = QColor(255, 255, 255)
                if not Element.does_exist(corner):
                    color = QColor(255, 0, 0)
                self._corner_list.add_item(corner, None, color)

            # tiles list
            self._tile_list = ListWidget("Tiles")
            self._tile_list.set_name_style(16, True)

            # connect to signals
            self._tile_list.on_add_item_pressed.connect(self._add_tile_to_roof_template)
            self._tile_list.on_remove_item_pressed.connect(self._remove_tile_from_roof_template)
            self._tile_list.on_item_selected.connect(self._tile_item_selected)

            # add tile blueprints
            for tile in template.tiles:
                color = QColor(255, 255, 255)
                if not Element.does_exist(tile):
                    color = QColor(255, 0, 0)
                self._tile_list.add_item(tile, None, color)

            # create layout
            lay = QtWidgets.QVBoxLayout()
            lay.addWidget(self._edge_list)
            lay.addWidget(self._corner_list)
            lay.addWidget(self._tile_list)

            # add layout to collapsible
            box = CollapsibleWidget("Blueprints")
            self._edit_layout.addWidget(box)

            box.set_content_layout(lay)
            box.on_changed_folding.connect(self._on_blueprints_folded)
            if not self.blueprints_collapsed:
                box.on_pressed()

        self._main_layout.addStretch(1)

    def _clear_edit_layout(self):
        # no edit layout?
        if self._edit_layout is None:
            return

        try:
            # delete all widgets
            while self._edit_layout.count():
                child = self._edit_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        except:
            pass
    # endregion

    # region Template Selection Signals
    def _add_new_template(self):
        # create window
        self._template_creation_window = TemplateCreationWindow(self._window.user_profile.get_cur_template())
        self._template_creation_window.setWindowModality(QtCore.Qt.ApplicationModal)

        # connect event
        self._template_creation_window.on_template_created.connect(self._on_template_created)

        # show window
        self._template_creation_window.show()
        pass

    def _on_template_created(self, template=BaseTemplate()):
        # add to list
        if isinstance(template, FloorTemplate):
            self._template_list.add_item(template.id, "icon_f")
        elif isinstance(template, RoofTemplate):
            self._template_list.add_item(template.id, "icon_r")

        # add to tempplate
        self._window.user_profile.get_cur_template().add_template(template)

        # save
        self._window.user_profile.save()

    def _remove_template(self, template="new_item"):
        # confirm
        result = mc.confirmDialog(message="Are you sure you want to delete the template \"" + template + "\"?",
                                  button=["Yes", "No"],
                                  defaultButton="No")
        if result == "No":
            return

        # remove
        self._window.user_profile.get_cur_template().remove_template_by_id(template)
        self._template_list.remove_selected_item()

        # refresh
        self._select_template(self._template_list.get_selected_item())

        # save
        self._window.user_profile.save()

    def _select_template(self, blueprint="new_template", skip_displayed=True):
        # search selected template
        template = self._window.user_profile.get_cur_template().get_floor_template(blueprint)
        if template is None:
            template = self._window.user_profile.get_cur_template().get_roof_template(blueprint)

        # already displayed?
        if skip_displayed and template is self._displayed_template:
            return

        # recreate ui
        self._clear_edit_layout()
        self._create_template_settings(template)
        self._create_blueprint_selection(template)

        self._displayed_template = template

    # endregion

    # region Template Edit Signals
    def _set_template_id(self, id="new_id"):
        # skip empty
        if self._displayed_template is None:
            return

        # already exists?
        existing = self._window.user_profile.get_cur_template().get_template_by_id(id)
        if existing is not None:
            return

        self._template_list.rename_selected_item(id)
        self._displayed_template.id = id
        self._window.user_profile.save()

    def _set_template_unit(self, unit=(0, 0, 0)):
        if self._displayed_template is None:
            return

        self._displayed_template.unit = unit
        self._window.user_profile.save()

    def _set_template_width(self, width=0):
        if self._displayed_template is None:
            return

        self._displayed_template.width = width
        self._window.user_profile.save()

    def _set_template_depth(self, depth=0):
        if self._displayed_template is None:
            return

        self._displayed_template.depth = depth
        self._window.user_profile.save()

    # endregion

    # region Floor Template Signals
    def _add_wall_to_floor_template(self):
        # add selected
        selections = mc.ls(sl=True)
        for cur_selected in selections:

            # check if already added
            already_added = False
            for existing in self._displayed_template.walls:
                if existing == cur_selected:
                    mc.confirmDialog(message="The wall \"" +
                                             cur_selected +
                                             " \" has already been added to the template.",
                                     button=["Ok"], )

                    already_added = True
                    break

            if already_added:
                continue

            # add to template
            self._displayed_template.walls.append(cur_selected)

            # add to list
            self._wall_list.add_item(cur_selected)

        # save profile
        self._window.user_profile.save()

    def _remove_wall_from_floor_template(self, wall="new_wall"):
        # skip empty
        if not wall:
            return

        # dialog
        result = mc.confirmDialog(message="Are you sure you want to delete wall \"" + wall + "\" from template?",
                                  button=["Yes", "No"],
                                  defaultButton="No")

        if result == "No":
            return

        # remove from template
        self._displayed_template.walls.remove(wall)

        # remove from list
        self._wall_list.remove_selected_item()

        # save profile
        self._window.user_profile.save()

    def _add_corner_to_floor_template(self):
        # add selected
        selections = mc.ls(sl=True)
        for cur_selected in selections:

            # check if already added
            already_added = False
            for existing in self._displayed_template.corners:
                if existing == cur_selected:
                    mc.confirmDialog(message="The corner \"" +
                                             cur_selected +
                                             " \" has already been added to the template.",
                                     button=["Ok"],
                                     defaultButton="Ok")

                    already_added = True
                    break

            if already_added:
                continue

            # add to template
            self._displayed_template.corners.append(cur_selected)

            # add to list
            self._corner_list.add_item(cur_selected)

        # save profile
        self._window.user_profile.save()

    def _remove_corner_from_floor_template(self, corner="new_wall"):
        # skip empty
        if not corner:
            return

        # dialog
        result = mc.confirmDialog(message="Are you sure you want to delete corner \"" + corner + "\" from template?",
                                  button=["Yes", "No"],
                                  defaultButton="No")

        if result == "No":
            return

        # remove from template
        self._displayed_template.corners.remove(corner)

        # remove from list
        self._corner_list.remove_selected_item()

        # save profile
        self._window.user_profile.save()

    # endregion

    # region Roof Template Signals
    def _add_edge_to_roof_template(self):
        # add selected
        selections = mc.ls(sl=True)
        for cur_selected in selections:

            # check if already added
            already_added = False
            for existing in self._displayed_template.edges:
                if existing == cur_selected:
                    mc.confirmDialog(message="The edge \"" +
                                             cur_selected +
                                             " \" has already been added to the template.",
                                     button=["Ok"],
                                     defaultButton="Ok")
                    already_added = True
                    break

            if already_added:
                continue

            # add to template
            self._displayed_template.edges.append(cur_selected)

            # add to list
            self._edge_list.add_item(cur_selected)

        # save profile
        self._window.user_profile.save()

    def _remove_edge_from_roof_template(self, edge="new_edge"):
        # skip empty
        if not edge:
            return

        # dialog
        result = mc.confirmDialog(message="Are you sure you want to delete edge \"" + edge + "\" from template?",
                                  button=["Yes", "No"],
                                  defaultButton="No")

        if result == "No":
            return

        # remove from template
        self._displayed_template.edges.remove(edge)

        # remove from list
        self._edge_list.remove_selected_item()

        # save profile
        self._window.user_profile.save()

    def _add_corner_to_roof_template(self):
        # add selected
        selections = mc.ls(sl=True)
        for cur_selected in selections:

            # check if already added
            already_added = False
            for existing in self._displayed_template.corners:
                if existing == cur_selected:
                    mc.confirmDialog(message="The corner \"" +
                                             cur_selected +
                                             " \" has already been added to the template.",
                                     button=["Ok"],
                                     defaultButton="Ok")
                    already_added = True
                    break

            if already_added:
                continue

            # add to template
            self._displayed_template.corners.append(cur_selected)

            # add to list
            self._corner_list.add_item(cur_selected)

        # save profile
        self._window.user_profile.save()

    def _remove_corner_from_roof_template(self, corner="new_wall"):
        # skip empty
        if not corner:
            return

        # dialog
        result = mc.confirmDialog(message="Are you sure you want to delete corner \"" + corner + "\" from template?",
                                  button=["Yes", "No"],
                                  defaultButton="No")

        if result == "No":
            return

        # remove from template
        self._displayed_template.corners.remove(corner)

        # remove from list
        self._corner_list.remove_selected_item()

        # save profile
        self._window.user_profile.save()

    def _add_tile_to_roof_template(self):
        # add selected
        selections = mc.ls(sl=True)
        for cur_selected in selections:

            # check if already added
            already_added = False
            for existing in self._displayed_template.tiles:
                if existing == cur_selected:
                    mc.confirmDialog(message="The tile \"" +
                                             cur_selected +
                                             " \" has already been added to the template.",
                                     button=["Ok"],
                                     defaultButton="Ok")
                    already_added = True
                    break

            if already_added:
                continue

            # add to template
            self._displayed_template.tiles.append(cur_selected)

            # add to list
            self._tile_list.add_item(cur_selected)

        # save profile
        self._window.user_profile.save()

    def _remove_tile_from_roof_template(self, tile="new_wall"):
        # skip empty
        if not tile:
            return

        # dialog
        result = mc.confirmDialog(message="Are you sure you want to delete tile \"" + tile + "\" from template?",
                                  button=["Yes", "No"],
                                  defaultButton="No")

        if result == "No":
            return

        # remove from template
        self._displayed_template.tiles.remove(tile)

        # remove from list
        self._tile_list.remove_selected_item()

        # save profile
        self._window.user_profile.save()

    # endregion

    # region Signals for Lists in general
    def _on_settings_folded(self, collapsed):
        self.settings_collapsed = collapsed

    def _on_blueprints_folded(self, collapsed):
        self.blueprints_collapsed = collapsed

    def _edge_item_selected(self):
        # deselect other items
        try:
            self._corner_list.deselect_all_items()
        except:
            pass

        try:
            self._wall_list.deselect_all_items()
        except:
            pass

        try:
            self._tile_list.deselect_all_items()
        except:
            pass

    def _corner_item_selected(self):
        # deselect other items
        try:
            self._wall_list.deselect_all_items()
        except:
            pass

        try:
            self._edge_list.deselect_all_items()
        except:
            pass

        try:
            self._tile_list.deselect_all_items()
        except:
            pass

    def _tile_item_selected(self):
        # deselect other items
        try:
            self._corner_list.deselect_all_items()
        except:
            pass

        try:
            self._wall_list.deselect_all_items()
        except:
            pass

        try:
            self._edge_list.deselect_all_items()
        except:
            pass

    def _wall_item_selected(self):
        # deselect other items
        try:
            self._corner_list.deselect_all_items()
        except:
            pass

        try:
            self._edge_list.deselect_all_items()
        except:
            pass

        try:
            self._tile_list.deselect_all_items()
        except:
            pass
    # endregion


class TemplateCreationWindow(QtWidgets.QMainWindow):

    # add signal
    on_template_created = QtCore.Signal(BaseTemplate)

    def __init__(self, template=BuildingTemplate()):
        QtWidgets.QMainWindow.__init__(self)

        # set title
        self.setWindowTitle("New Template")

        # set size
        self.setMinimumSize(350, 200)

        # save template
        self._template = template

        # central widget
        central_widget = QtWidgets.QWidget()

        # main layout
        self._main_layout = QtWidgets.QGridLayout()

        central_widget.setLayout(self._main_layout)
        self.setCentralWidget(central_widget)

        # input fields
        self._id_field = None
        self._type_dropdown = None
        self.add_button = None
        self.abort_button = None

        self._create_ui()

    def _create_ui(self):
        column = 1

        # add input field
        self._id_label = QtWidgets.QLabel("Name:")
        self._main_layout.addWidget(self._id_label, column, 1)
        self._id_field = QtWidgets.QLineEdit()
        self._main_layout.addWidget(self._id_field, column, 2)

        column += 1

        # type dropdown
        self._type_dropdown_label = QtWidgets.QLabel("Type:")
        self._main_layout.addWidget(self._type_dropdown_label, column, 1)
        self._type_dropdown = QtWidgets.QComboBox()
        self._type_dropdown.addItem("Floor Template")
        self._type_dropdown.addItem("Roof Template")
        self._main_layout.addWidget(self._type_dropdown, column, 2)

        column += 1

        # unit field
        self._unit_label = QtWidgets.QLabel("Unit:")
        self._unit_field = Vector3Widget((1, 1, 1))
        self._main_layout.addWidget(self._unit_label, column, 1)
        self._main_layout.addWidget(self._unit_field, column, 2)

        column += 1

        # width field
        self._with_label = QtWidgets.QLabel("Width:")
        self._width_field = QtWidgets.QSpinBox()
        self._width_field.setValue(1)
        self._width_field.setMinimum(1)
        self._main_layout.addWidget(self._with_label, column, 1)
        self._main_layout.addWidget(self._width_field, column, 2)

        column += 1

        # depth field
        self._depth_label = QtWidgets.QLabel("Depth:")
        self._depth_field = QtWidgets.QSpinBox()
        self._depth_field.setValue(1)
        self._depth_field.setMinimum(1)
        self._main_layout.addWidget(self._depth_label, column, 1)
        self._main_layout.addWidget(self._depth_field, column, 2)

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
        existing = self._template.get_template_by_id(self._id_field.text())
        if existing is not None:
            mc.confirmDialog(message="There is already a template with name \"" + self._id_field.text() + "\".")
            return

        # new floor template
        if self._type_dropdown.currentIndex() == 0:
            floor_template = FloorTemplate(self._id_field.text(),
                                           self._unit_field.get_value(),
                                           self._width_field.value(),
                                           self._depth_field.value(), [], [])
            self.on_template_created.emit(floor_template)

        # new floor template
        elif self._type_dropdown.currentIndex() == 1:
            roof_template = RoofTemplate(self._id_field.text(),
                                         self._unit_field.get_value(),
                                         self._width_field.value(),
                                         self._depth_field.value(), [], [], [])
            self.on_template_created.emit(roof_template)

        self.hide()

    def _on_abort_pressed(self):
        self.hide()
    # endregion
