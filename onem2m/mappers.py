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

	def create(self, cseid, resource):
		if isinstance(resource, Resource):
			#if cseid not in self._db.list_collection_names():
			#	raise KeyError

			to_store = resource.toDict().copy()
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
			resource.load(result)

			if '_id' in result:
				resource.set_id(str(result['_id']))

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

	def create(self, csi, resource):

		if isinstance(resource, ContentInstance):
			ri = super().create(csi, resource)
		else:
			raise TypeError

		if hasattr(resource, 'pi') and resource.pi is not None:
			self._db[csi].update_one({'_id':ObjectId(resource.pi)},{'$set': {'m2m:cnt': {'la':ObjectId(ri)}}})

		return ri


class CSEBaseMapper(ResourceMapper):
	def __init__(self):
		super().__init__()

	def create(self, cseid, resource):
		if isinstance(resource, CSEBase):
			return super().create(cseid, resource)
		else:
			raise TypeError



		