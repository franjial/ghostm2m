from onem2m.resources import ResourcesFactory
from onem2m.mappers import CSEBaseMapper
from onem2m.db import DBConnection
from django.conf import settings
from onem2m.types import ResourceType


def run():
    """
    reset db
    """
    try:
        DBConnection().db_client.drop_database(settings.GHOSTM2M["dbname"])
        DBConnection().db_client.drop_database('users')
        print('OK')
    except Exception as e:
        print(str(e))

    # create CSEBase
    resource = ResourcesFactory().create(ResourceType.CSEBase.value)
    resource.set_csi(settings.GHOSTM2M['CSE-ID'])
    
    base = DBConnection().db[settings.GHOSTM2M['CSE-ID']]
    result = base.find_one({'ty':ResourceType.CSEBase.value,'csi': settings.GHOSTM2M['CSE-ID']})
    if result is None:
        ri=CSEBaseMapper().store(settings.GHOSTM2M['CSE-ID'], resource)
        print('Creado CSEBase. ', ri)
    else:
        print('CSEBase ya existe. ', result)

    # create user admin
    try:
        users = DBConnection().db['users']
        result = users.insert_one({'_id':settings.GHOSTM2M['admin-user']['username'],'pwd':settings.GHOSTM2M['admin-user']['pwd']})
        print("se crea usuario admin")
    except Exception as e:
        print('no se crea usuario admin')
        print(str(e))

        