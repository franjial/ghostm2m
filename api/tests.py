from django.conf import settings
from django.test import TestCase
from django.test.client import Client

from onem2m.db import DBConnection
from bson.objectid import ObjectId


from onem2m.mappers import CSEBaseMapper, MappersFactory
from onem2m.resources import ResourcesFactory, AE, Container
from onem2m.types import ResourceType, Operation
from onem2m.security import User

import json
import sys


class TestOneM2MAPI(TestCase):
    def setUp(self):
        self.c = Client()
        settings.GHOSTM2M["dbname-test"]
        DBConnection().set_db(settings.GHOSTM2M["dbname-test"])

    def test_module_create_ae(self):
        f = ResourcesFactory()

        # create CSE
        csebase = f.create(ResourceType.CSEBase.value)
        csebase.set_csi(settings.GHOSTM2M['CSE-ID'])
        csebase_ri = CSEBaseMapper().store(settings.GHOSTM2M['CSE-ID'], csebase)

        # create AE
        ae = f.create(ty=ResourceType.AE.value, 
                      pi=csebase_ri, 
                      pc={'m2m:ae':{'api':'test','apn':'rfid-reader'}})
                      
        ae_mapper = MappersFactory().get(ae)
        ae_ri = ae_mapper.store(settings.GHOSTM2M['CSE-ID'], ae)

        # test dict
        self.assertIn('m2m:ae',ae.resource)
        self.assertIn('pi', ae.resource['m2m:ae'])
        self.assertEqual(csebase_ri, ae.resource['m2m:ae']['pi'])

        # test module 
        self.assertEqual(ae.apn, 'rfid-reader')
        self.assertEqual(ae.api, 'test')
        self.assertEqual(ae.pi, csebase_ri)

        recorded_ae = ae_mapper.retrieve(settings.GHOSTM2M['CSE-ID'], {'_id': ObjectId(ae_ri)})

        self.assertIsInstance(recorded_ae, AE)
        self.assertEqual(recorded_ae.apn, 'rfid-reader')
        self.assertEqual(recorded_ae.api, 'test')
        self.assertEqual(recorded_ae.pi, csebase_ri)

    def test_api_create_ae(self):
        

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

    def test_module_create_cnt(self):
        f = ResourcesFactory()

        # create CSE
        csebase = f.create(ResourceType.CSEBase.value)
        csebase.set_csi(settings.GHOSTM2M['CSE-ID'])
        csebase_ri = CSEBaseMapper().store(settings.GHOSTM2M['CSE-ID'], csebase)

        # create parent AE
        ae = f.create(ty=ResourceType.AE.value, 
                      pi=csebase_ri, 
                      pc={'m2m:ae':{'api':'test','apn':'rfid-reader'}})
                      
        ae_mapper = MappersFactory().get(ae)
        ae_ri = ae_mapper.store(settings.GHOSTM2M['CSE-ID'], ae)

        # create Container
        cnt = f.create(ty=ResourceType.container.value,
                       pi=ae_ri,
                       pc={'m2m:cnt':{'rn':'corner-rfids'}})
        cnt_mapper = MappersFactory().get(cnt)
        cnt_ri = cnt_mapper.store(settings.GHOSTM2M['CSE-ID'], cnt)
        recorded_cnt = cnt_mapper.retrieve(settings.GHOSTM2M['CSE-ID'], {'_id': ObjectId(cnt_ri)})

        # test dict
        self.assertIn('m2m:cnt',cnt.resource)
        self.assertIn('pi', cnt.resource['m2m:cnt'])
        self.assertIn('rn', cnt.resource['m2m:cnt'])

        self.assertEqual(ae_ri, cnt.resource['m2m:cnt']['pi'])
        self.assertEqual('corner-rfids', cnt.resource['m2m:cnt']['rn'])

        # test module 
        self.assertEqual(cnt.rn, 'corner-rfids')
        self.assertEqual(cnt.pi, ae_ri)

        # test db
        self.assertIsInstance(recorded_cnt, Container)
        self.assertEqual(recorded_cnt.rn, 'corner-rfids')
        self.assertEqual(recorded_cnt.pi, ae_ri)

    def test_api_create_cnt(self):
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
        response_ae = json.loads(response.content)['m2m:rsp']

        factory = ResourcesFactory()
        parent_ae = factory.create(request['m2m:rqp']['ty'], pc=response_ae['pc'])

        request = {'m2m:rqp':{
            'op': Operation.Create.value,
            'ty': ResourceType.container.value,
            'pc':{'m2m:cnt': {'rn':'corners-rfids'}},
            'fr':'{}:{}'.format(settings.GHOSTM2M['admin-user']['username'],settings.GHOSTM2M['admin-user']['pwd']),
            'to':'//localhost:80/Cernicalo',
        }}
        response = self.client.post('/~/Cernicalo/{}'.format(parent_ae.ri),
            json.dumps(request),
            content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        response_cnt = json.loads(response.content)['m2m:rsp']
        cnt = factory.create(request['m2m:rqp']['ty'], pc=response_cnt['pc'])

        self.assertIsInstance(cnt, Container)
        self.assertEqual(cnt.pi, parent_ae.ri)
        self.assertEqual(cnt.rn, 'corners-rfids')


    def tearDown(self):
        sys.stderr.write('Eliminar base de datos test.\n')
        DBConnection().db_client.drop_database(settings.GHOSTM2M["dbname-test"])

