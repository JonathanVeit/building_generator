from Floor import *
from Roof import *


# A Building represents a collection of floors and a roof
class Building(Element):
    def __init__(self, object="new_building", template_id="new_building_template"):
        Element.__init__(self, object)
        self._floors = {}
        self._roof = None
        self._template_id = template_id

    def get_template_id(self):
        return self._template_id

    # floors
    def add_floor(self, floor=Floor()):
        self._floors[floor.get_level()] = floor

    def get_floor_at_level(self, level=0):
        if not self._floors.__contains__(level):
            mc.error("Building {} has no floor at level {}.".format(self._object, level))
            return None

        return self._floors.__getitem__(level)

    def get_floor_count(self):
        return len(self._floors)

    def has_floor_at(self, level=0):
        return self._floors.__contains__(level)

    def remove_floor(self, level=0):
        self._floors.pop(level)

    # roof
    def set_roof(self, roof=Roof()):
        self._roof = roof

    def get_roof(self):
        return self._roof

    def remove_roof(self):
        self._roof = None

    # helper

    # serialization
    def get_serializable(self):
        result = {
            "object": self.get_object(),
            "floors": self.__get_floors_serializable(),
            "roof"  : self._roof.get_serializable(),
            "template_id": self._template_id,
        }

        return result

    def __get_floors_serializable(self):
        result = {}
        for level in self._floors:
            result[level] = self._floors[level].get_serializable()

        return result

    @staticmethod
    def get_from_serializable(serializable={}):
        result = Building(serializable["object"], serializable["template_id"])

        # load floors
        for level in serializable["floors"]:
            floor = Floor.get_from_serializable(serializable["floors"][level])
            result.add_floor(floor)

        # load roof
        result.set_roof(Roof.get_from_serializable(serializable["roof"]))

        return result
