from errorMessages import ErrorMessages


class BadRequestException (Exception):
    def __init__(self, error_message: ErrorMessages):
        self.error_message = error_message
        super().__init__(self.error_message.value)

    def __str__(self):
        return "400 Bad Request"
        
class NotImplementedException (Exception):
    def __init__(self, message="Feature not implemented"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "501 Not Implemented"


class HTTPErrorResponse(Exception):
    def __init__(self, code, error_type,error_message: ErrorMessages):
        self.code = code
        self.error_type = error_type
        self.error_message = error_message
        # Generate the HTML content for the error page
        self.error_page = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error {self.code}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 20px;
                    text-align: center;
                }}
                h1 {{
                    font-size: 48px;
                }}
                p {{
                    font-size: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>Error {self.code}</h1>
            <p>{self.error_type}</p>
            <p>{self.error_message.value}</p>
            
        </body>
        </html>
        """
        # Construct the HTTP response
        self.response = (
                f"HTTP/1.1 {self.code} {self.error_type}\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(self.error_page.encode('utf-8'))}\r\n\r\n"
                + self.error_page
        )

    def get_response(self):
        return self.response