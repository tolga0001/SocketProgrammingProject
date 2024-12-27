from errorMessages import ErrorMessages
from exceptions import BadRequestException, NotImplementedException, HTTPErrorResponse

recognized_methods = ['POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'TRACE', 'CONNECT']
class RequestHandler:
    def __init__(self, URI) -> None:
        try:
            self.URI = URI
            self.is_request_message_valid(self.URI)

            URI_size = self.extract_URI_size(self.URI)
            if self.is_URI_size_valid(URI_size):
                self.URI_size = URI_size
            else:

                raise BadRequestException(ErrorMessages.INVALID_URL_SIZE)
            
        except NotImplementedException:
            self.raise_http_error(501, "Not Implemented",ErrorMessages.NOT_IMPLEMENTED)
        except BadRequestException as e:
            #print("21")
            self.raise_http_error(400, "Bad Request", e.error_message)
    
    def is_URI_size_valid(self, URI_size) -> bool:
        return 100 <= URI_size <= 20000
    
    def extract_URI_size(self, URI) -> int:
        if 'http' in URI:
            URI_size = URI.split(" ")[1].split("/")[3]
        else:
            URI_size = URI.split(" ")[1][1:]

        if URI_size.isnumeric():
            return int(URI_size)
        else:
            raise BadRequestException(ErrorMessages.INVALID_URL_SIZE_FORMAT)
        
    def is_request_message_valid(self, URI):
        URI_message = URI.split(" ")[0]
        if URI_message != "GET" and URI_message in recognized_methods:
            raise NotImplementedException()
        elif URI_message != "GET" and URI_message not in recognized_methods:
            raise BadRequestException(ErrorMessages.UNRECOGNIZED_METHOD)
        else:
            return True

    def raise_http_error(self, code, error_type, error_message):
        #print(f"Error {code}: {message}")
        raise HTTPErrorResponse(code, error_type,error_message)  # Raising the response to be handled by the TCP client

    def generate_HTML(self):
        header = "<HTML>\n<HEAD>\n<TITLE>Computer Networks Project</TITLE>\n</HEAD>\n<BODY>\n"
        footer = "</BODY>\n</HTML>\n"
        filler = "A" * (self.URI_size - len(header + footer))
        print(f"LENGTH IS ----------- {len(header+footer)}")
        return header + filler[:self.URI_size - len(header + footer)] + footer



