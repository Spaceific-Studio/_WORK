from flask import Flask, request, redirect
import requests
import os
from dotenv import load_dotenv
import http.server
import json

app = Flask(__name__)

# Load configuration variables from .env
load_dotenv()
print(f"os.getenv('CLIENT_ID') - {os.getenv('CLIENT_ID')}")
print(f"os.getenv('CLIENT_SECRET') - {os.getenv('CLIENT_SECRET')}")
print(f"os.getenv('CALLBACK_URL') - {os.getenv('CALLBACK_URL')}")
print(f"os.getenv('SCOPES') - {os.getenv('SCOPES')}")

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


if __name__ == '__main__':
  app.run(debug=True, port=8080)

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