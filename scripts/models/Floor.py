from Blueprints import *
from GlobalDefinitions import *


# a Floor is a collection of Walls and Corners on a certain level
class Floor (Element):

    def __init__(self, object="new_floor", level=0, template_id="new_floor_template", seed=None):
        Element.__init__(self, object)

        self._level = level
        self._walls = {}
        self._corners = {}
        self._template_id = template_id
        self._seed = seed

    def get_template_id(self):
        return self._template_id

    def get_level(self):
        return self._level

    def set_level(self, level=0):
        self._level = level

    def get_seed(self):
        return self._seed

    # walls
    def add_wall(self, wall=Wall()):
        # add entry if it does not exist
        if not self._walls.has_key(wall.get_side()):
            self._walls[wall.get_side()] = []

        self._walls[wall.get_side()].append(wall)

    def get_walls(self, side=kFront):
        return self._walls[side]

    def remove_wall(self, wall=Wall()):
        self._walls[wall.get_side()].pop(wall)

    # corners
    def add_corner(self,corner=Corner()):
        self._corners[corner.get_side()] = corner

    def get_corner(self, side=kFront):
        return self._corners[side]

    def remove_corner(self, corner=Wall()):
        self._corners.pop(corner.get_side())

    # serialization
    def get_serializable(self):
        result = {
            "object" : self._object,
            "level": self._level,
            "walls": self.__get_walls_serializable(),
            "corners": self.__get_corners_serializable(),
            "template_id": self._template_id,
            "seed": self._seed
        }
        return result

    def __get_walls_serializable(self):
        result = {}
        for side in self._walls.keys():
            s_walls = []
            for wall in self._walls[side]:
                s_walls.append(wall.get_serializable())

            result[side] = s_walls

        return result

    def __get_corners_serializable(self):
        result = {}
        for side in self._corners.keys():
            result[side] = self._corners[side].get_serializable()

        return result

    @staticmethod
    def get_from_serializable(serializable={}):
        floor = Floor(serializable["object"],
                      int(serializable["level"]),
                      serializable["template_id"],
                      int(serializable["seed"]))

        # add walls
        for side in serializable["walls"]:
            for s_wall in serializable["walls"][side]:
                floor.add_wall(Wall.get_from_serializable(s_wall))

        # add corners
        for side in serializable["corners"]:
            floor.add_corner(Corner.get_from_serializable(serializable["corners"][side]))

        return floor