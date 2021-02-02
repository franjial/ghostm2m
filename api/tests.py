from django.conf import settings
from django.test import TestCase
from django.test.client import Client

from onem2m.db import DBConnection
from bson.objectid import ObjectId


from onem2m.mappers import CSEBaseMapper
from onem2m.resources import ResourcesFactory
from onem2m.types import ResourceType
from onem2m.security import User

import json
import sys


class TestOneM2MAPI(TestCase):
    def setUp(self):
        self.c = Client()
        settings.GHOSTM2M["dbname-test"]
        DBConnection().set_db(settings.GHOSTM2M["dbname-test"])


    def test_can_create_ae(self):
        # create CSE
        resource = ResourcesFactory().create(ResourceType.CSEBase.value)
        resource.set_csi(settings.GHOSTM2M['CSE-ID'])
        CSEBaseMapper().create(settings.GHOSTM2M['CSE-ID'], resource)

        # create admin user 
        result = DBConnection().db['users'].find_one({'_id': settings.GHOSTM2M['admin-user']['username']})
        if result is None:
            DBConnection().db['users'].insert_one({'_id':settings.GHOSTM2M['admin-user']['username'],'pwd':settings.GHOSTM2M['admin-user']['pwd']})

        # send request for create AE
        request = {'m2m:rqp':{
            'op':1,
            'ty':1,
            'pc':{'m2m:ae': {"apn":"lector-tarjetas"}},
            'fr':'{}:{}'.format(settings.GHOSTM2M['admin-user']['username'],settings.GHOSTM2M['admin-user']['pwd']),
            'to':'//localhost:80/Cernicalo'
        }}

        response = self.client.post('/~/Cernicalo/',
            json.dumps(request),
            content_type="application/json")

        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content)
        self.assertIn('m2m:rsp', response_content)
        self.assertIn('pc', response_content['m2m:rsp'])
        self.assertIn('m2m:ae', response_content['m2m:rsp']['pc'])

    def tearDown(self):
        sys.stderr.write('Eliminar base de datos test.\n')
        DBConnection().db_client.drop_database(settings.GHOSTM2M["dbname-test"])

