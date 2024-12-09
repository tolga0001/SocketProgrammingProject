import threading, sys
from socket import *

from errorMessages import ErrorMessages
from tcpClientHandler import TCP_client
from exceptions import HTTPErrorResponse

def start_server(server_port_number = 8080):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", server_port_number))
    serverSocket.listen()
    print(f"Server is running on port {server_port_number} and is ready to receive requests ^-^")

    while True:
        connectionSocket, client_address = serverSocket.accept()
        print(f"Connection with client {client_address} is established")

        client_thread = threading.Thread(target=TCP_client, args=(connectionSocket, ))
        client_thread.start()

if __name__ == "__main__":
    #b) Your server program should take single argument which specifies the port number.

    try:
        # Ensure the port number is passed as an argument
        if len(sys.argv) != 2:
            print("Usage: python mainServer.py <port number>")
        else:
            # Check if the port number is within the valid range (1024–65535)
            port_number = int(sys.argv[1])
            if 1024 <= port_number <= 65535:
                start_server(port_number)
            else:
                raise HTTPErrorResponse(400, "Bad Request", ErrorMessages.INVALID_PORT_NUMBER)
    except HTTPErrorResponse as e:
        print("HTTP Error:", f"{e.code} {e.error_type} {e.error_message}")
    except ValueError:
        print("Error: Invalid port number format. Please provide an integer.")
    except Exception as e:
        print("Unexpected error:", str(e))