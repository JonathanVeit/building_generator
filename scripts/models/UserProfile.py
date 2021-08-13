import json
from Templates import *


# user profile with information about the current user
# Can be saved and loaded from the maya prefs (using option vars)
class UserProfile():

    __option_var_key = "bg_profile"

    def __init__(self):
        self._templates = {}
        self._cur_template = None
        self._cur_building = None

    # templates
    def add_template(self, template=BuildingTemplate()):
        self._templates[template.id] = template

    def remove_template(self, template=BuildingTemplate()):
        self._templates.pop(template.id)

    def get_cur_template(self):
        if self._cur_template is None:
            return None

        return self._templates[self._cur_template]

    def get_all_templates(self):
        return self._templates.values()

    def set_cur_template(self, template=BuildingTemplate()):
        self._cur_template = template.id

    # last edit building
    def get_cur_building(self):
        return self._cur_building

    def set_cur_building(self, building_id="my_building"):
        self._cur_building = building_id

    # save / lod
    def save(self):
        mc.optionVar(sv=(self.__option_var_key, json.dumps(self.get_serializable())))

    @staticmethod
    def load():
        # no profile? -> create new one
        if mc.optionVar(exists=UserProfile.__option_var_key) == 0:
            profile = UserProfile()

            # add default building template
            default_template = BuildingTemplate()
            profile.add_template(default_template)
            profile.set_cur_template(default_template)

            return profile

        # load profile from option vars
        serialized = mc.optionVar(query=UserProfile.__option_var_key)
        serializable = json.loads(serialized)
        return UserProfile.get_from_serializable(serializable)

    # region Serialization
    def get_serializable(self):
        # default values
        result = {}
        result["cur_template"] = self._cur_template
        result["cur_building"] = self._cur_building

        # templates
        templates = {}
        for template in self._templates.values():
            templates[template.id] = template.get_serializable()
        result["templates"] = templates

        return result

    @staticmethod
    def get_from_serializable(serializable={}):
        profile = UserProfile()
        profile._cur_template = serializable["cur_template"]
        profile._cur_building = serializable["cur_building"]

        for serializable_template in serializable["templates"].values():
            template = BuildingTemplate.get_from_serializable(serializable_template)
            profile.add_template(template)

        return profile
    # endregion