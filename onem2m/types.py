from enum import Enum
class Operation(Enum):
	Create = 1
	Retrieve = 2
	Update = 3
	Delete = 4
	Notify = 5

class ResourceType(Enum):
	container = 3
	contentInstance = 4
	AE = 1
	CSEBase = 5

class cseTypeID(Enum):
	IN_CSE = 1
	MN_CSE = 2
	ASN_CSE = 3

class ResponseStatusCode(Enum):
	ACCEPTED = 1000
	OK = 2000
	CREATED = 2001
	DELETED = 2002
	UPDATED = 2004
	BAD_REQUEST = 4000
	RELEASE_VERSION_NOT_SUPPORTED = 4001
	NOT_FOUND = 4004
	OPERATION_NOT_ALLOWED = 4005
	INTERNAL_SERVER_ERROR = 5000
	NOT_IMPLEMENTED = 5001
	#todo all errors