from exceptions import BadRequestException, NotImplementedException, HTTPErrorResponse
from socket import *

class RequestHandler:
    def __init__(self, URI) -> None:
        try:
            self.URI = URI
            self.is_request_message_valid(self.URI)

            URI_size = self.extract_URI_size(self.URI)
            if self.is_URI_size_valid(URI_size):
                self.URI_size = URI_size
               # print(f"URI = {self.URI}, size = {self.URI_size}")
            else:
                #print('satır 21')
                raise BadRequestException()
            
        except NotImplementedException:
            self.raise_http_error( 501, "Not Implemented")
        except BadRequestException:
            #print("21")
            self.raise_http_error(400, "Bad Request")
    
    def is_URI_size_valid(self, URI_size) -> bool:
        return 100 <= URI_size <= 20000
    
    def extract_URI_size(self, URI) -> int:
        URI_size = URI.split(" ")[1][1:]
        #print(URI)
        if URI_size.isnumeric():
            return int(URI_size)
        else:
            #print("33")
            raise BadRequestException()
        
    def is_request_message_valid(self, URI):
        URI_message = URI.split(" ")[0]
        if URI_message != "GET":
            raise NotImplementedException()
        else:
            return True

    def raise_http_error(self,code, message):
        #print(f"Error {code}: {message}")
        raise HTTPErrorResponse(code, message)  # Raising the response to be handled by the TCP client

    def generate_HTML(self):
        header = "<HTML>\n<HEAD>\n<TITLE>Computer Networks Project</TITLE>\n</HEAD>\n<BODY>\n"
        footer = "</BODY>\n</HTML>\n"
        filler = "A" * (self.URI_size - len(header + footer))
        print(f"LENGTH IS ----------- {len(header+footer)}")
        return header + filler[:self.URI_size - len(header + footer)] + footer



