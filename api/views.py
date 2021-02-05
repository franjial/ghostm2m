from django.http import JsonResponse
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from bson.objectid import ObjectId

import json
import datetime
import sys

from onem2m.resources import ResourcesFactory
from onem2m.types import Operation, ResponseStatusCode, ResourceType
from onem2m.primitive import ResponsePrimitive
from onem2m.mappers import MappersFactory, ResourceMapper
from onem2m.security import User

def index(request):
	return HttpResponse("hola mundo!")

@csrf_exempt
def m2mrequest(request, origin_form):
	data = json.loads(request.body)
	primitive = None


	path_items = origin_form.split('/')
	http_to = dict()
	if len(path_items)>0:
		http_to['cse-id'] = path_items[0]
		if len(path_items) > 1:
			http_to['unstructured-resource-id'] = path_items[1]
		if len(path_items) > 2:
			http_to['attr'] = path_items[2]

	else:
		return JsonResponse({'status': 0, 'info': 'error mapping path'})


	try:
		if 'm2m:rqp' in data:
			primitive = data['m2m:rqp']
	except KeyError:
		resp = ResponsePrimitive(0, ResponseStatusCode.BAD_REQUEST.value)
		return JsonResponse(resp.toDict())

	try:
		if 'fr' in primitive:
			fr = primitive['fr']
			username, pwd = fr.split(':', maxsplit=2)
			user = User(username,pwd)
			if not user.valid():
				resp = ResponsePrimitive(0, ResponseStatusCode.OPERATION_NOT_ALLOWED.value)
				return JsonResponse(resp.toDict())

	except Exception:
		resp = ResponsePrimitive(0, ResponseStatusCode.BAD_REQUEST.value)
		return JsonResponse(resp.toDict())


	# CREATE or NOTIFY
	if request.method == "POST":

		try:
			if 'op' in primitive:
				op = primitive['op']
		except KeyError:
			return JsonResponse({'status': 0, 'info': 'no operation in primitive'})

		try:
			if 'ty' in primitive:
				ty = primitive['ty']
		except KeyError:
			return JsonResponse({'status':0, 'info': 'no resourceType in request primitive'})

		if op == Operation.Create.value:
			resource = None
			try:
				if primitive['ty'] == ResourceType.AE.value:
					target_resource = http_to['cse-id']
				else:
					target_resource = http_to['unstructured-resource-id']

				if target_resource is None:
					resp = ResponsePrimitive(rsc=ResponseStatusCode.BAD_REQUEST.value)
					return JsonResponse(resp.toDict())

				pc = None
				if 'pc' in primitive:
					pc = primitive['pc']
				resource = ResourcesFactory().create(ty=primitive['ty'], pc=pc, pi=target_resource)
				mapper = MappersFactory().get(resource)
				ri = mapper.store(http_to['cse-id'], resource)
				resource.set_id(ri)
				resp = ResponsePrimitive(rsc=ResponseStatusCode.CREATED.value)
				resp.set_pc(resource.toDict())
				return JsonResponse(resp.toDict())	

			except:
				resp = ResponsePrimitive(rsc=ResponseStatusCode.BAD_REQUEST.value)
				return JsonResponse(resp.toDict())


		else:
			resp = ResponsePrimitive(rsc=ResponseStatusCode.NOT_IMPLEMENTED.value)
			return JsonResponse(resp.toDict())	

	# RETRIEVE
	elif request.method == "GET":
		try:
			try:
				if 'op' in primitive:
					op = primitive['op']
			except KeyError:
				rsp = ResponsePrimitive(rsc=ResponseStatusCode.BAD_REQUEST.value)
				return JsonResponse(rsp.toDict())

			if op == Operation.Retrieve.value:
				if 'unstructured-resource-id' in http_to:
					resource = ResourceMapper().retrieve(http_to["cse-id"], {'_id': ObjectId(http_to['unstructured-resource-id'])})
				else:
					resource = ResourceMapper().retrieve(http_to["cse-id"], {'csi': http_to['cse-id']})

				if 'attr' in http_to:
					if hasattr(resource, http_to['attr']):
						target_attr = getattr(resource, http_to['attr'])
						rsp = ResponsePrimitive(rsc=ResponseStatusCode.OK.value)
						rsp.set_pc(target_attr)
						return JsonResponse(rsp.toDict())
					else:
						rsp = ResponsePrimitive(rsc=ResponseStatusCode.NOT_FOUND.value)
						return JsonResponse(rsp.toDict())
					
				else:
					if resource is None:
						rsp = ResponsePrimitive(rsc=ResponseStatusCode.NOT_FOUND.value)
						return JsonResponse(rsp.toDict())

					rsp = ResponsePrimitive(rsc=ResponseStatusCode.OK.value)
					rsp.set_pc(resource.toDict())
					return JsonResponse(rsp.toDict())
						
			else:
				rsp = ResponsePrimitive(rsc=ResponseStatusCode.NOT_IMPLEMENTED.value)
				return JsonResponse(rsp.toDict())

		except Exception:
			rsp = ResponsePrimitive(rsc=ResponseStatusCode.INTERNAL_SERVER_ERROR.value)
			return JsonResponse(rsp.toDict())


	else:
		rsp = ResponsePrimitive(rsc=ResponseStatusCode.NOT_IMPLEMENTED.value)
		return JsonResponse(rsp.toDict())
