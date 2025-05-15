import webbrowser
from urllib.parse import urlencode, parse_qs
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import socket
import tkinter as tk
from tkinter import simpledialog, messagebox
import json

# Replace these with your actual Autodesk app credentials
CLIENT_ID = "Y5XrdAWZhwscrASWKXnARt2YCV0t3CHP"
CLIENT_SECRET = "PKple38AUYm7FQJc"
CALLBACK_URL = "http://localhost:8080"
SCOPE = "data:read data:write account:read"

# Autodesk Authentication URLs (OAuth 2.0)
AUTH_URL = "https://developer.api.autodesk.com/authentication/v2/authorize"
TOKEN_URL = "https://developer.api.autodesk.com/authentication/v2/token"

# Autodesk API endpoints
HUBS_URL = "https://developer.api.autodesk.com/project/v1/hubs"
PROJECTS_URL = "https://developer.api.autodesk.com/project/v1/hubs/{hub_id}/projects"
FOLDER_CONTENTS_URL = "https://developer.api.autodesk.com/data/v1/projects/{project_id}/folders/{folder_id}/contents"
CUSTOM_ATTRIBUTES_URL = "https://developer.api.autodesk.com/bim360/docs/v1/projects/{project_id}/folders/{folder_id}/custom-attribute-definitions"
AEC_MODEL_GRAPHQL_URL = "https://developer.api.autodesk.com/aec/graphql"

# Global variables
authorization_code = None
server_closed = threading.Event()
access_token = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code
        query_components = parse_qs(self.path.split('?', 1)[-1])
        authorization_code = query_components.get('code', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Authorization successful! You can close this window.')
        
        server_closed.set()

    def log_message(self, format, *args):
        return

class AECDataModelClient:
    def __init__(self, base_url, api_key):
        """
        Initialize the AEC Data Model API Client
        
        :param base_url: Base URL of the AEC Data Model API
        :param api_key: Authentication API key
        """
        self.base_url = base_url
        self.access_token = api_key
        self.graphql_url = "https://developer.api.autodesk.com/aec/graphql"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            "region":"EMEA"
        }
        try:
            hubs = self.get_hubs()

            self.hubName = hubs[0]['name']
            self.hubId = hubs[0]['id']
            print(f"Successfuly joined to hub: {self.hubName} - {self.hubId}")
        except Exception as ex:
            print("unable to join to hub: {0}".format(ex))

    
    def execute_graphql_query(self, query, variables=None):
        """
        Execute a GraphQL query using JSON payload
        
        :param query: GraphQL query string
        :param variables: Optional variables dictionary
        :return: Query results
        """
        try:
            # Prepare payload
            payload = {
                'query': query
            }
            
            # Add variables if provided
            if variables:
                payload['variables'] = variables
            
            # Headers for GraphQL request
            headers = self.headers
            
            # Send POST request to GraphQL endpoint
            response = requests.post(
                self.base_url, 
                headers=headers, 
                json=payload
            )
            
            # Check for successful response
            response.raise_for_status()
            
            # Return parsed JSON response
            #print(f'JSON response {response.json()}')
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"GraphQL query error: {e}")
            print(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response'}")
            return None

    def get_hubs(self):
        """
        Retrieve list of hubs
        
        :return: List of hub names
        """

        # GraphQL query to fetch hubs
        query = '''
        query GetHubs {
            hubs {
                pagination {
                    cursor
                }
                results {
                    name
                    id
                }
            }
        }
        '''
        """
        # GraphQL query to fetch hub names
        query = '''{
            hubs {
                results {
                    name
                    id
                }
            }
        }'''
        """
        
        # Execute query
        result = self.execute_graphql_query(query)
        print(f"result in get_hubs: {result['data']}")
        # Extract hub names
        
        if result and 'data' in result:
            return result.get('data', {}).get('hubs', {}).get('results', [])
        else:
            return result

    def get_walls(self, elementGroupId):
        """
        Retrieve list of wall instances in model
        
        :return: List of wall instances properties
        """

        # GraphQL query to fetch hubs
        query = '''
        query GetWalls($elementGroupId: ID!, $propertyFilter: String!, $pagination: PaginationInput) {
            elementsByElementGroup(
                elementGroupId: $elementGroupId, filter: {query:$propertyFilter}, pagination: $pagination) {
                    pagination {
                        cursor
                    }
                    results {
                        id
                        name   	
                         properties {
                            results {
                                name
                                value
                            }
                        }
                    }    
                }
            }
        '''
        variables = {
            "elementGroupId": elementGroupId,
            "propertyFilter": "'property.name.category'=contains= Wall and 'property.name.Element Context' ==Instance and 'property.name.Element Name'=contains= 500"
        }
        
        # Execute query
        result = self.execute_graphql_query(query, variables=variables)
        #print(f"result in get_walls: {result['data']}")
        # Extract walls
        
        if result and 'data' in result:
            #return result.get('data', {}).get('results', [])
            return result
        else:
            return result
            
    def get_models_in_directory(self, hub_id, project_id, directory_path):
        """
        Retrieve list of models in a specific directory for a project
        
        :param hub_id: ID of the hub
        :param project_id: ID of the project
        :param directory_path: Path to the directory containing models
        :return: List of models in the specified directory
        """
        # GraphQL query to fetch models
        query = """
        query GetModelsInDirectory(
            $hubId: ID!, 
            $projectId: ID!, 
            $directoryPath: String!
        ) {
            hub(id: $hubId) {
                project(id: $projectId) {
                    models(
                        filter: {
                            directory: $directoryPath
                        }
                    ) {
                        items {
                            id
                            name
                            version
                            path
                            lastModifiedDate
                            fileType
                        }
                    }
                }
            }
        }
        """
        
        # Prepare variables for the query
        variables = {
            "hubId": hub_id,
            "projectId": project_id,
            "directoryPath": directory_path
        }
        
        # Prepare payload
        payload = {
            "query": query,
            "variables": variables
        }
        
        try:
            # Send POST request to the GraphQL endpoint
            response = requests.post(
                f"{self.base_url}/graphql", 
                headers=self.headers, 
                data=json.dumps(payload)
            )
            
            # Check for successful response
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Extract models from the response
            models = result.get('data', {}).get('hub', {}).get('project', {}).get('models', {}).get('items', [])
            
            return models
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models: {e}")
            return []

def start_local_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, CallbackHandler)
    httpd.handle_request()

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def get_authorization_code():
    global CALLBACK_URL
    port = get_free_port()
    CALLBACK_URL = f"http://localhost:8080"

    server_thread = threading.Thread(target=start_local_server)
    server_thread.start()

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": CALLBACK_URL,
        "scope": SCOPE
    }
    auth_url = f"{AUTH_URL}?{urlencode(params)}"
    print(f"auth_url: {auth_url}")
    print(f"Please authorize the application in your browser.")
    webbrowser.open(auth_url)

    server_closed.wait(timeout=120)

    if not authorization_code:
        print("Failed to obtain authorization code. The process may have timed out.")
    
    return authorization_code

