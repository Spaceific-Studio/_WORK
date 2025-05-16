import http.server
import socketserver
import webbrowser
import urllib
import base64
import json
import os
from urllib.parse import parse_qs, urlparse

# Třída pro obsluhu požadavků s přidáním cesty

#print("http.server.SimpleHTTPRequestHandler dir({0}".format(dir(http.server.SimpleHTTPRequestHandler)))
#print("socketserver.TCPServer dir({0}".format(dir(socketserver.TCPServer)))

clientId = 'Y5XrdAWZhwscrASWKXnARt2YCV0t3CHP'
clientSecret = 'PKple38AUYm7FQJc'
print(f"dir(webbrowser) : {dir(webbrowser)}")

class MyCode(object):
    threeLeggedAuthCode = "qaI0NXsQiBiVnNDG0zIiPra__inpUivf3Lp8dMn-"
    twoLeggedToken = ""
    def __init__(cls):
        pass
    
    @classmethod    
    def setThreeLeggedAuthCode(cls, inText):
        cls.threeLeggedAuthCode = inText
        
    @classmethod
    def getThreeLeggedAuthCode(cls):
        return cls.threeLeggedAuthCode
        
    @classmethod    
    def setTwoLeggedToken(cls, inText):
        cls.twoLeggedToken = inText
        
    @classmethod
    def getTwoLeggedToken(cls):
        return cls.twoLeggedToken
    


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Získání adresy z TCPServer
        server_host, server_port = self.server.server_address

        # Zpracování zbytku kódu...
        parsed_path = urllib.parse.urlparse(self.path)
        print("parsed_path {0}".format(parsed_path))
        
        if "code" in parsed_path.query:
            MyCode.setThreeLeggedAuthCode(parsed_path.query.split('=')[1])
            #self.send_response(200)
            #self.end_headers()
            #response_text = f'Hello, this is a response from {server_host}:{server_port}'
            #print(response_text)
            #self.wfile.write(response_text.encode())
        #else:
        super().do_GET()
    def getRequestLine():
        return self.requestline

# Definujte funkci pro otevření okna s přihlašovacími údaji

def getThreeLeggedAuthCode(inClientId):
    # Nastavte potřebné proměnné
    client_id = inClientId
    #redirect_uri = 'http://localhost:8080'
    #redirect_uri = 'http%3A%2F%2Flocalhost%3A8080%2F'
    redirect_uri = 'http%3A%2F%2Flocalhost%3A8080%2F'
    # Spusťte HTTP server na lokálním portu pro přesměrování URI
    with socketserver.TCPServer(("", 8080), MyHandler) as httpd:
        try:
            # Otevře prohlížeč s přihlašovacím URL
            myWeb = webbrowser.open(f"https://developer.api.autodesk.com/authentication/v1/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=data:read")

            # Čekáme na přesměrování na naši URI a získáme autorizační kód
            #httpd.handle_request()  # Blocking call
            #print(f"Serving on {httpd.server_address}")
            httpd.handle_request()
            #authorization_code = parse_qs(urlparse(httpd.path).query).get("code")
            #authorization_code = str(httpd.parse_request())
            
            authorization_code = ""
            #print("authorization_code : {0}".format(authorization_code))
            #print(f"dir(myWeb) : {dir(myWeb)}")
            #del myWeb

            # Zobrazíme autorizační kód
            return authorization_code[0] if authorization_code else None
        except Exception as e:
            print(f"Chyba: {e}")
            return None
            
getThreeLeggedAuthCode(clientId)

print('3 Legged Authorization Code : {0}'.format(MyCode.getThreeLeggedAuthCode()))

