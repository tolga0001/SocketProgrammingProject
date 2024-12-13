import socket
import threading
from errorMessages import ErrorMessages
import sys
from exceptions import HTTPErrorResponse
from urllib.parse import urlparse
from lruCache import LRUCache

# Proxy server configuration
PROXY_HOST = '127.0.0.1'  # Localhost for the proxy
PROXY_PORT = 8888         # Port for the proxy
BUFFER_SIZE = 4096
MAX_URI_SIZE = 9999

def extract_host_and_port(request_line):
    # ex GET http://example.com:8080/path/to/resource HTTP/1.1
    parsed_url = urlparse(request_line.split()[1]) 
    hostname = parsed_url.hostname
    port = parsed_url.port if parsed_url.port else (443 if parsed_url.scheme == "https" else 80)
    path = parsed_url.path if parsed_url.path else "/"
    return hostname, port, path


def handle_client(client_socket, cache):
    """Handles communication between the client and the main server."""
    try:
        # Receive the client's request
        client_request = client_socket.recv(BUFFER_SIZE).decode()
        if not client_request:
            client_socket.close()
            return


        print(f"Received request from client: {client_request}\n")
        client_request_splitted = client_request.splitlines()[0]
        hostname, port, path = extract_host_and_port(client_request_splitted)

        if len(path) > MAX_URI_SIZE:
            raise HTTPErrorResponse(414, "Request-URI Too Long", ErrorMessages.INVALID_URL_SIZE)
        
        cache_key = f"{hostname}_{port}_{path.replace('/', '_')}"
        cached_response = cache.retreive_from_cache(cache_key)
        if cached_response:
            print(f"Cache hit: {cache_key}")
            client_socket.sendall(cached_response)
            client_socket.close()
            return
        
        print(f"Cache miss: {cache_key}. Forwarding request to {hostname}:{port}")

        # Forward the request to the main server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_server_socket:
            main_server_socket.connect((hostname, port))
            main_server_socket.sendall(client_request.encode())
        
            # Receive the response from the main server
            server_response = main_server_socket.recv(BUFFER_SIZE)
            
            # add the server response to the cache
            cache.insert_into_cache(cache_key, server_response)

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

def start_proxy(port, hostname, cache_size):
    """Starts the proxy server."""
    cache = LRUCache(cache_size)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
        # proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) what's that?
        proxy_socket.bind((hostname, port))
        proxy_socket.listen()
        print(f"Proxy server running on {hostname}:{port} with cache size {cache_size}...")

        while True:
            #print("Its waiting to take request...")
            client_socket, client_address = proxy_socket.accept()
            #print(f"Accepted connection from {client_address}")
            # Handle the client request in a new thread
            client_thread = threading.Thread(target=handle_client, args=(client_socket, cache))
            client_thread.start()

if __name__ == "__main__":
    #b) Your server program should take single argument which specifies the port number.
    try:
        # Ensure the port number is passed as an argument
        if len(sys.argv) != 3:
            print("Usage: python proxyServer.py <port number> <cache size>")
        else:
            # Check if the port number is within the valid range (1024–65535)
            port_number = int(sys.argv[1])
            cache_size = int(sys.argv[2])

            if 1024 <= port_number <= 65535:
                start_proxy(port_number, PROXY_HOST, cache_size)
            else:
                raise HTTPErrorResponse(400, "Bad Request", ErrorMessages.INVALID_PORT_NUMBER)
    except HTTPErrorResponse as e:
        print("HTTP Error:", f"{e.code} {e.error_type} {e.error_message.value}")
    except ValueError:
        print("Error: Invalid port number format. Please provide an integer.")
    except Exception as e:
        print("Unexpected error:", str(e))
