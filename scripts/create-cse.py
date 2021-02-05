from onem2m.resources import ResourcesFactory
from onem2m.mappers import CSEBaseMapper
from onem2m.db import DBConnection
from django.conf import settings
from onem2m.types import ResourceType

def run():
    """
    create a CSEBase
    """
    resource = ResourcesFactory().create(ResourceType.CSEBase.value)
    resource.set_csi(settings.GHOSTM2M['CSE-ID'])
    
    base = DBConnection().db[settings.GHOSTM2M['CSE-ID']]
    result = base.find_one({'ty':ResourceType.CSEBase.value,'m2m:cb':{'csi': settings.GHOSTM2M['CSE-ID']}})
    if result is None:
        ri=CSEBaseMapper().store(settings.GHOSTM2M['CSE-ID'], resource)
        print('Creado CSEBase. ', ri)
    else:
        print('CSEBase ya existe. ', result)
        