def get2LeggedToken(inClientId,inClientSecret):
    b = base64.b64encode(bytes(inClientId + ':' + inClientSecret, 'utf-8')) # bytes
    #b = base64.b64encode(bytes('Y5XrdAWZhwscrASWKXnARt2YCV0t3CHP:PKple38AUYm7FQJc', 'utf-8')) # bytes
    base64_str = b.decode('utf-8')
    #print("base64_str: {0}".format(base64_str))
    # URL a cesta
    url = "developer.api.autodesk.com"
    path = "/authentication/v2/token"
    
    # Hlavičky
    headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "Authorization": 'Basic ' + base64_str
    }
    # Tělo požadavku
    data = "grant_type=client_credentials&scope=data:read"
    # Vytvoření připojení
    conn = http.client.HTTPSConnection(url)
    
    # Odešlete POST požadavek
    conn.request("POST", path, body=data, headers=headers)
    
    # Získejte odpověď
    response = conn.getresponse()
    
    # Přečtěte obsah odpovědi
    response_data = response.read()
    
    # Vytiskněte obsah odpovědi
    #print(response_data)
    
    # Uzavřete spojení
    conn.close()
    
    # Převod json na dict
    jsonResponse = json.loads(response_data)
    #print(type(jsonResponse))
    #print(jsonResponse)
    #print("access_token: {0}".format(jsonResponse['access_token']))
    MyCode.setTwoLeggedToken(jsonResponse['access_token'])
    
get2LeggedToken(clientId, clientSecret)
twoLeggedToken = MyCode.getTwoLeggedToken()
print("MyCode.twoLeggedToken : {0}".format(twoLeggedToken))

# URL pro získání seznamu všech hubů v ACC
hub_list_url = "/project/v1/hubs"

# Přístupový token (Bearer Token) získaný s odpovídajícími oprávněními

#access_token = jsonResponse['access_token']
access_token = MyCode.getTwoLeggedToken()
#access_token = MyCode.getCode()

# Nahraďte YOUR_ACCESS_TOKEN vaším platným přístupovým tokenem

# Vytvoření připojení k serveru
conn = http.client.HTTPSConnection("developer.api.autodesk.com")

# Hlavičky pro požadavek
headers = {
    "Authorization": f"Bearer " + access_token
}

# Nastavení cesty pro GET požadavek
conn.request("GET", hub_list_url, headers=headers)

# Získání odpovědi
response = conn.getresponse()
response_data = response.read()
#print(response_data)

# Zkontrolujte, zda požadavek byl úspěšný
if response.status == 200:
    hub_list = json.loads(response_data)
    for hub in hub_list['data']:
        hub_id = hub['id']
        hub_name = hub['attributes']['name']
        print(f"Hub ID: {hub_id}, Název: {hub_name}")
        print("{:_<10}".format(""))
else:
    print(f"Chyba při získávání seznamu hubů ({response.status}): {response_data}")

# Uzavřete spojení
conn.close()

# URL pro získání seznamu všech projektů v určitém hubu (nastavte na konkrétní hub ID)

project_list_url = f"/project/v1/hubs/{hub_id}/projects"

# Vytvoření připojení k serveru
conn = http.client.HTTPSConnection("developer.api.autodesk.com")

# Hlavičky pro požadavek
twoLeggedToken = MyCode.getTwoLeggedToken()
headers = {
    "Authorization": f"Bearer {MyCode.getTwoLeggedToken()}"
}

# Nastavení cesty pro GET požadavek
conn.request("GET", project_list_url, headers=headers)

# Získání odpovědi
response = conn.getresponse()
response_data = response.read()

# Zkontrolujte, zda požadavek byl úspěšný
if response.status == 200:
    project_list = json.loads(response_data)
    for project in project_list['data']:
        project_id = project['id']
        project_name = project['attributes']['name']
        print(f"Project ID: {project_id}, Název: {project_name}, project_list_url - {project_list_url}")
else:
    print(f"Chyba při získávání seznamu projektů ({response.status}): {response_data}")

# Uzavřete spojení
conn.close()

# funkce pro získání seznamu složek

def ziskat_id_slozky(token, project_id, folder_name, base_url):
    url = f"{base_url}/data/v1/projects/{project_id}/folders"
    headers = {"Authorization": f"Bearer {token}"}
    
    conn.request("GET", project_list_url, headers=headers)
    response = conn.getresponse()
    response_data = response.read()
    data = json.loads(response_data)

    for folder in data["data"]:
        if folder["attributes"]["displayName"] == folder_name:
            folder_id = folder["id"]
            print(f"ID složky '{folder_name}': {folder_id}")
            return folder_id

    print(f"Složka '{folder_name}' nebyla nalezena.")
    return None

