from onem2m.db import DBConnection
from django.conf import settings

def run():
    try:
        users = DBConnection().db['users']
        result = users.insert_one({'_id':settings.GHOSTM2M['admin-user']['username'],'pwd':settings.GHOSTM2M['admin-user']['pwd']})
    except Exception:
        print('no se crea usuario admin')