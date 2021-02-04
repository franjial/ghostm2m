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
		self.ty = None # resourceType
		self.pi = None # parent-id
		self.ri = None # resource-id
		
		self._rtn = None # p.e. m2m:cnt
		self._set_rtn()

		self.resource = dict()
		self.resource[self._rtn] = dict()


	@abstractmethod
	def _set_rtn(self):
		self._rtn = None

	def get_rtn(self):
		return self._rtn

	def get_type_name(self):
		return self._rtn

	def load(self, pc):
		if isinstance(pc, dict):
			self.resource[self._rtn] = pc[self._rtn]
			for key in pc[self._rtn]:
				if isinstance(pc[self._rtn][key], ObjectId):
					pc[self._rtn][key] = str(pc[self._rtn][key])
				#setattr(self, key, pc[self._rtn][key])
		else:
			raise TypeError('pc arg must be a dict')

	def set_id(self, _id):
		self._id = _id
		self.ri = _id
		self.resource[self._rtn]['ri'] = _id


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
	AE resource class
	"""
	def __init__(self):
		super().__init__()

		self.api = None  # APP-ID
		self.apn = None  # [appname]

	def _set_rtn(self):
		self._rtn = "m2m:ae"

	def load(self, pc):
		super().load(pc)

		for key in pc[self._rtn]:
			if key=='apn': self.apn=pc[self._rtn]['apn']
			if key=='api': self.api=pc[self._rtn]['api']
			if key=='pi': self.pi=pc[self._rtn]['pi']
			if key=='ri': self.ri=pc[self._rtn]['ri']

	def set_id(self, _id):
		super().set_id(_id)

		self.aei = 'C'+_id
		self.resource[self._rtn]['aei'] = self.aei

	def get_id(self):
		return self._id

class Container(Resource):
	"""
	The <container> resource represents a container for data instances. It is used to share 
	information with other entities and potentially to track the data. A <container> resource 
	has no associated content. It has only attributes and child resources.
	"""
	def __init__(self):
		super().__init__()
		self.resource[self._rtn] = dict()
		
		#self.resource[self._rtn]['la'] = None
		#self.resource[self._rtn]['ol'] = None
		self.resource[self._rtn]['ct'] = datetime.datetime.now() #creationTime
		self.resource[self._rtn]['lt'] = self.resource["m2m:cnt"]['ct'] #lastModifiedTime

		self.la = None
		self.ol = None
		self.ct = self.resource[self._rtn]['ct']
		self.lt = self.resource[self._rtn]['ct']
		self.rn = None # resourceName

	def load(self, pc):
		super().load(pc)

		for key in pc[self._rtn]:
			if key=='la': self.la=pc[self._rtn]['la']
			if key=='ol': self.ol=pc[self._rtn]['ol']
			if key=='ct': self.ct=pc[self._rtn]['ct']
			if key=='lt': self.lt=pc[self._rtn]['lt']
			if key=='rn': self.rn=pc[self._rtn]['rn']
			if key=='pi': self.pi=pc[self._rtn]['pi']

	def _set_rtn(self):
		self._rtn = "m2m:cnt"

class ContentInstance(Resource):
	"""
	ContentInstance resource
	"""
	def __init__(self):
		super().__init__()

		self.rn = None  # resourceName
		self.con = None # content
		self._st = 0     # stateTag
		self.ct = datetime.datetime.now()  # creationTime
		self.lt = self.ct  #lastModifiedTime

		self.resource[self._rtn]['ct'] = self.ct
		self.resource[self._rtn]['lt'] = self.lt
		self.resource[self._rtn]['st'] = self.st
		self.resource[self._rtn]['cs'] = self.cs

	##
	# ONLY READ PROPERTIES
	#

	@property
	def cs(self):
		if self.con is None: return 0
		else: return len(self.con)

	@property
	def st(self):
		return self._st
	
	#
	# ONLY READ PROPERTIES
	######


	def _set_rtn(self):
		self._rtn = "m2m:cin"

	def load(self, pc):
		super().load(pc)

		for key in pc[self._rtn]:
			if key=='pi': self.pi=pc[self._rtn]['pi']    # parentID
			if key=='rn': self.rn=pc[self._rtn]['rn']    # resourceName
			if key=='con': self.con=pc[self._rtn]['con'] # content
			if key=='st': self._st=pc[self._rtn]['st']   # stateTag


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
	def create(self, ty, **kwargs):
		resource_data = dict()
		resource = None

		pc = kwargs.get('pc', None)
		ri = kwargs.get('ri', None)
		pi = kwargs.get('pi', None)

		if ty == ResourceType.contentInstance.value:
			resource = self.create_content_instance(**kwargs)

		if ty == ResourceType.container.value:
			resource = self.create_container(**kwargs)
		
		if ty == ResourceType.AE.value:
			resource = self.create_ae(**kwargs)

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

	def create_container(self, **kwargs):
		ri = kwargs.get('ri', None)
		pi = kwargs.get('pi', None)
		pc = kwargs.get('pc', None)
		rn = kwargs.get('rn', None)
		
		con = Container()
		if pc is not None: 
			con.load(pc)
			try:
				pc_ri = con.resource['m2m:cnt']['ri']
				con.set_id(pc_ri)
			except:
				if ri is not None:
					con.set_id(ri)

		if rn is not None: con.rn = rn
		if pi is not None: con.set_pi(pi)
		
		return con

	def create_content_instance(self, **kwargs):
		ri = kwargs.get('ri', None)
		pi = kwargs.get('pi', None)
		pc = kwargs.get('pc', None)

		cin = ContentInstance()
		if pc is not None: 
			cin.load(pc)
			try:
				pc_ri = cin.resource['m2m:cin']['ri']
				cin.set_id(pc_ri)
			except:
				if ri is not None:
					cin.set_id(ri)
		if pi is not None: cin.set_pi(pi)

		return cin

	def create_ae(self, **kwargs):
		ri = kwargs.get('ri', None)
		pi = kwargs.get('pi', None)
		pc = kwargs.get('pc', None)	

		ae = AE()

		if pc is not None: ae.load(pc)
		if pc is not None: 
			ae.load(pc)
			try:
				pc_ri = ae.resource['m2m:ae']['ri']
				ae.set_id(pc_ri)
			except:
				if ri is not None:
					ae.set_id(ri)

		if pi is not None: ae.set_pi(pi)

		return ae
