from EditorWindow import *


class MenuEntry():

    # naming and ids
    _menu_id = "main_menu"
    _menu_item_id = "main_menu_item"

    _menu_caption = "Tools"
    _menu_item_caption = "Building Generator"

    _widget = None

    def __init__(self):
        pass

    def create (self):
        # delete existing menu
        if mc.menu(self._menu_id, query=True, exists=True):
            mc.deleteUI(self._menu_id)

        # add menu
        mc.menu(self._menu_id,
                parent="MayaWindow",
                label=self._menu_caption)

        # add menu item
        mc.menuItem(self._menu_item_id,
                    parent=self._menu_id,
                    label=self._menu_item_caption,
                    command=self.__open_window)

    def destroy (self):
        if mc.menu(self._menu_id, query=True, exists=True):
            mc.deleteUI(self._menu_id)

    def __open_window(self, *args):
        _window = EditorWindow()