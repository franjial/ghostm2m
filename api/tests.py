from django.conf import settings
from django.test import TestCase
from django.test.client import Client

from onem2m.db import DBConnection
from bson.objectid import ObjectId


from onem2m.mappers import CSEBaseMapper, MappersFactory, ResourceMapper
from onem2m.resources import ResourcesFactory, AE, Container, ContentInstance
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
        cnt.set_id(cnt_ri)
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
        self.assertEqual(cnt.ri, cnt_ri)

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
        response = json.loads(response.content)
        self.assertIn('m2m:rsp', response)
        self.assertIn('pc', response['m2m:rsp'])
        self.assertIn('m2m:cnt', response['m2m:rsp']['pc'])
        self.assertIn('ri', response['m2m:rsp']['pc']['m2m:cnt'])

        response_cnt = response['m2m:rsp']
        cnt = factory.create(request['m2m:rqp']['ty'], pc=response_cnt['pc'])

        self.assertIsInstance(cnt, Container)
        self.assertEqual(cnt.pi, parent_ae.ri)
        self.assertEqual(cnt.rn, 'corners-rfids')
        self.assertEqual(cnt.ri, response['m2m:rsp']['pc']['m2m:cnt']['ri'])

    def test_module_create_cin(self):
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
        ae.set_id(ae_ri)

        # create Container
        cnt = f.create(ty=ResourceType.container.value,
                       pi=ae_ri,
                       pc={'m2m:cnt':{'rn':'corner-rfids'}})
        cnt_mapper = MappersFactory().get(cnt)
        cnt_ri = cnt_mapper.store(settings.GHOSTM2M['CSE-ID'], cnt)
        cnt.set_id(cnt_ri)
        recorded_cnt = cnt_mapper.retrieve(settings.GHOSTM2M['CSE-ID'], {'_id': ObjectId(cnt_ri)})


        # create ContentInstance
        cin = f.create(ty=ResourceType.contentInstance.value,
                       pi=cnt_ri,
                       pc={'m2m:cin':{'con':'abcdef'}})
        cin_mapper = MappersFactory().get(cin)
        cin_ri = cin_mapper.store(settings.GHOSTM2M['CSE-ID'], cin)
        cin.set_id(cin_ri)
        recorded_cin = cin_mapper.retrieve(settings.GHOSTM2M['CSE-ID'], {'_id': ObjectId(cin_ri)})

        # test dict
        self.assertIn('m2m:cin',cin.resource)
        self.assertIn('pi', cin.resource['m2m:cin'])
        self.assertIn('con', cin.resource['m2m:cin'])

        self.assertEqual(cnt_ri, cin.resource['m2m:cin']['pi'])
        self.assertEqual('abcdef', cin.resource['m2m:cin']['con'])

        # test module 
        self.assertEqual(cin.con, 'abcdef')
        self.assertEqual(cin.pi, cnt_ri)

        # test db
        self.assertIsInstance(recorded_cin, ContentInstance)
        self.assertEqual(recorded_cin.con, 'abcdef')
        self.assertEqual(recorded_cin.pi, cnt_ri)

    def test_api_create_cin(self):
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
            'to':'/~/Cernicalo/{}'.format(parent_ae.ri),
        }}
        response = self.client.post('/~/Cernicalo/{}'.format(parent_ae.ri),
            json.dumps(request),
            content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        response_cnt = json.loads(response.content)['m2m:rsp']
        cnt = factory.create(request['m2m:rqp']['ty'], pc=response_cnt['pc'])

        request = {'m2m:rqp':{
            'op': Operation.Create.value,
            'ty': ResourceType.contentInstance.value,
            'pc':{'m2m:cin': {'con':'hola mundo!'}},
            'fr':'{}:{}'.format(settings.GHOSTM2M['admin-user']['username'],settings.GHOSTM2M['admin-user']['pwd']),
            'to':'/~/Cernicalo/{}'.format(cnt.ri),
        }}

        
        response = self.client.post('/~/Cernicalo/{}'.format(cnt.ri),
                                    json.dumps(request),
                                    content_type="application/json")
        
        self.assertIn('m2m:rsp', json.loads(response.content))
        response_cin = json.loads(response.content)['m2m:rsp']

        self.assertIn('m2m:cin',response_cin['pc'])

        cin = factory.create(request['m2m:rqp']['ty'], pc=response_cin['pc'])
        

        self.assertIsInstance(cin, ContentInstance)
        self.assertEqual(cin.pi, cnt.ri)
        self.assertEqual(cin.con, 'hola mundo!')

        parent = ResourceMapper().retrieve(cseid=settings.GHOSTM2M['CSE-ID'], ft={'_id':ObjectId(cin.pi)})
        self.assertIsInstance(parent, Container)
        self.assertNotEqual(parent.la, None)

    def test_api_retrieve(self):

        f = ResourcesFactory()

        # create admin user 
        result = DBConnection().db['users'].find_one({'_id': settings.GHOSTM2M['admin-user']['username']})
        if result is None:
            DBConnection().db['users'].insert_one({'_id':settings.GHOSTM2M['admin-user']['username'],'pwd':settings.GHOSTM2M['admin-user']['pwd']})


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
        ae.set_id(ae_ri)

        # create Container
        cnt = f.create(ty=ResourceType.container.value,
                       pi=ae_ri,
                       pc={'m2m:cnt':{'rn':'corner-rfids'}})
        cnt_mapper = MappersFactory().get(cnt)
        cnt_ri = cnt_mapper.store(settings.GHOSTM2M['CSE-ID'], cnt)
        cnt.set_id(cnt_ri)
        
        # create ContentInstance
        cin = f.create(ty=ResourceType.contentInstance.value,
                       pi=cnt_ri,
                       pc={'m2m:cin':{'con':'abcdef'}})
        cin_mapper = MappersFactory().get(cin)
        cin_ri = cin_mapper.store(settings.GHOSTM2M['CSE-ID'], cin)
        cin.set_id(cin_ri)

        # Request CSE
        # @TODO

        # Request AE
        request = {'m2m:rqp':{
            'op': Operation.Retrieve.value,
            'fr':'{}:{}'.format(settings.GHOSTM2M['admin-user']['username'],settings.GHOSTM2M['admin-user']['pwd']),
            'to':'/~/Cernicalo',
        }}

        request_str = json.dumps(request)
        response = self.client.generic('GET', '/~/Cernicalo/{}'.format(ae_ri),
                                    request_str,
                                    'application/json')
        self.assertEqual(response.status_code, 200)
        response_ae = json.loads(response.content)['m2m:rsp']
        self.assertIn('pc', response_ae)
        self.assertIn('m2m:ae', response_ae['pc'])
        self.assertIn('apn', response_ae['pc']['m2m:ae'])
        self.assertIn('ri', response_ae['pc']['m2m:ae'])

        # Request Container
        request = {'m2m:rqp':{
            'op': Operation.Retrieve.value,
            'fr':'{}:{}'.format(settings.GHOSTM2M['admin-user']['username'],settings.GHOSTM2M['admin-user']['pwd']),
            'to':'/~/Cernicalo',
        }}

        request_str = json.dumps(request)
        response = self.client.generic('GET', '/~/Cernicalo/{}'.format(cnt_ri),
                                    request_str,
                                    'application/json')
        self.assertEqual(response.status_code, 200)
        response_cnt = json.loads(response.content)['m2m:rsp']
        self.assertIn('pc', response_cnt)
        self.assertIn('m2m:cnt', response_cnt['pc'])
        self.assertIn('rn', response_cnt['pc']['m2m:cnt'])
        self.assertIn('ri', response_cnt['pc']['m2m:cnt'])

        # Request ContentInstance
        request = {'m2m:rqp':{
            'op': Operation.Retrieve.value,
            'fr':'{}:{}'.format(settings.GHOSTM2M['admin-user']['username'],settings.GHOSTM2M['admin-user']['pwd']),
            'to':'/~/Cernicalo',
        }}

        request_str = json.dumps(request)
        response = self.client.generic('GET', '/~/Cernicalo/{}'.format(cin_ri),
                                    request_str,
                                    'application/json')
        self.assertEqual(response.status_code, 200)
        response_cin = json.loads(response.content)['m2m:rsp']
        self.assertIn('pc', response_cin)
        self.assertIn('m2m:cin', response_cin['pc'])
        self.assertIn('con', response_cin['pc']['m2m:cin'])
        self.assertIn('ri', response_cin['pc']['m2m:cin'])

        # Request <last> <ContentInstance>
        request = {'m2m:rqp':{
            'op': Operation.Retrieve.value,
            'fr':'{}:{}'.format(settings.GHOSTM2M['admin-user']['username'],settings.GHOSTM2M['admin-user']['pwd']),
            'to':'/~/Cernicalo',
        }}
        request_str = json.dumps(request)
        response = self.client.generic('GET', '/~/Cernicalo/{}/la'.format(cnt_ri),
                                    request_str,
                                    'application/json')
        self.assertEqual(response.status_code, 200)
        response_la = json.loads(response.content)['m2m:rsp']
        self.assertIn('pc', response_cin)
        
        







    def tearDown(self):
        #sys.stderr.write('Eliminar base de datos test.\n')
        DBConnection().db_client.drop_database(settings.GHOSTM2M["dbname-test"])

