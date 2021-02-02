from onem2m.util import Singleton
from pymongo import MongoClient
from django.conf import settings

class DBConnection(metaclass=Singleton):
	def __init__(self):
		self.db_client = MongoClient(settings.GHOSTM2M["mongodb"])
		self.db = self.db_client[settings.GHOSTM2M["dbname"]]

	def get_db(self, env='production'):
		return self.db

	def set_db(self, db):
		self.db = self.db_client[db]
		self.active_db = db
