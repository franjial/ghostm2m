from django.conf import settings
from django.test import TestCase
from django.test.client import Client

from onem2m.db import DBConnection
from bson.objectid import ObjectId


from onem2m.mappers import CSEBaseMapper
from onem2m.resources import ResourcesFactory
from onem2m.types import ResourceType

import json

class TestOneM2MAPI(TestCase):
    def setUp(self):
        self.c = Client()
        settings.GHOSTM2M["dbname-test"]
        DBConnection().set_db(settings.GHOSTM2M["dbname-test"])

    def __del__(self):
        DBConnection().db_client.drop_database(settings.GHOSTM2M["dbname-test"])


    def test_can_create_csebase(self):
        resource = ResourcesFactory().create(ResourceType.CSEBase.value)
        resource.set_csi(settings.GHOSTM2M['CSE-ID'])
        ri = CSEBaseMapper().create(settings.GHOSTM2M['CSE-ID'], resource)

        stored = DBConnection().db[settings.GHOSTM2M['CSE-ID']].find_one({'_id':ObjectId(ri)})
        self.assertIn('m2m:cb', stored)
        self.assertIn('csi', stored['m2m:cb'])
        self.assertIn('ty', stored)
        self.assertEqual(stored['m2m:cb']['csi'], settings.GHOSTM2M['CSE-ID'])
        self.assertEqual(stored['ty'], 5)


    def test_can_create_ae(self):
        request = {'m2m:rqp':{
            'op':1,
            'ty':1,
            'pc':{'m2m:ae': {"apn":"lector-tarjetas"}},
            'fr':'/Cernicalo/',
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

