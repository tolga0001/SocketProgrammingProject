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
BUFFER_SIZE = 8192  # Daha uygun bir buffer boyutu
MAX_URI_SIZE = 9999

def sanitize_key(key):
    return re.sub(r'[<>:"/\\|?*]', '_', key)

def extract_host_and_port(url, headers, localhost_port):
    if url.startswith("http://"):
        # Absolute URL (proxy açıkken)
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 80  # Varsayılan HTTP portu
        path = parsed_url.path if parsed_url.path else "/"
    else:
        # Relative URL (proxy kapalıyken)
        if "Host" in headers:
            host_header = headers["Host"]
            if ":" in host_header:
                host, port = host_header.split(":")
                port = int(port)
            else:
                host = host_header
                port = 80  
        else:
           
            host = "localhost"
            port = localhost_port
        path = url if url.startswith("/") else f"/{url}"

    return host, port, path


def parse_headers(request_lines):

    headers = {}
    for line in request_lines[1:]:  
        if not line.strip():
            break
        key, value = line.decode().split(":", 1)
        headers[key.strip()] = value.strip()
    return headers

def handle_client(client_socket, cache, proxy_port, localhost_port):
    """Handles communication between the client and the main server."""
    try:
        client_request = client_socket.recv(BUFFER_SIZE)
        if not client_request:
            client_socket.close()
            return
        
        request_lines = client_request.split(b'\r\n')
        first_line = request_lines[0].decode()
        method, url, _ = first_line.split()
        headers = parse_headers(request_lines)

        hostname, port, path = extract_host_and_port(url, headers, localhost_port)

        

        cache_key = sanitize_key(f"{hostname}{port}{path.replace('/', '_')}")
        cached_response = cache.retreive_from_cache(cache_key)
        
        if cached_response:
            print(f"Cache hit: {cache_key}")
            print(cached_response)

            client_socket.sendall(cached_response)
            client_socket.close()
            return
        print(f"Cache miss: {cache_key}. Forwarding request to {hostname}:{port}")
        
        if hostname == "localhost" and port == proxy_port:
            port = localhost_port
        target_host = "127.0.0.1" if hostname == "localhost" else hostname
        http_10_request = f"{method} {path} HTTP/1.0\r\nHost: {target_host}\r\n\r\n".encode()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_server_socket:
            main_server_socket.connect((target_host, port))
            main_server_socket.sendall(http_10_request)

            server_response = b""
            while True:
                chunk = main_server_socket.recv(BUFFER_SIZE)
                if not chunk:
                    break
                server_response += chunk

            cache.insert_into_cache(cache_key, server_response)
            client_socket.sendall(server_response)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def start_proxy(port, hostname, cache_size, localhost_port):
    """Starts the proxy server."""
    cache = LRUCache(cache_size)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
        proxy_socket.bind((hostname, port))
        proxy_socket.listen()
        print(f"Proxy server running on {hostname}:{port} with cache size {cache_size}...")
        print(f"Forwarding to localhost on port {localhost_port}...")

        while True:
            client_socket, client_address = proxy_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, cache, port, localhost_port))
            client_thread.start()

if __name__ == "__main__":
    try:
        # Argüman sayısı kontrolü (2 veya 3 olabilir)
        if len(sys.argv) < 3 or len(sys.argv) > 4:
            print("Usage: python proxyServer.py <proxy port> <cache size> [<localhost port>]")
        else:
            # Proxy port ve cache size değerlerini oku
            proxy_port = int(sys.argv[1])
            cache_size = int(sys.argv[2])

            # Varsayılan localhost portu
            localhost_port = 8080  # Varsayılan değer

            # Eğer üçüncü bir argüman girildiyse onu localhost_port olarak al
            if len(sys.argv) == 4:
                localhost_port = int(sys.argv[3])

            # Port numaralarının geçerli aralıkta olup olmadığını kontrol et
            if not (1024 <= proxy_port <= 65535):
                print("Error: Proxy port must be in the range 1024–65535")
            elif not (1024 <= localhost_port <= 65535):
                print("Error: Localhost port must be in the range 1024–65535")
            else:
                print(f"Starting proxy on port {proxy_port} with cache size {cache_size}...")
                print(f"Forwarding requests to localhost:{localhost_port}")
                # Proxy sunucusunu başlat
                start_proxy(proxy_port, PROXY_HOST, cache_size, localhost_port)
    except ValueError:
        print("Error: Invalid port or cache size. Please provide integers.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
