import threading, sys
from socket import *
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
    if len(sys.argv) != 2:
        print("Usage: python mainServer.py <port number>")
        sys.exit(1)

    # it's common to use ports in the registered range (1024–65535) to avoid conflicts with well-known ports
    if 1024 <= int(sys.argv[1]) <= 65535:
        server_port_number = int(sys.argv[1])
        start_server(server_port_number)
    else:
        raise HTTPErrorResponse(400, "Bad Request")