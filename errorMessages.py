from enum import Enum

class ErrorMessages(Enum):
    INVALID_URL_SIZE = "Url size should be between 100 and 200000"
    INVALID_URL_SIZE_FORMAT = "Url size format should be numeric"
    NOT_IMPLEMENTED = "The request type should be get"
    INVALID_PORT_NUMBER = "Port number should be between 1024 and 65535"
    UNRECOGNIZED_METHOD = "Invalid method"
