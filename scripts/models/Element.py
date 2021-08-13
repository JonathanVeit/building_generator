import maya.cmds as mc
from Object import *
import json


# An Element represents an object in the scene by its name
# Elements provide certain methods to modify the object
class Element(Object):

    # static definitions
    __META_KEY = 'metaData'

    def __init__(self, object="new_mesh"):
       # if not mc.objExists(mesh):
           # mc.warning("Mesh \"" + mesh + "\" does not exist, created element is invalid.")

        self._object = object

    # scene mesh
    def select(self):
        if self._object is None:
            mc.error("Element has been destroyed, it cannot be selected.")
            return

        mc.select(self._object)

    def get_object(self):
        if self._object is None:
            mc.error("Element has been destroyed, it has no mesh.")
            return None

        return self._object

    def get_parent(self):
        if self._object is None:
            mc.error("Element has been destroyed, there is no parent.")
            return None

        parents = mc.listRelatives(self._object, parent=True)
        if parents is None:
            return None

        return parents[0]

    def set_parent(self, parent="parent_object"):
        if self._object is None:
            mc.error("Element has been destroyed, cannot set parent.")
            return

        # already parented
        if self.get_parent() == parent:
            return

        # None -> unparent
        if parent is None:
            mc.parent(self._object, world=True)
            return

        mc.parent(self._object, parent)

    def get_position(self):
        if self._object is None:
            mc.error("Element has been destroyed, there is no position.")
            return None

        pos = mc.getAttr(self._object + '.translate')[0]
        return pos

    def set_position(self, position=(0, 0, 0)):
        if self._object is None:
            mc.error("Element has been destroyed, cannot set position.")
            return

        mc.setAttr(self._object + '.translate', position[0], position[1], position[2])

    def move_position(self, direction=(0, 0, 0)):
        if self._object is None:
            mc.error("Element has been destroyed, cannot set position.")
            return

        pos = self.get_position()
        mc.setAttr(self._object + '.translate', pos[0] + direction[0],  pos[1] + direction[1],  pos[2] + direction[2])

    def get_rotation(self):
        if self._object is None:
            mc.error("Element has been destroyed, there is no rotation")
            return None

        rot = mc.getAttr(self._object + '.rotate')[0]
        return rot

    def set_rotation(self, rotation=(0, 0, 0)):
        if self._object is None:
            mc.error("Element has been destroyed, cannot set rotation.")
            return

        rot = mc.setAttr(self._object + '.rotate', rotation[0], rotation[1], rotation[2])
        return rot

    def rotate(self, rotation=(0, 0, 0)):
        cur_rot = self.get_rotation()
        self.set_rotation((cur_rot[0] + rotation[0], cur_rot[1] + rotation[1], cur_rot[2] + rotation[2]))

    def destroy(self):
        if self._object is None:
            mc.error("Element has already been destroyed")
            return None

        mc.delete(self._object)
        self._object = None

    def exists(self):
        return mc.objExists(self._object)

    @staticmethod
    def does_exist(element="new_element"):
        return mc.objExists(element)

    # meta data
    @staticmethod
    def get_meta_data_key():
        return Element.__META_KEY

    def write_metadata(self, data_dict={}):
        # already destroyed?
        if self._object is None:
            mc.error("Element has been destroyed, cannot write meta data.")
            return

        # replace ' with "
        data_string = str(data_dict)
        data_string = data_string.replace("'", '"')

        # does it exist?
        if mc.objExists(self._object):

            # add meta data if not existing
            if not mc.attributeQuery(self.__META_KEY, node=self._object, exists=True):
                mc.addAttr(self._object, longName=self.__META_KEY, dataType='string')

            # write meta data
            mc.setAttr(self._object + '.' + self.__META_KEY, data_string, type='string')
        else:
            mc.warning('Can not find object: ' + self._object)

    def read_metadata(self):
        # already destroyed?
        if self._object is None:
            mc.error("Element has been destroyed, cannot read meta data.")
            return None

        # data to load
        meta_data = None

        # does it exist?
        if mc.objExists(self._object):

            # load meta data
            if mc.attributeQuery(self.__META_KEY, node=self._object, exists=True):

                # convert to json
                attr_value = mc.getAttr(self._object + '.' + self.__META_KEY)
                meta_data = json.loads(attr_value)
            else:
                mc.warning("Can not find meta data attribute on object: " + self._object)
        else:
            mc.warning("Can not find object: " + self._object)

        return meta_data