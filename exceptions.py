class BadRequestException (Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "400 Bad Request"
        
class NotImplementedException (Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "501 Not Implemented" 
