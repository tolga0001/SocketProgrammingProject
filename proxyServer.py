import socket
import threading
from errorMessages import ErrorMessages
import sys
from exceptions import HTTPErrorResponse
from urllib.parse import urlparse
from lruCache import LRUCache

# Proxy server configuration
PROXY_HOST = '127.0.0.1'  # Localhost for the proxy
PROXY_PORT = 8888  # Port for the proxy

BUFFER_SIZE = 999999999
MAX_URI_SIZE = 9999


def extract_host_and_port(url):
    url_parts = url[7:].split("/", 1)
    host_port = url_parts[0].split(":")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) == 2 else 80
    path = "/" + url_parts[1] if len(url_parts) > 1 else "/"
    return host, port, path


def handle_https(client_socket, target_host, target_port):
    """Handle HTTPS tunneling for CONNECT requests."""
    try:
        # Establish a connection to the target host
        with socket.create_connection((target_host, target_port)) as server_socket:
            print(f"Establishing tunnel to {target_host}:{target_port}")

            # Inform the client that the tunnel is established
            client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            # Set both sockets to non-blocking mode for bidirectional tunneling
            client_socket.setblocking(False)
            server_socket.setblocking(False)

            while True:
                # Forward data from client to server
                try:
                    client_data = client_socket.recv(BUFFER_SIZE)
                    if client_data:
                        server_socket.sendall(client_data)
                    else:
                        break
                except BlockingIOError:
                    pass  # Non-blocking read, no data available

                # Forward data from server to client
                try:
                    server_data = server_socket.recv(BUFFER_SIZE)
                    if server_data:
                        client_socket.sendall(server_data)
                    else:
                        break
                except BlockingIOError:
                    pass  # Non-blocking read, no data available
    except Exception as e:
        print(f"Tunneling error: {e}")
    finally:
        client_socket.close()


def handle_client(client_socket, cache):
    """Handles communication between the client and the main server."""
    try:
        client_request = client_socket.recv(BUFFER_SIZE)
        if not client_request:
            client_socket.close()
            return

        # Parse request
        request_lines = client_request.split(b'\r\n')
        first_line = request_lines[0].decode()
        method, url, _ = first_line.split()

        # Handle HTTPS (CONNECT) requests
        if method == "CONNECT":
            hostname, port = url.split(":")
            handle_https(client_socket, hostname, int(port))
            return

        # Handle HTTP requests
        if not url.startswith("http://"):
            client_socket.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\nOnly HTTP is supported.")
            client_socket.close()
            return

        print(f"Received request from client: {client_request}\n")
        hostname, port, path = extract_host_and_port(url)

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

        # Modify the request for HTTP/1.0
        http_10_request = f"{method} {path} HTTP/1.0\r\nHost: {hostname}\r\n\r\n".encode()

        # Forward the request to the main server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_server_socket:
            main_server_socket.connect((hostname, port))
            main_server_socket.sendall(http_10_request)

            server_response = b""
            while True:
                chunk = main_server_socket.recv(BUFFER_SIZE)
                if not chunk:
                    break
                server_response += chunk

            # Cache the response
            cache.insert_into_cache(cache_key, server_response)

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
        proxy_socket.bind((hostname, port))
        proxy_socket.listen()
        print(f"Proxy server running on {hostname}:{port} with cache size {cache_size}...")

        while True:
            client_socket, client_address = proxy_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, cache))
            client_thread.start()


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            print("Usage: python proxyServer.py <port number> <cache size>")
        else:
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
