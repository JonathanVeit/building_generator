from Element import *
from GlobalDefinitions import *


# a Wall represents an Element on the side of a building (except for the corner)
class Wall (Element):
    def __init__(self, object="new_wall", side=kFront):
        Element.__init__(self, object)
        self._side = side

    def get_side(self):
        return self._side

    # serialization
    def get_serializable(self):
        return {
            "object": self._object,
            "side": self._side,
        }

    @staticmethod
    def get_from_serializable(serializable={}):
        return Wall(serializable["object"], serializable["side"])


# a Corner represents an Element on the side of a floor or roof
class Corner (Element):
    def __init__(self, object="new_corner", side=kFront):
        Element.__init__(self, object)
        self._side = side

    def get_side(self):
        return self._side

    # serialization
    def get_serializable(self):
        return {
            "object": self._object,
            "side": self._side,
        }

    @staticmethod
    def get_from_serializable(serializable={}):
        return Corner(serializable["object"], serializable["side"])


# a Tile represents an Element on the middle of the roof (except for the corner and edges)
class Tile (Element):
    def __init__(self, object="new_tile", tile_position=(0, 0)):
        Element.__init__(self, object)
        self._tile_postion = tile_position

    def get_tile_position(self):
        return self._tile_postion

    # serialization
    def get_serializable(self):
        return {
            "object": self._object,
            "tile_position": self._tile_postion,
        }

    @staticmethod
    def get_from_serializable(serializable={}):
        return Tile(serializable["object"], serializable["tile_position"])


# an Edge represents an Element on the edge of a roof between two corners
class Edge (Element):
    def __init__(self, object="new_wall", side=kFront):
        Element.__init__(self, object)
        self._side = side

    def get_side(self):
        return self._side

    # serialization
    def get_serializable(self):
        return {
            "object": self._object,
            "side": self._side,
        }

    @staticmethod
    def get_from_serializable(serializable={}):
        return Edge(serializable["object"], serializable["side"])
