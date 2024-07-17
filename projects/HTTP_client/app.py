from flask import Flask, request, redirect
import requests
import os
from dotenv import load_dotenv
import http.server
import socketserver
import webbrowser
import urllib
import json

app = Flask(__name__)

# Load configuration variables from .env
load_dotenv()

print(f"os.getenv('CLIENT_ID') - {os.getenv('CLIENT_ID')}")
print(f"os.getenv('CLIENT_SECRET') - {os.getenv('CLIENT_SECRET')}")
print(f"os.getenv('CALLBACK_URL') - {os.getenv('CALLBACK_URL')}")
print(f"os.getenv('SCOPES') - {os.getenv('SCOPES')}")

CLIENT_ID = os.getenv('CLIENT_ID') if os.getenv('CLIENT_ID') else "m97exmFH1Y6orJGrLhg4x1SIOt8eUXaZuLzJ9bJE7FgqZlig"
CLIENT_SECRET = os.getenv('CLIENT_SECRET') if os.getenv('CLIENT_SECRET') else "AWZQjJVT7wuR1JNcaIZOMMl9Nr8fJvVUcvJKLsXK4blk0GLO3AXFkvdnp4Gid1Ri"
CALLBACK_URL = os.getenv('CALLBACK_URL') if os.getenv('CALLBACK_URL') else "http://localhost:8080/api/auth/callback"
SCOPES = os.getenv('SCOPES') if os.getenv('SCOPES') else "data:read viewables:read"

print(f"CLIENT_ID - {CLIENT_ID}")
print(f"CLIENT_SECRET - {CLIENT_SECRET}")
print(f"CALLBACK_URL - {CALLBACK_URL}")
print(f"SCOPES - {SCOPES}")

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

class MyCode(object):
    threeLeggedAuthCode = ""
    threeLeggedAccessToken = ""
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
    
    @classmethod    
    def setThreeLeggedAccessToken(cls, inText):
        cls.threeLeggedAccessToken = inText
    
    @classmethod
    def getThreeLeggedAccessToken(cls):
        return cls.threeLeggedAccessToken

def getThreeLeggedAuthCode(inClientId):
    # Nastavte potřebné proměnné
    client_id = inClientId
    #redirect_uri = 'http://localhost:8080'
    redirect_uri = CALLBACK_URL
    #redirect_uri = 'http%3A%2F%2Flocalhost%3A8080%2F'
    # Spusťte HTTP server na lokálním portu pro přesměrování URI
    with socketserver.TCPServer(("", 8080), MyHandler) as httpd:
        try:
            # Otevře prohlížeč s přihlašovacím URL
            myWeb = webbrowser.open(f"https://developer.api.autodesk.com/authentication/v1/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=data:read")

            # Čekáme na přesměrování na naši URI a získáme autorizační kód
            #httpd.handle_request()  # Blocking call
            #print(f"Serving on {httpd.server_address}")
            httpd.handle_request()
            
            authorization_code = ""

            # Zobrazíme autorizační kód
            return authorization_code[0] if authorization_code else None
        except Exception as e:
            print(f"Chyba: {e}")
            return None        

def getAuthToken():
    url = "https://developer.api.autodesk.com"
    path = "/authentication/v2/token"
    headers = {
      "Content-Type": "application/x-www-form-urlencoded"
    }
    code = MyCode.getThreeLeggedAuthCode()
    print(f"getAuthToken() code - {code}")
    print(f"grant_type=authorization_code&code={code}&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&redirect_uri={CALLBACK_URL}")
    data = f"grant_type=authorization_code&code={code}&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&redirect_uri={CALLBACK_URL}"
    conn = http.client.HTTPSConnection(url)
    conn.request("POST", path, body=data, headers=headers)
    response = conn.getresponse()
    
    # Přečtěte obsah odpovědi
    response_data = response.read()
    
    # Vytiskněte obsah odpovědi
    #print(response_data)
    
    # Uzavřete spojení
    conn.close()
    
    # Převod json na dict
    #jsonResponse = json.loads(response_data)
    #print(type(jsonResponse))
    #print(jsonResponse)
    #print("access_token: {0}".format(jsonResponse['access_token']))
    #MyCode.setThreeLeggedAccessToken(jsonResponse['access_token'])
    #print(f"getAuthToken() - {MyCode.setThreeLeggedAccessToken(jsonResponse['access_token'])}")
      

