from Object import Object
import maya.cmds as mc


# Base class for all templates
class BaseTemplate(Object):
    def __init__(self, id="new_template", unit=(4, 4, 4), width=3, depth=3):
        self.id = id
        self.unit = unit
        self.width = width
        self.depth = depth


# template to generate a roof
class RoofTemplate(BaseTemplate):
    def __init__(self, id="new_roof_template", unit=(4, 4, 4), width=3, depth=3, tiles=["roof_tile_01"], edges=["roof_edge_01"], corners=["roof_corner_01"]):
        BaseTemplate.__init__(self, id, unit, width, depth)
        self.tiles = tiles
        self.edges = edges
        self.corners = corners

    # serialization
    def get_serializable(self):
        return {
            "id": self.id,
            "unit": self.unit,
            "width": self.width,
            "depth": self.depth,
            "tiles": self.tiles,
            "edges": self.edges,
            "corners": self.corners
        }

    @staticmethod
    def get_from_serializable(serializable={}):
        return RoofTemplate(serializable["id"], serializable["unit"], serializable["width"], serializable["depth"],
                            serializable["tiles"], serializable["edges"], serializable["corners"])


# template to generate a floor
class FloorTemplate(BaseTemplate):
    def __init__(self, id="new_floor_template", unit=(4, 4, 4), width=3, depth=3, walls=["floor_wall_01"], corners=["floor_corner_01"]):
        BaseTemplate.__init__(self, id, unit, width, depth)
        self.walls = walls
        self.corners = corners

    # serialization
    def get_serializable(self):
        return {
            "id": self.id,
            "unit": self.unit,
            "width": self.width,
            "depth": self.depth,
            "walls": self.walls,
            "corners": self.corners
        }

    @staticmethod
    def get_from_serializable(serializable={}):
        return FloorTemplate(serializable["id"], serializable["unit"], serializable["width"], serializable["depth"],
                             serializable["walls"], serializable["corners"])


# Collection of roof and floor templates
class BuildingTemplate(Object):

    def __init__(self, id="new_building_template", floor_templates=[], roof_templates=[]):
        self.id = id
        self.floor_templates = floor_templates
        self.roof_templates = roof_templates

    # floor templates
    def add_floor_template(self, template=FloorTemplate()):
        self.floor_templates.append(template)

    def get_floor_template(self, id="new_floor_template"):
        for template in self.floor_templates:
            if template.id == id:
                return template
        return None

    def get_all_floor_templates(self):
        return self.floor_templates

    # roof templates
    def add_roof_templates(self, template=RoofTemplate()):
        self.roof_templates.append(template)

    def get_roof_template(self, name="new_roof_template"):
        for template in self.roof_templates:
            if template.id == name:
                return template
        return None

    def get_all_roof_templates(self):
        return self.roof_templates

    # general
    def add_template(self, template=BaseTemplate()):
        if isinstance(template, FloorTemplate):
            self.floor_templates.append(template)
        elif isinstance(template, RoofTemplate):
            self.roof_templates.append(template)

    def get_template_by_id(self, id="my_template"):
        template = self.get_roof_template(id)
        if template is None:
            template = self.get_floor_template(id)

        return template

    def remove_template_by_id (self, id="my_template"):
        template = self.get_template_by_id(id)

        if isinstance(template, FloorTemplate):
            self.floor_templates.remove(template)
        elif isinstance(template, RoofTemplate):
            self.roof_templates.remove(template)

    # is the template valid? -> are all objects in the scene?
    # 1 = is valid
    # 2 = no floor templates
    # 3 = no roof templates
    # 4 = has invalid floor blueprints
    # 5 = has invalid roof blueprints
    def is_valid(self):
        # no templates?
        if len(self.floor_templates) == 0:
            return 2

        if len(self.roof_templates) == 0:
            return 3

        # no blueprints?
        floor_blueprints_valid = False
        for floor_template in self.floor_templates:
            if len(floor_template.walls) > 0 and len(floor_template.corners) > 0:
                floor_blueprints_valid = True
                break

        if not floor_blueprints_valid:
            return 4

        roof_blueprints_valid = False
        for roof_template in self.roof_templates:
            if len(roof_template.tiles) > 0 and len(roof_template.edges) > 0 and len(roof_template.corners) > 0:
                roof_blueprints_valid = True
                break

        if not roof_blueprints_valid:
            return 5

        return 1

    # only return valid templates
    def get_valid_floor_templates(self, id_only=False):
        result = []

        for floor_template in self.floor_templates:
            # no blueprints?
            if len(floor_template.walls) == 0 or len(floor_template.corners) == 0:
                continue

            # validate blueprints
            blueprints_valid = True

            # walls valid?
            for wall in floor_template.walls:
                if not mc.objExists(wall):
                    blueprints_valid = False
                    break

            # corners valid?
            for corner in floor_template.corners:
                if not mc.objExists(corner):
                    blueprints_valid = False
                    break

            # blueprints not valid?
            if not blueprints_valid:
                continue

            # add to result
            if id_only:
                result.append(floor_template.id)
            else:
                result.append(floor_template)

        return result

    def get_valid_roof_templates(self, id_only=False):
        result = []

        for roof_template in self.roof_templates:
            # no blueprints?
            if len(roof_template.tiles) == 0 or len(roof_template.edges) == 0 or len(roof_template.corners) == 0:
                continue

            # validate blueprints
            blueprints_valid = True

            # tiles valid?
            for tile in roof_template.tiles:
                if not mc.objExists(tile):
                    blueprints_valid = False
                    break

            # corners valid?
            for edge in roof_template.edges:
                if not mc.objExists(edge):
                    blueprints_valid = False
                    break

            # corners valid?
            for corner in roof_template.corners:
                if not mc.objExists(corner):
                    blueprints_valid = False
                    break

            # blueprints not valid?
            if not blueprints_valid:
                continue

            # add to result
            if id_only:
                result.append(roof_template.id)
            else:
                result.append(roof_template)

        return result

    # serialization
    def get_serializable(self):
        return {
            "id": self.id,
            "floor_templates": self.__get_floor_templates_serializable(),
            "roof_templates": self.__get_roof_templates_serializable(),
        }

    def __get_floor_templates_serializable(self):
        result = []
        for template in self.floor_templates:
            result.append(template.get_serializable())
        return result

    def __get_roof_templates_serializable(self):
        result = []
        for template in self.roof_templates:
            result.append(template.get_serializable())

        return result

    @staticmethod
    def get_from_serializable(serializable={}):
        building_template = BuildingTemplate(serializable["id"], [], [])

        # load floor templates
        for serializable_floor_template in serializable["floor_templates"]:
            floor_template = FloorTemplate.get_from_serializable(serializable_floor_template)
            building_template.add_floor_template(floor_template)

        # load roof templates
        for serializable_roof_template in serializable["roof_templates"]:
            roof_template = RoofTemplate.get_from_serializable(serializable_roof_template)
            building_template.add_roof_templates(roof_template)

        return building_template