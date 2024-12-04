from exceptions import BadRequestException, NotImplementedException
from socket import *

class WebServer:
    def __init__(self, URI) -> None:
        try:
            self.URI = URI
            self.is_request_message_valid(self.URI)

            URI_size = self.extract_URI_size(self.URI)
            if self.is_URI_size_valid(URI_size):
                self.URI_size = URI_size
                print(f"URI = {self.URI}, size = {self.URI_size}")
            else:
                raise BadRequestException()
            
        except NotImplementedException:
            self.send_error_response(501, "Not Implemented")
        except BadRequestException:
            self.send_error_response(400, "Bad Request")
    
    def is_URI_size_valid(self, URI_size) -> bool:
        return 100 <= URI_size <= 20000
    
    def extract_URI_size(self, URI) -> int:
        URI_size = URI.split(" ")[1][1:]
        print(URI_size)
        if URI_size.isnumeric():
            return int(URI_size)
        else:
            raise BadRequestException()
        
    def is_request_message_valid(self, URI):
        URI_message = URI.split(" ")[0]
        if URI_message != "GET":
            raise NotImplementedException()
        else:
            return True

    # display error on browser    
    def send_error_response(self, code, message):
        pass

    def generate_HTML(self):
        pass 