def ziskat_Top_folder(token, hub_id, project_id):
    #url = f"{base_url}/project/v1/hubs/:{hub_id}/projects/:{project_id}/topFolders
    top_folder_url = f"/project/v1/hubs/:{hub_id}/projects/:{project_id}/topFolders"
    print(f"ziskat_Top_folder() > hub_id - {hub_id}, project_id - {project_id}")
    # Vytvoření připojení k serveru
    conn = http.client.HTTPSConnection("developer.api.autodesk.com")

    # Hlavičky pro požadavek
    #twoLeggedToken = MyCode.getTwoLeggedToken()
    print(f"auth_token: {token}")
    headers = {
    "Authorization": f"Bearer {token}", "x-user-id": os.getenv('CLIENT_ID')
    }

    # Nastavení cesty pro GET požadavek
    conn.request("GET", top_folder_url, headers=headers)

    #headers = {"Authorization": f"Bearer {token}"}
    
    #conn.request("GET", project_list_url, headers=headers)
    response = conn.getresponse()
    response_data = response.read()
    if response.status == 200:
        print(f"top folder response: {response_data}")
    else:
        print(f"Chyba při získávání topFoldru ({response.status}): {response_data}")

    # Uzavřete spojení
    conn.close()

@app.route('/')
def authenticate():
  return redirect(f"https://developer.api.autodesk.com/authentication/v2/authorize?response_type=code&client_id={os.getenv('CLIENT_ID')}&redirect_uri={os.getenv('CALLBACK_URL')}&scope={os.getenv('SCOPES')}")

@app.route('/api/auth/callback', methods=['POST','GET'])
def callback():
  # Get credential code
  code = request.args.get('code')
  MyCode.setThreeLeggedAuthCode(code)
  payload = f"grant_type=authorization_code&code={code}&client_id={os.getenv('CLIENT_ID')}&client_secret={os.getenv('CLIENT_SECRET')}&redirect_uri={os.getenv('CALLBACK_URL')}"
  tokenUrl = "https://developer.api.autodesk.com/authentication/v2/token"
  headers = {
      "Content-Type": "application/x-www-form-urlencoded"
  }
  resp = requests.request("POST", tokenUrl, data=payload, headers=headers)
  respJson = resp.json()
  print(f"respJson['access_token'] - {respJson['access_token']}")
  MyCode.setThreeLeggedAccessToken(respJson['access_token'])
  ### kod vlozeny z predosleho pokusu o pripojenie
  hub_list_url = "/project/v1/hubs"
  conn = http.client.HTTPSConnection("developer.api.autodesk.com")
  
  # Hlavičky pro požadavek
  headers = {
    "Authorization": f"Bearer " + MyCode.getThreeLeggedAccessToken(),
    "Region":"EMEA"}
  print(f"headers - {headers}")
  
  # Nastavení cesty pro GET požadavek
  conn.request("GET", hub_list_url, headers=headers)
  
  # Získání odpovědi
  response = conn.getresponse()
  response_data = response.read()
  if response.status == 200:
        hub_list = json.loads(response_data)
        for hub in hub_list['data']:
            hub_id = hub['id']
            hub_name = hub['attributes']['name']
            print(f"Hub ID: {hub_id}, Název: {hub_name}")
            print("{:_<10}".format(""))
  else:
        print(f"Chyba při získávání seznamu hubů ({response.status}): {response_data}")
  #print(f"response_data - {response_data}")
  conn.close()

  # URL pro získání seznamu všech projektů v určitém hubu (nastavte na konkrétní hub ID)

  project_list_url = f"/project/v1/hubs/{hub_id}/projects"

  # Vytvoření připojení k serveru
  conn = http.client.HTTPSConnection("developer.api.autodesk.com")

  # Hlavičky pro požadavek
  #twoLeggedToken = MyCode.getTwoLeggedToken()
  headers = {
    "Authorization": f"Bearer {MyCode.getThreeLeggedAccessToken()}"
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
            print(f"Project ID: {project_id}, Název: {project_name}")
  else:
        print(f"Chyba při získávání seznamu projektů ({response.status}): {response_data}")

  # Uzavřete spojení
  conn.close()

  ziskat_Top_folder(MyCode.getThreeLeggedAccessToken(), hub_id, 'b.aeeffa13-fa76-4740-8c75-ccced3afc914')
  ### kod vlozeny z predosleho pokusu o pripojenie
  # Return success response
  return f"{respJson}", 200

MyCode.setThreeLeggedAccessToken(getThreeLeggedAuthCode(CLIENT_ID))
print(f"MyCode.getThreeLeggedAccessToken() - {MyCode.getThreeLeggedAccessToken()}")

getAuthToken()
#if __name__ == '__main__':
#  app.run(debug=True, port=8080)

#print(f"MyCode.getThreeLeggedAccessToken() - {MyCode.getThreeLeggedAccessToken()}")

'''
hub_list_url = "/project/v1/hubs"
conn = http.client.HTTPSConnection("developer.api.autodesk.com")

# Hlavičky pro požadavek
headers = {
    "Authorization": f"Bearer " + MyCode.getThreeLeggedAccessToken(),
    "region":"EMEA"
}
print(f"headers - {headers}")

# Nastavení cesty pro GET požadavek
conn.request("GET", hub_list_url, headers=headers)

# Získání odpovědi
response = conn.getresponse()
response_data = response.read()
print(f"response_data - {response_data}") 

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
'''