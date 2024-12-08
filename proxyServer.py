import socket
import threading
from tcpClientHandler import TCP_client
import sys
from exceptions import HTTPErrorResponse

# Proxy server configuration
PROXY_HOST = '127.0.0.1'  # Localhost for the proxy
PROXY_PORT = 8888         # Port for the proxy


def handle_client(client_socket, main_server_port):
    """Handles communication between the client and the main server."""
    try:
        # Receive the client's request
        client_request = client_socket.recv(4096).decode()
        if not client_request:
            return
        
        print(f"Received request from client:\n{client_request}\n")

        # Parse the request (omitted for brevity, refer to the full code above)

        # Forward the request to the main server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_server_socket:
            main_server_socket.connect(('localhost', main_server_port))
            main_server_socket.sendall(client_request.encode())
            print("main port: ", main_server_port)
            # Receive the response from the main server
            server_response = main_server_socket.recv(4096)
            
            # Print the server response for debugging purposes
            try:
                print(f"Server response:\n{server_response.decode()}\n")  # Decode if it's text
            except UnicodeDecodeError:
                print(f"Server response (raw bytes): {server_response}\n")  # Print raw bytes if decoding fails

            # Send the response back to the client
            client_socket.sendall(server_response)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def start_proxy(main_server_port):
    """Starts the proxy server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
        proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_socket.bind((PROXY_HOST, PROXY_PORT))
        proxy_socket.listen(5)
        print(f"Proxy server running on {PROXY_HOST}:{PROXY_PORT}...")

        while True:
            client_socket, client_address = proxy_socket.accept()
            print(f"Accepted connection from {client_address}")
            # Handle the client request in a new thread
            client_thread = threading.Thread(target=handle_client, args=(client_socket, main_server_port))
            client_thread.start()



if __name__ == "__main__":
    #b) Your server program should take single argument which specifies the port number.
    if len(sys.argv) != 2:
        print("Usage: python proxyServer.py <port number>")
        sys.exit(1)

    # it's common to use ports in the registered range (1024–65535) to avoid conflicts with well-known ports
    if 1024 <= int(sys.argv[1]) <= 65535:
        server_port_number = int(sys.argv[1])
        start_proxy(server_port_number)
    else:
        raise HTTPErrorResponse(400, "Bad Request")