# Object is the base class for most types
# Objects can be converted into a serialized and deserialized
class Object(object):

    # serialization
    def get_serializable(self):
        return {}

    @staticmethod
    def get_from_serializable(serializable={}):
        return Object()

