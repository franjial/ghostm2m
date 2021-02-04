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


	#def delete(self, cseid, ri):
	#	pass
	#

	#def update(self, cseid, newresource):
	#	pass


class ContentInstanceMapper(ResourceMapper):
	def __init__(self):
		super().__init__()

	def store(self, csi, resource):

		if isinstance(resource, ContentInstance):
			ri = super().store(csi, resource)
		else:
			raise TypeError

		if hasattr(resource, 'pi') and resource.pi is not None:
			self._db[csi].update_one({'_id':ObjectId(resource.pi)},{'$set': {'m2m:cnt': {'la':ObjectId(ri)}}})

		return ri


class CSEBaseMapper(ResourceMapper):
	def __init__(self):
		super().__init__()

	def store(self, cseid, resource):
		if isinstance(resource, CSEBase):
			return super().store(cseid, resource)
		else:
			raise TypeError



		