def get_access_token(auth_code):
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": CALLBACK_URL,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error getting access token: {response.text}")
        return None

def get_hubs(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(HUBS_URL, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error getting hubs: {response.text}")
        return []

def get_projects(token, hub_id):
    headers = {"Authorization": f"Bearer {token}"}
    url = PROJECTS_URL.format(hub_id=hub_id)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error getting projects: {response.text}")
        return []

def select_hub(hubs):
    options = [f"{hub['attributes']['name']} (ID: {hub['id']})" for hub in hubs]
    choice = create_selection_dialog("Select Hub", "Choose a hub:", options)
    if choice:
        return next(hub for hub in hubs if f"{hub['attributes']['name']} (ID: {hub['id']})" == choice)
    return None

def get_custom_attributes(token, project_id, folder_id):
    headers = {"Authorization": f"Bearer {token}"}
    url = CUSTOM_ATTRIBUTES_URL.format(project_id=project_id, folder_id=folder_id)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error getting projects: {response.text}")
        return []

def create_selection_dialog(title, prompt, options):
    result = [None]
    
    def on_select():
        selection = listbox.curselection()
        if selection:
            result[0] = options[selection[0]]
        dialog.quit()

    dialog = tk.Tk()
    dialog.title(title)
    dialog.geometry("400x300")
    dialog.resizable(False, False)

    tk.Label(dialog, text=prompt).pack(pady=10)

    listbox = tk.Listbox(dialog, width=50)
    listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    for option in options:
        listbox.insert(tk.END, option)

    tk.Button(dialog, text="Select", command=on_select).pack(pady=10)

    dialog.mainloop()
    dialog.destroy()
    
    return result[0]

def select_project(projects):
    options = [f"{project['attributes']['name']} (ID: {project['id']})" for project in projects]
    choice = create_selection_dialog("Select Project", "Choose a project:", options)
    if choice:
        return next(project for project in projects if f"{project['attributes']['name']} (ID: {project['id']})" == choice)
    return None

def get_folder_contents(token, project_id, folder_id):
    headers = {"Authorization": f"Bearer {token}"}
    url = FOLDER_CONTENTS_URL.format(project_id=project_id, folder_id=folder_id)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error getting folder contents: {response.text}")
        return []

''' def display_folder_structure(token, project_id, folder_id, level=0):
    contents = get_folder_contents(token, project_id, folder_id)
    structure = ""
    for item in contents:
        indent = "  " * level
        name = item['attributes']['displayName']
        item_type = item['type']
        structure += f"{indent}{name} ({item_type})\n"
        if item_type == 'folders':
            structure += display_folder_structure(token, project_id, item['id'], level + 1)
    return structure '''

def display_folder_structure(token, project_id, folder_id, level=0, **kwargs):
    folderName = kwargs['folder_name'] if 'folder_name' in kwargs else None
    contents = get_folder_contents(token, project_id, folder_id)
    structure = ""
    for item in contents:
        indent = "  " * level
        name = item['attributes']['displayName']
        item_type = item['type']
        structure += f"{indent}{name} ({item_type})\n"
        itemPropperties = ""
        for k,v in item.items():
            itemPropperties += f"< {k} : {v} >\n"
        #print(f"\n{name}\n\n###\nitemAttributes:\n{itemPropperties}\n###")
        print(f"\n{name} - {item_type}\n\n###")
        if item_type == 'folders':
            if folderName and (name == folderName or name == 'Project Files'):
                structure += display_folder_structure(token, project_id, item['id'], level + 1, **kwargs)
    return structure

def main():
    global access_token

    # Get the authorization code
    auth_code = get_authorization_code()
    if not auth_code:
        print("Failed to obtain authorization code.")
        return

    # Get the access token
    access_token = get_access_token(auth_code)
    if not access_token:
        print("Failed to obtain access token.")
        return

    # Get hubs
    hubs = get_hubs(access_token)
    if not hubs:
        print("No hubs found.")
        return

    selected_hub = None
    if len(hubs) == 1:
        selected_hub = hubs[0]
    else:
        selected_hub = select_hub(hubs)

    if not selected_hub:
        print("No hub selected.")
        return

    # Get projects for the selected hub
    projects = get_projects(access_token, selected_hub['id'])
    if not projects:
        print("No projects found for the selected hub.")
        return

    selected_project = select_project(projects)
    if not selected_project:
        print("No project selected.")
        return
    
    #working with GraphQL queries
    # Create API client
    client = AECDataModelClient(AEC_MODEL_GRAPHQL_URL, access_token)
    #client.get_models_in_directory(selected_hub, project_id, directory_path)
    #hubs = client.get_hubs()
    #hubs = client.get_hub_details()
    #for i, hub in enumerate(hubs):
    #    print(f"hub_{i}: " + hub['name'] + " id: " + hub['id'])
    wallsData = client.get_walls("YWVjZH4yeERkcUxEME5MMnR2QVE4dlh4WGE2X0wyQ35oSjZhWWlPOFN6ZVlTN1hySXQxTTdB")
    for i, element in enumerate(wallsData['data']['elementsByElementGroup']['results']):
        print(f"{i} - {element.get('name', [])} - {element.get('properties', [])}")

    # Get the top folder structure of the selected project
    project_id = selected_project['id']
    root_folder_id = selected_project['relationships']['rootFolder']['data']['id']
    folder_structure = display_folder_structure(access_token, project_id, root_folder_id, folder_name="Project Files")
    #folder_structure = display_folder_structure(access_token, project_id, root_folder_id, folder_name="09_REVIT")
    #folder_structure = display_folder_structure(access_token, project_id, root_folder_id, folder_name="09_Revit")
    custom_attributes = get_custom_attributes(access_token, project_id, "urn:adsk.wipemea:fs.folder:co.MeELLppmRG2LRb_JOor0hg")
    #print(f"get_custom_attributes() > {custom_attributes})")

    # Display the selected project information and folder structure
    messagebox.showinfo("Selected Project", 
                        f"Hub: {selected_hub['attributes']['name']}\n"
                        f"Hub ID: {selected_hub['id']}\n"
                        f"Project: {selected_project['attributes']['name']}\n"
                        f"Project ID: {project_id}\n\n"
                        f"Folder Structure:\n{folder_structure}"
                        )

if __name__ == "__main__":
    main()