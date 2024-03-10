import xmlrpc.client
import ssl
from datetime import datetime
import base64
import getpass

try:
    # Create SSL context with TLS support for HTTPS
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # ssl_context.check_hostname=False

    # Load server's certificate for SSL verification
    ssl_context.load_verify_locations(cafile='server.crt')
    # server=xmlrpc.client.ServerProxy('https://localhost:8000', context=ssl_context)
    # ßprint(server.get_server_status())
    # Connect to the XML-RPC server using HTTPS
    server = xmlrpc.client.ServerProxy('https://localhost:8080', context=ssl_context)
    print(xmlrpc.client)
    # Call the server function to get the server status with authentication headers
    print(server.get_server_status())
except ConnectionRefusedError:
    print("Connection to the server refused. Please ensure the server is running.")
except xmlrpc.client.ProtocolError as e:
    if e.errcode == 401:
        print("Authentication failed. Please check your username and password.")
    else:
        print("An error occurred:", e)
except Exception as e:
    print("An error occurred:", e)
