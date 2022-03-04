from datetime import datetime
from json import JSONEncoder, loads
from bson.objectid import ObjectId

class CustomEncoder(JSONEncoder):
    """A C{json.JSONEncoder} subclass to encode documents that have fields of
    type C{bson.objectid.ObjectId}, C{datetime.datetime}
    """
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return ObjectId.__str__(obj)
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return loads(JSONEncoder.default(self, obj))