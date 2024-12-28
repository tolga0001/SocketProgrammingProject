import socket
import threading
from errorMessages import ErrorMessages
import sys
from exceptions import HTTPErrorResponse
from urllib.parse import urlparse
from lruCache import LRUCache
import re
# Proxy server configuration
PROXY_HOST = '127.0.0.1'  # Localhost for the proxy
PROXY_PORT = 8888         # Port for the proxy

BUFFER_SIZE = 999999999
MAX_URI_SIZE = 9999

def sanitize_key(key):
    return re.sub(r'[<>:"/\\|?*]', '_', key)

def extract_host_and_port(url):
    # ex GET http://example.com:8080/path/to/resource HTTP/1.1
    # Parse the host and path
    url_parts = url[7:].split("/", 1)
    host_port = url_parts[0].split(":")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) == 2 else 80
    path = "/" + url_parts[1] if len(url_parts) > 1 else "/"
    return host, port, path

def handle_client(client_socket, cache):
    """Handles communication between the client and the main server."""
    try:
        # Receive the client's request
        client_request = client_socket.recv(BUFFER_SIZE)
        if not client_request:
            client_socket.close()
            return
        
        # Extract the host and port from the request headers
        request_lines = client_request.split(b'\r\n')
        first_line = request_lines[0].decode()
        method, url, _ = first_line.split()
        # Only handle HTTP requests (not HTTPS)
        if not url.startswith("http://"):
            client_socket.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\nOnly HTTP is supported.")
            client_socket.close()
            return
        print(f"Received request from client: {client_request}\n")
        hostname, port, path = extract_host_and_port(url)
        print(path)
        if hostname== 'localhost' and int(path[1:]) > MAX_URI_SIZE:
            error_string = ErrorMessages.REQUEST_URI_TOO_LONG
            error_response = (
                b"HTTP/1.1 414 Request-URI Too Long\r\n"
                b"Content-Type: text/plain\r\n\r\n" +
                b"Request-URI Too Long. Please check the URL and try again."
            )

            client_socket.sendall(error_response)
            raise HTTPErrorResponse(414, "Request-URI Too Long", ErrorMessages.REQUEST_URI_TOO_LONG)
        cache_key =  sanitize_key(f"{hostname}_{port}_{path.replace('/', '_')}")
        cached_response = cache.retreive_from_cache(cache_key)
        if cached_response:
            print(f"Cache hit: {cache_key}")
            print(cached_response)
            client_socket.sendall(cached_response)
            client_socket.close()
            return
        print(f"Cache miss: {cache_key}. Forwarding request to {hostname}:{port}")
        # Check if the request is for the local server
        if hostname == "localhost":
            target_host = "127.0.0.1"
        else:
            target_host = hostname
        # Modify the request to use HTTP/1.0
        http_10_request = f"{method} {path} HTTP/1.0\r\nHost: {target_host}\r\n\r\n"
        http_10_request = http_10_request.encode()
        # Forward the request to the main server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_server_socket:
            try:
                main_server_socket.connect((target_host, port))
                if hostname != "localhost":
                    client_request = client_request.replace(url.encode(), path.encode())
                main_server_socket.sendall(http_10_request)
                # Receive the response from the main server
                server_response = b""
                while True:
                    chunk = main_server_socket.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    server_response += chunk
                # add the server response to the cache
                cache.insert_into_cache(cache_key, server_response)
                # Print the server response for debugging purposes
                try:
                    print(f"Server response:\n{server_response.decode()}\n")  # Decode if it's text
                except UnicodeDecodeError:
                    print(f"Server response (raw bytes): {server_response}\n")  # Print raw bytes if decoding fails
            except (ConnectionRefusedError, socket.gaierror, TimeoutError):
                # Handle connection errors by returning a 404 Not Found response
                error_response = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n"+"Web Server is not running."
                client_socket.sendall(error_response)
                print(f"Error: Could not connect to {target_host}:{port}. Returned 404 to client.")
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
                error_response = (
                    b"HTTP/1.1 400 Bad Reqeuest\r\n"
                    b"Content-Type: text/plain\r\n\r\n"+
                    b"Port number should be between 1024 and 65535"
                )
                # Create a fake socket to send the error response to the client
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as fake_client_socket:
                    fake_client_socket.connect((PROXY_HOST, port_number))
                    fake_client_socket.sendall(error_response)
                raise HTTPErrorResponse(400, "Bad Request", ErrorMessages.INVALID_PORT_NUMBER)
    except HTTPErrorResponse as e:
        print("HTTP Error:", f"{e.code} {e.error_type} {e.error_message.value}")
    except ValueError:
        print("Error: Invalid port number format. Please provide an integer.")
    except Exception as e:
        print("Unexpected error:", str(e))