import xmlrpc.client
import ssl
from datetime import datetime
import base64
import getpass

def connect_server(username, password):
    try:
        # Create SSL context with TLS support for HTTPS
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        #ssl_context.check_hostname=False

        # Load server's certificate for SSL verification
        ssl_context.load_verify_locations(cafile='server.crt')

        # Connect to the XML-RPC server using HTTPS
        server = xmlrpc.client.ServerProxy(f'https://{username}:{password}@localhost:8080', context=ssl_context)
        # Call get_server_status  function to get the server status with authentication headers
        print(server.get_server_status())
        return server
    except ConnectionRefusedError:
        print("Connection to the server refused. Please ensure the server is running.")
        return False
    except xmlrpc.client.ProtocolError as e:
        if e.errcode == 401:
            print("Authentication failed. Please check your username and password.")
        else:
            print("An error occurred:", e)
        return False
    except Exception as e:
        print("An error occurred:", e)
        return False


def update_topic():
    try:
        # Create SSL context with TLS support for HTTPS
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

        # Load server's certificate for SSL verification
        ssl_context.load_verify_locations(cafile='server.crt')

        # Connect to the XML-RPC server using HTTPS
        server=connect_server(username, password)
        if server is False:
            print("Exiting...")
        else:
            # Get the topic, note, and text from the user
            topic = input("Enter topic: ")
            note = input("Enter note: ")
            text = input("Enter text: ")

            # Generate timestamp
            timestamp = datetime.now().strftime("%m/%d/%y - %H:%M:%S")
            # Call the server function to update the database with authentication headers
            result = server.update_database(topic, note, text, timestamp)
            print(result)

    except Exception as e:
        print("An error occurred:", e)


def get_topic():
    try:
        # Create SSL context with TLS support for HTTPS
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

        # Load server's certificate for SSL verification
        ssl_context.load_verify_locations(cafile='server.crt')

        # Connect to the XML-RPC server using HTTPS
        server = connect_server(username, password)
        # Get the topic from the user
        if server is False:
            print("Exiting...")
        else:
            topic = input("Enter topic: ")

            # Call the server function to get XML content for the given topic with authentication headers
            xml_content = server.get_xml_content_by_topic(topic)

            # Print the XML content
            print("XML Content for topic", topic + ":")
            print(xml_content)
    except Exception as e:
        print("An error occurred:", e)
def wiki_search():
    try:
        # Create SSL context with TLS support for HTTPS
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

        # Load server's certificate for SSL verification
        ssl_context.load_verify_locations(cafile='server.crt')

        # Connect to the XML-RPC server using HTTPS
        server = connect_server(username, password)
        if server is False:
            print("Exiting...")
        else:
            # Get the topic and search from the user
            # topic = input("Enter topic: ")
            topic_search = input("Enter Search: ")
            # Call the server function to get Wiki content for the given topic with authentication headers
            wiki_search_return = server.search_wiki_content(topic_search)
            # Print the Search content
            print("Wiki Return for topic", topic_search + ":")
            if wiki_search_return is not None:
                print(wiki_search_return)
                wiki_search_append = server.topic_wiki_update(topic_search, wiki_search_return)
                print(wiki_search_append)
    except Exception as e:
        print("An error occurred:", e)

# Get username and password from user
print("Please ente your user name and password.")
username = input("Enter username: ")
password = getpass.getpass(prompt="Enter password: ")

# Connect to the server and execute user's request
if connect_server(username, password):
    while not False:
        choice = input("Menu (Type and Press Enter):  1 for Update Topic, 2 for Get Topic, 3 for Wiki Search, "
                       "4 for Exit: ")
        if choice == '1':
            update_topic()
        elif choice == '2':
            get_topic()
        elif choice == '3':
            wiki_search()
        elif choice == '4':
            print("Exiting.....")
            break
        else:
            print("Invalid choice. Please select again.")
else:
    print("Cannot proceed with the request. Please check the error message above.")
