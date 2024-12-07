from pickletools import bytes_types
from requestHandler import RequestHandler

from exceptions import HTTPErrorResponse


def log_message(msg_type, msg):
    print(f"{msg_type}: {msg}")

def TCP_client(connection_socket):
    try:

        request = connection_socket.recv(1024).decode('utf-8')
        log_message("Received request", request.strip())
        # create web server to handle request
        # all the controllers are in the constructor. If there's an exception inside all of them are raised by HTTPErrorResponse to get handled here
        web_server = RequestHandler(request)
        html_file = web_server.generate_HTML()
        # Send a response back to the client
        response = (
            "HTTP/1.1 200 OK\n"
            "Content-Type: text/html\n"
            "Content-Length: "+str(len(html_file.encode('utf-8')))+"\n\n"
            +html_file
        )
        connection_socket.sendall(response.encode('utf-8'))
        print("Response sent.")
        print("--------------------------------------------------")
    except HTTPErrorResponse as e:
        connection_socket.sendall(e.response.encode('utf-8'))
        pass
    except Exception as e:
        log_message("Error", f"An error occurred: {str(e)}")
    finally:
        connection_socket.close()