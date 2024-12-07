import threading, sys
from socket import *
from tcpClientHandler import TCP_client

def start_server(server_port_number = 8080):
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(("", server_port_number))
        serverSocket.listen()
        print(f"Server is running on port {server_port_number} and is ready to receive requests ^-^")

        while True:
            connectionSocket, client_address = serverSocket.accept()
            print(f"Connection with client {client_address} is established")

            client_thread = threading.Thread(target=TCP_client, args=(connectionSocket, ))
            client_thread.start()

    except Exception as e:
        print(f"Error: {e}")
        pass

if __name__ == "__main__":
    #b) Your server program should take single argument which specifies the port number.


    # do we need to specify the ranges of valid port numbers?
    server_port_number = 8080
    start_server(server_port_number)