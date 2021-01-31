from onem2m.types import ResponseStatusCode

class ResponsePrimitive:
	def __init__(self, ri=0, rsc=ResponseStatusCode.OK.value, rvi=2):
		self.rsc = rsc
		self.ri = ri
		self.rvi = rvi

		self.__dict = {'m2m:rsp': {
			'rsc': self.rsc,
			'ri':  self.ri,
			'rvi': self.rvi
		}}

	def set_pc(self,pc):
		self.__pc = pc
		self.__dict['m2m:rsp']['pc'] = pc

	def set_rvi(self,rvi):
		self.__rvi = rvi
		self.__dict['m2m:rsp']['rvi'] = rvi

	def set_ri(self,ri):
		self.__ri = ri
		self.__dict['m2m:rsp']['ri'] = ri

	def set_rsc(self,rsc):
		self.__rsc = rsc
		self.__dict['m2m:rsp']['rsc'] = rsc

	def toDict(self):
		return self.__dict