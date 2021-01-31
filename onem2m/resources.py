from onem2m.types import Operation, ResourceType, cseTypeID
from pymongo import MongoClient
from bson.objectid import ObjectId
from abc import ABC, abstractmethod
import json
import datetime

class AbstractFactory(ABC):
	"""

	"""
	@abstractmethod
	def create_container(self):
		pass

	@abstractmethod
	def create_content_instance(self):
		pass

	@abstractmethod
	def create_ae(self):
		pass

class Resource(ABC):
	def __init__(self):

		self._id = None
		self.ty = None  #resourceType
		
		self._rtn = None # p.e. m2m:cnt
		self._set_rtn()

		self.resource = dict()
		self.resource[self._rtn] = dict()


	@abstractmethod
	def _set_rtn(self):
		self._rtn = None

	def get_type_name(self):
		return self._rtn

	def load(self, pc):
		if isinstance(pc, dict):
			self.resource[self._rtn] = pc[self._rtn]
			for key in pc[self._rtn]:
				if isinstance(pc[self._rtn][key], ObjectId):
					pc[self._rtn][key] = str(pc[self._rtn][key])
				setattr(self, key, pc[self._rtn][key])
		else:
			raise TypeError('pc arg must be a dict')

	def set_id(self, _id):
		self._id = _id

		try:
			self.resource[self._rtn]['ri'] = _id
		except:
			raise KeyError

	def get_id(self):
		return self._id

	def set_pi(self, pi):
		self.pi = pi
		self.resource[self._rtn]['pi'] = pi

	def toJSON(self):
		if "_id" in self.resource:
			self.resource.pop("_id")
		return json.dumps(self.resource)

	def toDict(self):
		if "_id" in self.resource:
			self.resource.pop("_id")

		if "ty" in self.resource:
			self.resource.pop("ty")

		return self.resource

class AE(Resource):
	"""
	common interface of all AE resources
	"""
	def __init__(self):
		super().__init__()

	def _set_rtn(self):
		self._rtn = "m2m:ae"

	def set_id(self, _id):
		super().set_id(_id)

		self.aei = 'C'+_id
		self.resource[self._rtn]['aei'] = self.aei

	def get_id(self):
		return self._id

	def get_aei(self):
		return self.aei

class Container(Resource):
	def __init__(self):
		super().__init__()
		self._rtn = "m2m:cnt"
		self.resource["m2m:cnt"] = dict()
		
		self.resource["m2m:cnt"]['la'] = {}
		self.resource["m2m:cnt"]['ol'] = {}
		self.resource["m2m:cnt"]['ct'] = datetime.datetime.now() #creationTime
		self.resource["m2m:cnt"]['lt'] = self.resource["m2m:cnt"]['ct'] #lastModifiedTime

		self.la = {}
		self.ol = {}
		self.ct = self.resource["m2m:cnt"]['ct']
		self.lt = self.resource["m2m:cnt"]['ct']

	def _set_rtn(self):
		self._rtn = "m2m:cnt"

	def set_la(self, la):
		if isinstance(la, dict):
			self.la = la
		else:
			raise TypeError

	def set_ol(self, ol):
		if isinstance(ol, dict):
			self.ol = ol
		else:
			raise TypeError

class ContentInstance(Resource):
	"""
	common interface of all ContentInstance resources
	"""
	def __init__(self):
		super().__init__()

	def _set_rtn(self):
		self._rtn = "m2m:cin"

	def set_content(self, con):
		self.resource["m2m:cin"]["con"] = con

class CSEBase(Resource):
	def __init__(self):
		super().__init__()	
		self.csi = None #CSE-ID
		self.cst = cseTypeID.IN_CSE.value

		self.resource[self._rtn] = dict()
		self.resource[self._rtn]['csi'] = self.csi
		self.resource[self._rtn]['cst'] = self.cst

		#self.CSE_ID = "Cernicalo"
		#self.cseType = cseTypeID.IN_CSE.value
		#self.supportedReleaseVersions = list()

	def _set_rtn(self):
		self._rtn = "m2m:cb"

	def set_csi(self, csi):
		self.csi = csi
		self.resource[self._rtn]['csi'] = csi

class ResourcesFactory(AbstractFactory):
	def create(self, ty, pc={}, ri=None, pi=None):
		resource_data = dict()
		resource = None

		if ty == ResourceType.contentInstance.value:

			try:
				if "m2m:cin" in pc:
					resource_data = pc["m2m:cin"]
					resource = self.create_content_instance(pc, ri=ri, pi=pi)
				else:
					pc = {"m2m:cin":{}}
					resource = self.create_content_instance(pc, ri=ri, pi=pi)
			except:
				pc = {"m2m:cin":{}}
				resource = self.create_content_instance(pc, ri=ri, pi=pi)

		if ty == ResourceType.container.value:
			try:
				if "m2m:cnt" in pc:
					resource_data = pc["m2m:cnt"]
					resource = self.create_container(pc, ri=ri, pi=pi)
				else:
					pc = {"m2m:cnt":{}}
					resource = self.create_container(pc, ri=ri, pi=pi)
			except Exception as e:
				pc = {"m2m:cnt":{}}
				resource = self.create_container(pc, ri=ri, pi=pi)	

		if ty == ResourceType.AE.value:
			try:
				if "m2m:ae" in pc:
					resource_data = pc["m2m:ae"]
					resource = self.create_ae(pc, ri=ri, pi=pi)
				else:
					resource = self.create_ae(ri=ri, pi=pi)
			except:
				resource = self.create_ae(ri=ri, pi=pi)

		if ty == ResourceType.CSEBase.value:
			try:
				if "m2m:cb" in pc:
					resource_data = pc["m2m:cb"]
					resource = self.create_csebase(pc, ri=ri)
				else:
					resource = self.create_csebase(ri=ri)
			except:
				resource = self.create_csebase(ri=ri)

		if resource is not None:
			resource.ty = ty
			return resource
		else:
			raise NotImplementedError


	def create_csebase(self, pc=None, ri=None, pi=None):
		cb = CSEBase()
		if pc is not None:
			cb.load(pc)
		if ri is not None:
			cb.set_id(ri)

		return cb

	def create_container(self, pc=None, ri=None, pi=None):
		con = Container()
		if pc is not None:
			con.load(pc)
		if ri is not None:
			con.set_id(ri)

		if pi is not None:
			con.set_pi(pi)

		return con

	def create_content_instance(self, pc=None, ri=None, pi=None):
		cin = ContentInstance()
		if pc is not None:
			cin.load(pc)
		if ri is not None:
			cin.set_id(ri)

		if pi is not None:
			cin.set_pi(pi)


		return cin

	def create_ae(self, pc=None, ri=None, pi=None):
		ae = AE()
		if pc is not None:
			ae.load(pc)

		if ri is not None:
			ae.set_id(ri)

		if pi is not None:
			ae.set_pi(pi)

		return ae
