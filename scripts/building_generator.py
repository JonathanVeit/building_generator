import random
import sys
import uuid
from models.Building import *
from models.Templates import *


# Generator class for creating Buildings
class BuildingGenerator:

    # region Building
    def building_exists(self, building_id="new_building"):
        return mc.objExists(building_root_format.format(building_id))

    def destroy_building(self, building_id="building_name"):
        if self.building_exists(building_id):
            mc.delete(building_root_format.format(building_id))

    def create_empty_building(self, building_id="building_name", template=BuildingTemplate()):
        # destroy the building if it already exists
        self.destroy_building(building_id)

        # create building with root
        building_root = mc.createNode('transform', name=building_root_format.format(building_id))
        building = Building(building_root, template.id)

        # return the new building
        return building
    # endregion

    #region Create Floors
    def create_floor(self, building=Building(), building_template=BuildingTemplate(), floor_template=FloorTemplate(), level=0, seed=None):
        # remove existing floor
        if building.has_floor_at(level):
            existing_floor = building.get_floor_at_level(level)

            floor_template_id = existing_floor.get_template_id()
            offset_y = building_template.get_floor_template(floor_template_id).unit[1]

            building.remove_floor(level)
            existing_floor.destroy()

            direction = (0, floor_template.unit[1] - offset_y, 0)
            self._move_floors_in_range(building, level + 1, building.get_floor_count(), direction, 0)
            building.get_roof().move_position(direction)

        # adjust roof if exists
        elif building.get_roof() is not None:
            building.get_roof().move_position((0, floor_template.unit[1], 0))

        # set seed
        if seed is None:
            seed = random.randint(0, sys.maxint)
        random.seed(seed)

        # create floor with root
        floor_root = self._get_floor_root(building, building_template, level)
        new_floor = Floor(floor_root, level, floor_template.id, seed)

        # walls and corners
        self._crate_floor_walls(building, building_template, new_floor, floor_template)
        self._create_floor_corners(building, building_template, new_floor, floor_template)

        # add floor to building
        building.add_floor(new_floor)

    def _crate_floor_walls(self, building=Building(), building_template=BuildingTemplate(), floor=Floor(), floor_template=FloorTemplate()):
        for side in [kFront, kBack, kLeft, kRight]:
            self._create_floor_walls_for_side(side, building, building_template, floor, floor_template)

    def _create_floor_walls_for_side(self, side, building=Building(), building_template=BuildingTemplate(), floor=Floor(), floor_template=FloorTemplate()):
        # level of the floor to create
        level = floor.get_level()

        # calculate origin parameters
        start_x = floor_template.width * 0.5 * floor_template.unit[0] - self._get_offset(floor_template.unit[0])
        start_z = floor_template.depth * 0.5 * floor_template.unit[2] - self._get_offset(floor_template.unit[2])
        length = self._get_length_of_side(floor_template, side)

        # create floor walls
        for i in range(length):
            # skip corners
            if floor_template.corners:
                if i == 0 or i == length - 1:
                    continue

            # choose random wall
            wall_index = random.randint(0, len(floor_template.walls) - 1)

            # create mesh and rename
            wall_object = mc.duplicate(floor_template.walls[wall_index], ilf=True)[0]
            wall_object = mc.rename(wall_object, floor_wall_format.format(building.get_object(), str(level), side_names[side], i))

            # new wall element
            new_wall = Wall(wall_object, side)

            # set position and rotation
            wall_position = [0, self._get_level_height(building, building_template, floor.get_level()) + self._get_offset(floor_template.unit[1]), 0]
            wall_rotation = [0, self._get_y_angle_of_side(side), 0]

            if side == kFront:
                wall_position[0] = start_x - i * floor_template.unit[0]
                wall_position[2] = floor_template.depth * self._get_offset(floor_template.unit[2])
            if side == kBack:
                wall_position[0] = start_x - i * floor_template.unit[0]
                wall_position[2] = -floor_template.depth * self._get_offset(floor_template.unit[2])
            if side == kLeft:
                wall_position[0] = floor_template.width * self._get_offset(floor_template.unit[0])
                wall_position[2] = start_z - i * floor_template.unit[2]
            if side == kRight:
                wall_position[0] = -floor_template.width * self._get_offset(floor_template.unit[0])
                wall_position[2] = start_z - i * floor_template.unit[2]

            # add building offset
            wall_position[0] += building.get_position()[0]
            wall_position[1] += building.get_position()[1]
            wall_position[2] += building.get_position()[2]

            new_wall.set_position(tuple(wall_position))
            new_wall.set_rotation(tuple(wall_rotation))

            # parent wall to floor root
            new_wall.set_parent(self._get_floor_wall_root(floor, side))

            # add wall to its floor
            floor.add_wall(new_wall)

    def _create_floor_corners(self, building=Building(), building_template=BuildingTemplate(), floor=Floor(), floor_template=FloorTemplate()):
        # level of the floor
        level = floor.get_level()

        # create corners
        for i in range(4):
            # choose corner for individual side
            corner_index = i
            if corner_index > len(floor_template.corners) - 1:
                corner_index = len(floor_template.corners) - 1

            # create corner object
            corner_object = mc.duplicate(floor_template.corners[corner_index])[0]
            corner_object = mc.rename(corner_object, floor_corner_format.format(building.get_object(), str(level), side_names[i]))

            # create corner
            new_corner = Corner(corner_object, i)

            # get parameters for face direction
            face_width = self._get_corner_face_width(i)
            face_depth = self._get_corner_face_depth(i)

            # set position and rotation of the corner
            corner_position = [floor_template.width * self._get_offset(floor_template.unit[0]) * face_width,
                               self._get_level_height(building, building_template, floor.get_level()) + self._get_offset(floor_template.unit[1]),
                               floor_template.depth * self._get_offset(floor_template.unit[2]) * face_depth]
            corner_rotation = [0,
                               self._get_y_angle_of_side(i),
                               0]

            # add building offset
            corner_position[0] += building.get_position()[0]
            corner_position[1] += building.get_position()[1]
            corner_position[2] += building.get_position()[2]

            new_corner.set_position(tuple(corner_position))
            new_corner.set_rotation(tuple(corner_rotation))

            # parent corner to the root
            new_corner.set_parent(self._get_floor_corner_root(floor))

            # add corner to the floor
            floor.add_corner(new_corner)
    #endregion

    # region Create Roof
    def create_roof(self, building=Building(), building_template=BuildingTemplate(), roof_template=RoofTemplate(), seed=None):
        # destroy roof if exist
        if building.get_roof() is not None:
            building.get_roof().destroy()
            building.remove_roof()

        # set seed
        if seed is None:
            seed = random.randint(0, sys.maxint)
        random.seed(seed)

        # create roof with root
        roof_root = self._get_roof_root(building, building_template)
        new_roof = Roof(roof_root, roof_template.id, seed)

        # create roof parts
        self._create_roof_tiles(building, building_template, new_roof, roof_template)
        self._create_roof_edges(building, building_template, new_roof, roof_template)
        self._create_roof_corners(building, building_template, new_roof, roof_template)

        # add roof to building
        building.set_roof(new_roof)

    def _create_roof_tiles(self, building=Building(), building_template=BuildingTemplate(), roof=Roof(), roof_template=RoofTemplate()):
        # calculate start paremeters
        start_x = roof_template.width * 0.5 * roof_template.unit[0] - self._get_offset(roof_template.unit[0])
        start_z = roof_template.depth * 0.5 * roof_template.unit[2] - self._get_offset(roof_template.unit[2])

        # create tiles
        for x in range(roof_template.width):
            for y in range(roof_template.depth):
                # skip corners
                if self._position_is_cornder_or_edge(roof_template, x, y):
                    continue

                # get random tile
                tile_index = random.randint(0, len(roof_template.tiles) - 1)

                # create tile object
                tile_object = mc.duplicate(roof_template.tiles[tile_index], ilf=True)[0]
                tile_object = mc.rename(tile_object, roof_tile_format.format(building.get_object(), str(x), str(y)))

                # create tile
                new_tile = Tile(tile_object, (x, y))

                # calculate position
                tile_position = [start_x - x * roof_template.unit[0],
                                 self._get_level_height(building, building_template, building.get_floor_count()),
                                 start_z - y * roof_template.unit[2]]

                # add building offset
                tile_position[0] += building.get_position()[0]
                tile_position[1] += building.get_position()[1]
                tile_position[2] += building.get_position()[2]

                # set position of the tile
                new_tile.set_position(tuple(tile_position))

                # parent tile to root
                new_tile.set_parent(self._get_roof_tile_root(roof))

                # add tile to roof
                roof.add_tile(new_tile)

    def _create_roof_edges(self, building=Building(), building_template=BuildingTemplate(), roof=Roof(), roof_template=RoofTemplate()):
        for side in [kFront, kBack, kLeft, kRight]:
            self._create_roof_edges_for_side(side, building, building_template, roof, roof_template)

    def _create_roof_edges_for_side(self, side, building=Building(), building_template=BuildingTemplate(), roof=Roof(), roof_template=RoofTemplate()):
        # calculate start parameters
        start_x = roof_template.width * 0.5 * roof_template.unit[0] - self._get_offset(roof_template.unit[0])
        start_z = roof_template.depth * 0.5 * roof_template.unit[2] - self._get_offset(roof_template.unit[2])
        length = self._get_length_of_side(roof_template, side)

        for i in range(length):
            # skip corners
            if roof_template.corners:
                if i == 0 or i == length - 1:
                    continue

            # choose random edge
            edge_index = random.randint(0, len(roof_template.edges) - 1)

            # create mesh and rename
            edge_object = mc.duplicate(roof_template.edges[edge_index], ilf=True)[0]
            edge_object = mc.rename(edge_object,
                                    roof_edge_format.format(building.get_object(), side, str(i)))

            # new edge
            new_edge = Edge(edge_object, side)

            # set position and rotation
            edge_position = [0,
                             self._get_level_height(building, building_template, building.get_floor_count()),
                             0]
            edge_rotation = [0,
                             self._get_y_angle_of_side(side),
                             0]

            if side == kFront:
                edge_position[0] = start_x - i * roof_template.unit[0]
                edge_position[2] = (roof_template.depth * self._get_offset(roof_template.unit[2])) - self._get_offset(roof_template.unit[2])
            if side == kBack:
                edge_position[0] = start_x - i * roof_template.unit[0]
                edge_position[2] = (-roof_template.depth * self._get_offset(roof_template.unit[2])) + self._get_offset(roof_template.unit[2])
            if side == kLeft:
                edge_position[0] = (roof_template.width * self._get_offset(roof_template.unit[0])) - self._get_offset(roof_template.unit[0])
                edge_position[2] = start_z - i * roof_template.unit[2]
            if side == kRight:
                edge_position[0] = (-roof_template.width * self._get_offset(roof_template.unit[0])) + self._get_offset(roof_template.unit[0])
                edge_position[2] = start_z - i * roof_template.unit[2]

            # add building offset
            edge_position[0] += building.get_position()[0]
            edge_position[1] += building.get_position()[1]
            edge_position[2] += building.get_position()[2]

            new_edge.set_position(tuple(edge_position))
            new_edge.set_rotation(tuple(edge_rotation))

            # parent edge to root
            new_edge.set_parent(self._get_roof_edge_root(roof, side))

            # add edge to roof
            roof.add_edge(new_edge)

    def _create_roof_corners(self, building=Building(), building_template=BuildingTemplate(), roof=Roof(), roof_template=RoofTemplate()):
        for i in range(4):
            # choose corner for individual side
            corner_index = i
            if corner_index > len(roof_template.corners) - 1:
                corner_index = len(roof_template.corners) - 1

            # create corner object
            corner_object = mc.duplicate(roof_template.corners[corner_index], ilf=True)[0]
            corner_object = mc.rename(corner_object,
                                      roof_corner_format.format(building.get_object(), side_names[i]))

            # create corner
            new_corner = Corner(corner_object, i)

            # get parameters for face direction
            face_width = self._get_corner_face_width(i)
            face_depth = self._get_corner_face_depth(i)

            offset_width = self._get_offset(roof_template.unit[0]) * face_width
            offset_depth = self._get_offset(roof_template.unit[2]) * face_depth

            # set position and rotation of the corner
            corner_position = [(roof_template.width * offset_width) - offset_width,
                               self._get_level_height(building, building_template, building.get_floor_count()),
                               (roof_template.depth * offset_depth) - offset_depth]
            corner_rotation = [0,
                               self._get_y_angle_of_side(i),
                               0]

            # add building offset
            corner_position[0] += building.get_position()[0]
            corner_position[1] += building.get_position()[1]
            corner_position[2] += building.get_position()[2]

            new_corner.set_position(tuple(corner_position))
            new_corner.set_rotation(tuple(corner_rotation))

            # parent corner to root
            new_corner.set_parent(self._get_roof_corner_root(roof))

            # add corner to roof
            roof.add_corner(new_corner)
    # endregion

    # region Floor Modifications
    def swap_floors(self, building=Building(), building_template=BuildingTemplate(), level_1=0, level_2=1):
        # get floors
        floor_1 = building.get_floor_at_level(level_1)
        floor_2 = building.get_floor_at_level(level_2)

        # switch floor levels
        floor_1.set_level(level_2)
        floor_2.set_level(level_1)

        # remove floors
        building.add_floor(floor_1)
        building.add_floor(floor_2)

        # swap positions
        building.get_floor_at_level(level_1).set_position((0, self._get_level_height(building, building_template, level_1), 0))
        building.get_floor_at_level(level_2).set_position((0, self._get_level_height(building, building_template, level_2), 0))

        # adjust floors in between
        if len(range(level_1, level_2)) > 1:
            template_1 = building_template.get_floor_template(floor_1.get_template_id())
            template_2 = building_template.get_floor_template(floor_2.get_template_id())

            direction = (0, template_2.unit[1] - template_1.unit[1], 0)
            self._move_floors_in_range(building, level_1 + 1, level_2 - 1, direction, 0)

    def destroy_floor(self, building=Building(), building_template=BuildingTemplate(), level=0):
        # get floor to destroy
        floor_to_destroy = building.get_floor_at_level(level)

        # get the offset y of the floor
        floor_template_id = floor_to_destroy.get_template_id()
        offset_y = building_template.get_floor_template(floor_template_id).unit[1]

        # remove and destroy the floor
        building.remove_floor(level)
        floor_to_destroy.destroy()

        # adjust all following floors
        self._move_floors_in_range(building, level+1, building.get_floor_count(), (0, -offset_y, 0))

        # adjust roof
        building.get_roof().move_position((0, -offset_y, 0))

    def insert_floor(self, building=Building(), building_template=BuildingTemplate(), floor_template=FloorTemplate(), level=0):
        # offset of new floor
        offset_y = floor_template.unit[1]

        # move floors up
        if level <= building.get_floor_count() - 1:
            self._move_floors_in_range(building, level, building.get_floor_count() - 1, (0, offset_y, 0), 1)

        # create new floor
        self.create_floor(building, building_template, floor_template, level)

    def _move_floors_in_range(self, building=Building(), start_level=0, end_level=1, direction=(0, 0, 0), adjust_level=2):
        # move floors
        for cur_level in range(start_level, end_level + 1):
            # get the current floor
            cur_floor = building.get_floor_at_level(cur_level)

            # move the floor by the previews offset
            cur_floor.move_position(direction)

        # no level adjustment
        if adjust_level == 0:
            return

        # adjust level up
        if adjust_level == 1:
            for cur_level in reversed(range(start_level, end_level + 1)):
                # get the current floor
                cur_floor = building.get_floor_at_level(cur_level)

                # change floor level
                cur_floor.set_level(cur_level + 1)

                # remove floor from current level
                building.remove_floor(cur_level)

                # add floor again
                building.add_floor(cur_floor)

        # adjust level down
        elif adjust_level == 2:
            for cur_level in range(start_level, end_level + 1):
                # get the current floor
                cur_floor = building.get_floor_at_level(cur_level)

                # change floor level
                cur_floor.set_level(cur_level - 1)

                # remove floor from current level
                building.remove_floor(cur_level)

                # add floor again
                building.add_floor(cur_floor)
    # endregion

    # region Helper
    def _get_offset(self, unit=1):
        return unit * 0.5

    def _remove_duplicates(self, template=BuildingTemplate()):
        if mc.objExists(building_root_format.format(template.id)):
            mc.delete(building_root_format.format(template.id))

    def _get_y_angle_of_side(self, side=kFront):
        if side == kFront:
            return 0
        if side == kBack:
            return 180
        if side == kLeft:
            return 90
        if side == kRight:
            return -90

    def _get_length_of_side(self, template=BaseTemplate(), side=kFront):
        if side == kLeft or side == kRight:
            return template.depth
        else:
            return template.width

    def _get_corner_face_width(self, corner_index=0):
        if corner_index == 1 or corner_index == 3:
            return -1
        return 1

    def _get_corner_face_depth(self, corner_index=0):
        if corner_index == 2 or corner_index == 1:
            return -1
        return 1

    def _position_is_cornder_or_edge(self, template=BaseTemplate(), position_x=0, position_y=0):
        if position_x == 0 or position_y == 0 or position_x == template.width - 1 or position_y == template.depth - 1:
            return True

        return False

    def _get_level_height(self, building=Building(), building_template=BuildingTemplate(), level=0):
        height = 0

        for i in range(level):
            floor = building.get_floor_at_level(i)
            template_id = floor.get_template_id()
            floor_template = building_template.get_floor_template(template_id)
            height += floor_template.unit[1]

        return height
    # endregion

    # region Formatting
    def _get_floors_root(self, building=Building()):
        root = floors_root_format.format(building.get_object())
        if not mc.objExists(root):
            mc.createNode('transform', name=root)
            mc.parent(root, building.get_object())

        return root

    def _get_floor_root(self, building=Building(), building_template=BuildingTemplate(), level=0):
        root = floor_format.format(building.get_object(), str(uuid.uuid4()).replace("-", "_"))
        if not mc.objExists(root):
            mc.createNode('transform', name=root)
            mc.parent(root, self._get_floors_root(building))

            pos = self._get_level_height(building, building_template, level)
            mc.setAttr(root + '.translate', 0, pos, 0)

        return root

    def _get_floor_wall_root(self, floor=Floor(), side=kFront):
        root = floor_walls_root_format.format(floor.get_object(), side_names[side])
        if not mc.objExists(root):
            mc.createNode('transform', name=root)
            mc.parent(root, floor.get_object())

        return root

    def _get_floor_corner_root(self, floor=Floor()):
        root = floor_corner_root_format.format(floor.get_object())
        if not mc.objExists(root):
            mc.createNode('transform', name=root)
            mc.parent(root, floor.get_object())

        return root

    def _get_roof_root(self, building=Building(), building_template=BuildingTemplate()):
        root = roof_root_format.format(building.get_object())
        if not mc.objExists(root):
            mc.createNode('transform', name=root)
            mc.parent(root, building.get_object())

            pos = self._get_level_height(building, building_template, building.get_floor_count())
            mc.setAttr(root + '.translate', 0, pos, 0)

        return root

    def _get_roof_tile_root(self, roof=Roof()):
        root = roof_tiles_root_format.format(roof.get_object())
        if not mc.objExists(root):
            mc.createNode('transform', name=root)
            mc.parent(root, roof.get_object())

        return root

    def _get_roof_corner_root(self, roof=Roof(), side=kFront):
        root = roof_corners_root_format.format(roof.get_object(), side_names[side])
        if not mc.objExists(root):
            mc.createNode('transform', name=root)
            mc.parent(root, roof.get_object())

        return root

    def _get_roof_edge_root(self, roof=Roof(), side=kFront):
        root = roof_edges_root_format.format(roof.get_object(), side_names[side])
        if not mc.objExists(root):
            mc.createNode('transform', name=root)
            mc.parent(root, roof.get_object())

        return root
    # endregion





