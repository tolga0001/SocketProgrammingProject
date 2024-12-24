import socket
import threading
from exceptions import HTTPErrorResponse
from lruCache import LRUCache
from errorMessages import ErrorMessages

# Proxy server configuration
PROXY_HOST = '127.0.0.1'  # Localhost
PROXY_PORT = 8888         # Port for the proxy
BUFFER_SIZE = 4096
MAX_URI_SIZE = 9999
LOCAL_SERVER_PORT = 8080  # Local server port
CACHE_SIZE = 30

def handle_client(client_socket, cache):
    """Handles the communication between the client and the web server."""
    try:
        # Receive the client's request
        request = client_socket.recv(BUFFER_SIZE)
        if not request:
            client_socket.close()
            return

        # Extract the host and port from the request headers
        request_lines = request.split(b'\r\n')
        first_line = request_lines[0].decode()
        method, url, _ = first_line.split()

        # Only handle HTTP requests (not HTTPS)
        if not url.startswith("http://"):
            client_socket.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\nOnly HTTP is supported.")
            client_socket.close()
            return

        # Parse the host and path
        url_parts = url[7:].split("/", 1)
        host_port = url_parts[0].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) == 2 else 80
        path = "/" + url_parts[1] if len(url_parts) > 1 else "/"


        if len(path) > MAX_URI_SIZE:
            raise HTTPErrorResponse(414, "Request-URI Too Long", ErrorMessages.INVALID_URL_SIZE)
        
        cache_key = f"{host}_{port}_{path.replace('/', '_')}"
        cached_response = cache.retreive_from_cache(cache_key)
        if cached_response:
            print(f"Cache hit: {cache_key}")
            client_socket.sendall(cached_response)
            client_socket.close()
            return
        
        print(f"Cache miss: {cache_key}. Forwarding request to {host}:{port}")

        # Check if the request is for the local server
        if host == "localhost" and port == LOCAL_SERVER_PORT:
            target_host = "127.0.0.1"
            target_port = LOCAL_SERVER_PORT
        else:
            target_host = host
            target_port = port

        # Forward the request to the target server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as target_socket:
            target_socket.connect((target_host, target_port))
            # Rewrite the request line with the correct path if routing externally
            if host != "localhost" or port != LOCAL_SERVER_PORT:
                request = request.replace(url.encode(), path.encode())
            target_socket.sendall(request)

            # Receive the response from the target server
            while True:
                response = target_socket.recv(BUFFER_SIZE)
                if not response:
                    break
                # Send the response back to the client
                client_socket.sendall(response)

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()


def start_proxy():
    cache = LRUCache(CACHE_SIZE)
    """Starts the proxy server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
        proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_socket.bind((PROXY_HOST, PROXY_PORT))
        proxy_socket.listen()
        print(f"Proxy server running on {PROXY_HOST}:{PROXY_PORT}...")

        while True:
            client_socket, client_address = proxy_socket.accept()
            print(f"Accepted connection from {client_address}")
            # Handle each client request in a separate thread
            client_thread = threading.Thread(target=handle_client, args=(client_socket, cache))
            client_thread.start()


if __name__ == "__main__":
    start_proxy()
