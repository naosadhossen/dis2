import xmlrpc.server
import xml.etree.ElementTree as ET
from datetime import datetime
import ssl
from xmlrpc.server import SimpleXMLRPCRequestHandler
from base64 import b64decode
import requests
import xml.dom.minidom


# Load XML database
tree = ET.parse('DB.xml')
root = tree.getroot()

# Username and password for authentication
USERNAME = "me"
PASSWORD = "me"

# Function to check server status
def get_server_status():
    return "Welcome to XML-RPC Server."

# Function to authenticate user
def authenticate(username, password):
    return username == USERNAME and password == PASSWORD

# Function to update XML database
def update_database(topic, note, text, timestamp):
    try:
        # Check if topic exists
        topic_element = root.find(f'.//topic[@name="{topic}"]')
        if topic_element is None:
            # Create new topic if not exists
            topic_element = ET.SubElement(root, 'topic', {'name': topic})
        # Append note to the topic
        note_element = ET.SubElement(topic_element, 'note', {'name': note})
        text_element = ET.SubElement(note_element, 'text')
        text_element.text = text
        timestamp_element = ET.SubElement(note_element, 'timestamp')
        timestamp_element.text = timestamp

        # Write changes back to the XML file
        # tree.write('DB.xml')
        # Write changes back to the XML file
        xml_str = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
        with open('DB.xml', 'w') as f:
            f.write(xml_str)

        return "Data successfully updated on the server."
    except Exception as e:
        print("An error occurred:", e)
        return e


# Function to retrieve XML content based on topic
def get_xml_content_by_topic(topic):
    try:
        # Find the topic element
        topic_element = root.find(f'.//topic[@name="{topic}"]')
        if topic_element is not None:
            # Serialize XML data to string
            xml_string = ET.tostring(topic_element, encoding='utf-8').decode()
            return xml_string
        else:
            return "Topic not found in the database."

    except Exception as e:
        print("An error occurred:", e)
        return e

def search_wiki_content(search):
    try:
        wiki = requests.Session()
        URL = "https://en.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "opensearch",
            "namespace": "0",
            "search": search,
            "limit": "5",
            "format": "json"
        }
        wiki_return = wiki.get(url=URL, params=PARAMS, timeout=30)
        wiki_search_return = wiki_return.json()

        # Extract and return all URLs from the JSON response as a single string
        if len(wiki_search_return) > 3:
            urls = '\n'.join(wiki_search_return[3])  # Join URLs with newline
            return urls
        else:
            return "No URLs found for the search query."

    except Exception as e:
        print("An error occurred:", e)
        return e

def topic_wiki_update(topic,searchresult):
    try:
        # update wiki search return in Topic
        print("Topic:", topic)
        print("Search Result:", searchresult)
        topic_element = root.find(f'.//topic[@name="{topic}"]')
        if topic_element is None:
            # Create new topic if not exists
            topic_element = ET.SubElement(root, 'topic', {'name': topic})
        # Append Search Result to Topic in WikiSearch
        wiki_element = ET.SubElement(topic_element, 'WikiSearch')
        print(searchresult)
        wiki_element.text=searchresult
        timestamp = datetime.now().strftime("%m/%d/%y - %H:%M:%S")
        timestamp_element = ET.SubElement(wiki_element, 'timestamp')
        timestamp_element.text = timestamp

        # Write changes back to the XML file
        # tree.write('DB.xml')
        xml_str = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
        with open('DB.xml', 'w') as f:
            f.write(xml_str)

        return "Wiki Search successfully updated on the server."

    except Exception as e:
        print("An error occurred:", e)
        return e


# Custom request handler to access request headers and handle authentication
class CustomRequestHandler(SimpleXMLRPCRequestHandler):
    # Check if the connection is over HTTPS
    print("I am here in CustomRequestHandler")
    def authentication(self, headers):
        print("I am here in authenticate")
        #self.send_response(300,'Authentication Starts...')
        try:
            (basic, _, encoded) = headers.get('Authorization').partition(' ')
        except Exception as e:
            self.send_response(800, 'No credential is provided by Client- Refusing Connection:' + str(e))
            print("No credential is provided by Client- Refusing Connection", e)
            return 0
        else:
            print("Credential is provided by Client- Authentication in Progress")
            # Client authentication
            (basic, _, encoded) = headers.get('Authorization').partition(' ')
            assert basic == 'Basic', 'Only basic authentication supported'
            #    Encoded portion of the header is a string
            #    Need to convert to bytestring
            encodedByteString = encoded.encode()
            #    Decode Base64 byte String to a decoded Byte String
            decodedBytes = b64decode(encodedByteString)
            #    Convert from byte string to a regular String
            decodedString = decodedBytes.decode()
            #    Get the username and password from the string
            (username, _, password) = decodedString.partition(':')
            #    Check that username and password match internal global dictionary
            print ("User: %s" % username)
            if username == USERNAME and password == PASSWORD:
                print("Credential is provided by Client- Authentication Successful")
                return 1
            else:
                print("Credential is provided by Client- Authentication Failed")
                return 0


    def parse_request(self):
        try:
            if SimpleXMLRPCRequestHandler.parse_request(self):
                print("I am here in parse_request")
                print(self.headers)
                is_https = self.connection.context is not None
                if is_https:
                    print("Client is connecting over encrypted connection (HTTPS).")
                    # next we authenticate
                    if self.authentication(self.headers):
                        self.send_response(200, 'Authentication Successful')
                        return True
                    else:
                        # if authentication fails, send 401 error code to client
                        self.send_error(401)
                else:
                    print("Client is not connecting over encrypted connection (HTTP).")
            return False

        except Exception as e:
            print("An error occurred:", e)
            return False



# Create SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

# Load server's certificate and key for SSL/TLS encryption
ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key')

# Create XML-RPC server with custom request handler
server = xmlrpc.server.SimpleXMLRPCServer(('localhost', 8080),
                                          logRequests=True,
                                          allow_none=True,
                                          requestHandler=CustomRequestHandler)

# Wrap the server socket with SSL/TLS encryption
server.socket = ssl_context.wrap_socket(server.socket, server_side=True)

print("RPC Server listening on port 8080 (HTTPS)...")

# Register RPC functions to handle client requests
server.register_function(get_server_status, 'get_server_status')
server.register_function(update_database, 'update_database')
server.register_function(get_xml_content_by_topic, 'get_xml_content_by_topic')
server.register_function(search_wiki_content, 'search_wiki_content')
server.register_function(topic_wiki_update,'topic_wiki_update')

# Start the server
server.serve_forever()
