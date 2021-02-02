from onem2m.db import DBConnection
from bson.objectid import ObjectId

class User:
    def __init__(self, username, pwd):
        self._username = username
        self._pwd = pwd

    def valid(self):
        result = DBConnection().db['users'].find_one({'_id':self._username})
        if result is None:
            return False
        elif self._pwd==result['pwd']:
            return True
        else:
            return False
