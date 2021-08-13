from Blueprints import *
from GlobalDefinitions import *


# a Roof is a collection of Tile and Corners
class Roof (Element):
    def __init__(self, object="new_roof", template_id="new_roof_template", seed=None):
        Element.__init__(self, object)

        self._tiles = {}
        self._corners = {}
        self._edges = {}
        self._template_id = template_id
        self._seed = seed

    def get_template_id(self):
        return self._template_id

    def get_seed(self):
        return self._seed

    # tiles
    def add_tile(self, tile=Tile()):
        tile_pos_x = tile.get_tile_position()[0]
        tile_pos_y = tile.get_tile_position()[1]

        # add x entry if it does not exist
        if not self._tiles.has_key(tile_pos_x):
            self._tiles[tile_pos_x] = {}

        self._tiles[tile_pos_x][tile_pos_y] = tile

    def get_tile(self, tile_position=(0, 0)):
        tile_pos_x = tile_position[0]
        tile_pos_y = tile_position[1]

        # no tile at position?
        if not self._tiles.has_key(tile_pos_x) or not self._tiles[tile_pos_x].has_key(tile_pos_y) :
            mc.error("Roof has no tile at position " + str(tile_position))
            return

        return self._tiles[tile_pos_x][tile_pos_y]

    def remove_tile(self, tile=Tile()):
        tile_pos_x = tile.get_tile_position()[0]
        tile_pos_y = tile.get_tile_position()[1]

        self._tiles[tile_pos_x].pop(tile_pos_y)

    # edges
    def add_edge(self, edge=Edge()):
        # add entry if it does not exist
        if not self._edges.has_key(edge.get_side()):
            self._edges[edge.get_side()] = []

        self._edges[edge.get_side()].append(edge)

    def get_edges(self, side=kFront):
        return self._edges[side]

    def remove_edge(self, edge=Edge()):
        self._edges[edge.get_side()].pop(edge)

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
            "tiles": self.__get_tiles_serializable(),
            "corners": self.__get_corners_serializable(),
            "template_id": self._template_id,
            "seed": self._seed
        }
        return result

    def __get_tiles_serializable(self):
        result = []
        for x in self._tiles.keys():
            for y in self._tiles[x ]:
                result.append(self._tiles[x][y].get_serializable())

        return result

    def __get_corners_serializable(self):
        result = {}
        for side in self._corners.keys():
            result[side] = self._corners[side].get_serializable()

        return result

    @staticmethod
    def get_from_serializable(serializable={}):
        roof = Roof(serializable["object"], serializable["template_id"], int(serializable["seed"]))

        # add tiles
        for tile in serializable["tiles"]:
            roof.add_tile(Tile.get_from_serializable(tile))

        # add corners
        for side in serializable["corners"]:
            roof.add_corner(Corner.get_from_serializable(serializable["corners"][side]))

        return roof