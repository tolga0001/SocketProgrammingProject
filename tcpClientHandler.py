import os

from requestHandler import RequestHandler
from exceptions import HTTPErrorResponse


def log_message(msg_type, msg):
    print(f"{msg_type}: {msg}")


def save_html_to_disk(html_content, file_name, directory="html_files"):
    """
    Save the HTML content to a file in the specified directory.

    :param html_content: The HTML content to save.
    :param file_name: The name of the file to save the HTML content as.
    :param directory: The directory to save the file in. Defaults to 'html_files'.
    """
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Full path to the file
    file_path = os.path.join(directory, file_name)

    # Write the HTML content to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"HTML file saved: {file_path}")
def TCP_client(connection_socket):
    try:
        request = connection_socket.recv(1024).decode('utf-8')
        log_message("Received request", request.strip())
        # create web server to handle request
        # all the controllers are in the constructor. If there's an exception inside all of them are raised by HTTPErrorResponse to get handled here
        web_server = RequestHandler(request)
        html_file = web_server.generate_HTML()
        save_html_to_disk(html_file, "generated_page.html")


        # Build successful response
        #check that the html file size
        print(f"html file size is{len(html_file)} byte")
        if len(html_file) %2 == 0:
            info_header= "200 OK\r\n"
        else:
            info_header = "304 Not Modified\r\n"

        response = (
            f"HTTP/1.1 {info_header}"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(html_file.encode('utf-8'))}\r\n"
            "Connection: close\r\n\r\n"
            f"{html_file}"
        )
        print(f"response is {response}")
        connection_socket.sendall(response.encode('utf-8'))
        log_message("Response", "200 OK sent successfully")
    except HTTPErrorResponse as e:
        connection_socket.sendall(e.response.encode('utf-8'))
        log_message("HTTP Error", f"{e.code} {e.error_type} {e.error_message.value}")
    except Exception as e:
        log_message("Error", f"Unexpected error: {str(e)}")
    finally:
        connection_socket.close()