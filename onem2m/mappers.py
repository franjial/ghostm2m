from onem2m.resources import ResourcesFactory, Resource, ContentInstance, CSEBase
from onem2m.db import DBConnection
from bson.objectid import ObjectId

class MappersFactory:
	def __init__(self):
		pass

	def get(self, resource):
		if isinstance(resource, ContentInstance):
			mapper = ContentInstanceMapper()
		
		elif isinstance(resource, Resource):
			mapper = ResourceMapper()
		
		else:
			raise TypeError

		return mapper




class ResourceMapper:

	def __init__(self):
		self._db =  DBConnection().db

	def store(self, cseid, resource):
		if isinstance(resource, Resource):
			to_store = resource.toDict()[resource.get_rtn()].copy()
			to_store['rtn'] = resource.get_rtn()
			to_store['ty'] = resource.ty
			result = self._db[cseid].insert_one(to_store)

			return str(result.inserted_id)
		else:
			raise TypeError

	def retrieve(self, cseid, ft):
		if cseid not in self._db.list_collection_names():
			raise KeyError

		result = self._db[cseid].find_one(ft)
		
		if result is None:
			return None

		elif 'ty' in result:
			resource = ResourcesFactory().create(ty=result['ty'])
			resource.load(pc={resource.get_rtn(): result})

			rtn = None
			if 'rtn' in result:
				rtn = result['rtn']
				result.pop('rtn')
			else:
				raise KeyError

			_id = None
			if '_id' in result:
				_id = result['_id']
				result.pop('_id')
			else:
				raise KeyError

			resource.load({rtn: result})
			resource.set_id(str(_id))

			return resource

		else:
			raise TypeError

	def discovery(self, cseid, pi, fc):
		mongodb_filter = dict()
		mongodb_filter = fc.copy()

		if 'ty' in mongodb_filter: mongodb_filter['ty'] = int(mongodb_filter['ty'])
		#TODO continue with params in Table Summary on Filter conditions (Table 7.3.3.17.0 Document TS-0004)

		mongodb_filter['pi']=str(pi)
		result = self._db[cseid].find(mongodb_filter)
		ret = list()
		for doc in result:
			ret.append('//{}/{}'.format(cseid, str(doc['_id'])))
		return ret

	#def delete(self, cseid, ri):
	#	pass
	#

	#def update(self, cseid, newresource):
	#	pass


class ContentInstanceMapper(ResourceMapper):
	def __init__(self):
		super().__init__()

	def store(self, csi, resource):
		stored_ri = None
		if isinstance(resource, ContentInstance):
			stored_ri = super().store(csi, resource)
		else:
			raise TypeError

		if resource.pi is not None and stored_ri is not None:
			cnt_childs = self._db[csi].find({'pi':resource.pi})
			self._db[csi].update_one({'_id':ObjectId(resource.pi)},
									 {'$set': {'la':ObjectId(stored_ri),
									     	   'cni': cnt_childs.count()}} )
		return stored_ri


class CSEBaseMapper(ResourceMapper):
	def __init__(self):
		super().__init__()

	def store(self, cseid, resource):
		if isinstance(resource, CSEBase):
			return super().store(cseid, resource)
		else:
			raise TypeError



		