#ziskat_id_slozky(MyCode.getThreeLeggedAuthCode(), 'b.aeeffa13-fa76-4740-8c75-ccced3afc914', "MODELY", f"https://developer.api.autodesk.com")

def ziskat_Top_folder(token, hub_id, project_id, folder_name, base_url):
    #url = f"{base_url}/project/v1/hubs/:{hub_id}/projects/:{project_id}/topFolders
    splittedHubId = hub_id.split('.')[1]
    print(f"splitted_HUB ID: {splittedHubId}")
    top_folder_url = f"/project/v1/hubs/b.8a0397e0-4e1b-4a3c-8af2-266938cb8473/projects/b.f560e904-c5c2-4b56-afe6-20fa267287fe/topFolders"

    # Vytvoření připojení k serveru
    conn = http.client.HTTPSConnection("developer.api.autodesk.com")

    # Hlavičky pro požadavek
    #twoLeggedToken = MyCode.getTwoLeggedToken()
    print(f"auth_token: {token}")
    headers = {
    "Authorization": f"Bearer {token}", "x-user-id": "8a0397e0-4e1b-4a3c-8af2-266938cb8473"
}

    # Nastavení cesty pro GET požadavek
    conn.request("GET", top_folder_url, headers=headers)

    #headers = {"Authorization": f"Bearer {token}"}
    
    #conn.request("GET", project_list_url, headers=headers)
    response = conn.getresponse()
    response_data = response.read()
    print("HUB_ID in ziskat_Top_Folder: {0}".format(hub_id))
    print(f"top_folder_url: {top_folder_url}")
    if response.status == 200:
        print(f"top folder response: {response_data}")
    else:
        print(f"Chyba při získávání topFoldru ({response.status}): {response_data}")

    # Uzavřete spojení
    conn.close()
    
"""
hubCURLstr = "curl -v 'https://developer.api.autodesk.com/project/v1/hubs/:hub_id/projects/:project_id/topFolders' \
  -H 'Authorization: Bearer AuIPTf4KYLTYGVnOHQ0cuolwCW2a' \
  -H 'x-user-id: 8a0397e0-4e1b-4a3c-8af2-266938cb8473'"
try:
    hubResponse = os.popen(hubCURLstr).read()
    print(type(hubResponse))
    print("hubResponse: {0}".format(hubResponse))
except HTTPError as error:
        print("{0}".format(sys.exc_info()))
        print(error.status, error.reason)
"""        

ziskat_Top_folder(MyCode.getTwoLeggedToken(), hub_id, project_list['data'][1]['id'], "MODELY", "https://developer.api.autodesk.com")



#ziskat_Top_folder(MyCode.getThreeLeggedAuthCode(), hub_id, 'b.aeeffa13-fa76-4740-8c75-ccced3afc914', "MODELY", "https://developer.api.autodesk.com")

 

"""
# URL pro získání seznamu všech parameter collections anebo groups v určitém hubu (nastavte na konkrétní hub ID)

group_list_url = f"parameters/v1/accounts/{MyCode.getThreeLeggedAuthCode()}/groups"

# Vytvoření připojení k serveru
conn = http.client.HTTPSConnection("developer.api.autodesk.com")

# Hlavičky pro požadavek
twoLeggedToken = MyCode.getTwoLeggedToken()
headers = {
    "Authorization": f"Bearer {MyCode.getTwoLeggedToken()}"
}

# Nastavení cesty pro GET požadavek
conn.request("GET", group_list_url, headers=headers)

# Získání odpovědi
response = conn.getresponse()
response_data = response.read()

# Zkontrolujte, zda požadavek byl úspěšný
if response.status == 200:
    project_list = json.loads(response_data)
    for group in project_list['data']:
        group_id = group['id']
        group_title = group['title']
        print(f"Project ID: {group_id}, Název: {group_title}")
else:
    print(f"Chyba při získávání seznamu collections ({response.status}): {response_data}")

# Uzavřete spojení
conn.close()
"""