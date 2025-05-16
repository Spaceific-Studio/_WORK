import http.client, base64, json
import secrets
import hashlib
import tkinter as tk
from tkinter import Entry, Label, Button
from tkinter import Canvas, Scrollbar, Text, Frame




b = base64.b64encode(bytes('Y5XrdAWZhwscrASWKXnARt2YCV0t3CHP:PKple38AUYm7FQJc', 'utf-8')) # bytes
base64_str = b.decode('utf-8')
print("base64_str: {0}".format(base64_str))

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
print(response_data)

# Uzavřete spojení
conn.close()

# Převod json na dict
jsonResponse = json.loads(response_data)
print(type(jsonResponse))
#print(jsonResponse)
print("access_token: {0}".format(jsonResponse['access_token']))

# URL pro získání seznamu všech hubů v ACC
hub_list_url = "/project/v1/hubs"

# Přístupový token (Bearer Token) získaný s odpovídajícími oprávněními
access_token = jsonResponse['access_token']
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
headers = {
    "Authorization": f"Bearer {access_token}"
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

selected_project_id = f"b.eb8763a4-b474-492a-9927-256de2c29dc1"

#Získání 3-Legged Token

client_id = "Y5XrdAWZhwscrASWKXnARt2YCV0t3CHP"
client_secret = "PKple38AUYm7FQJc"
redirect_uri = "http://localhost:8080/"
authorization_url = "developer.api.autodesk.com"
token_url = "developer.api.autodesk.com"

# Náhodný generovaný PKCE kód (Proof Key for Code Exchange)
code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).rstrip(b'=').decode('utf-8')

# Vytvoření funkce pro autorizaci
def authorize():
    # Vytvoření připojení k serveru pro získání URL pro autorizaci
    conn = http.client.HTTPSConnection(authorization_url)

    # Vytvoření URL pro získání autorizačního kódu s PKCE
    authorization_code_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "data:read",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }

    authorization_code_path = f"/authentication/v1/authorize?{'&'.join([f'{key}={value}' for key, value in authorization_code_params.items()])}"
    conn.request("GET", authorization_code_path)

    response = conn.getresponse()
    response_data = response.read()
    #response_dict = json.loads(response_data)
    authorization_code_url = response.getheader("Location")
    
    #response_str = ""
    #response_str = join(x for x in values(response_dict))
    
    # Zobrazení URL v textovém widgetu
    text_widget.delete(1.0, tk.END)  # Vymaže předchozí text
    text_widget.insert(tk.END, "Autorizační URL:\n" + authorization_code_url +"\n response_data\n" + str(response_data))

# Vytvoření Tkinter okna
root = tk.Tk()
root.title("3-Legged Autorizace")

# Vytvoření tlačítka pro autorizaci
authorize_button = Button(root, text="Autorizovat", command=authorize)
authorize_button.pack()

# Vytvoření rámu s textovým widgetem a scrolbarem
frame = Frame(root)
frame.pack()

# Vytvoření textového widgetu
text_widget = Text(frame, wrap=tk.WORD)
text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Vytvoření scrollbaru
scrollbar = Scrollbar(frame, command=text_widget.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_widget.config(yscrollcommand=scrollbar.set)

# Spuštění Tkinter smyčky
root.mainloop()


# Vytvoření připojení k serveru pro získání autorizačního kódu
conn = http.client.HTTPSConnection(authorization_url)

# Vytvoření URL pro získání autorizačního kódu s PKCE
authorization_code_params = {
    "response_type": "code",
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "scope": "data:read",
    "code_challenge": code_challenge,
    "code_challenge_method": "S256"
}

authorization_code_path = f"/authentication/v1/authorize?{'&'.join([f'{key}={value}' for key, value in authorization_code_params.items()])}"
conn.request("GET", authorization_code_path)

response = conn.getresponse()
response_data = response.read()
authorization_code_url = response.getheader("Location")
print(f"authorization_code_url: {authorization_code_url}")
authorization_code = authorization_code_url.split("code=")[1]

# Získání autorizačního kódu z odpovědi po autorizaci
print(f"Otevřete tuto URL ve vašem prohlížeči a autorizujte aplikaci:\n{authorization_code_url}")
authorization_code = input("Zadejte autorizační kód: ")

# Vytvoření připojení k serveru pro výměnu autorizačního kódu za token
token_conn = http.client.HTTPSConnection(token_url)

# Vytvoření POST požadku pro výměnu autorizačního kódu za token
token_request_data = f"client_id={client_id}&client_secret={client_secret}&grant_type=authorization_code&code={authorization_code}&redirect_uri={redirect_uri}&code_verifier={code_verifier}"

headers = {"Content-Type": "application/x-www-form-urlencoded"}

token_conn.request("POST", "/authentication/v1/gettoken", body=token_request_data, headers=headers)

# Získání odpovědi
token_response = token_conn.getresponse()
token_data = token_response.read()

# Výstup tokenu
print("3-Legged Token:")
print(token_data.decode('utf-8'))


# URL pro získání seznamu vlastních atributů projektu
custom_attributes_url = f"/construction/assets/v1/projects/{selected_project_id}/custom-attributes"

# Vytvoření připojení k serveru
conn = http.client.HTTPSConnection("developer.api.autodesk.com")

# Hlavičky pro požadavek
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Nastavení cesty pro GET požadavek
conn.request("GET", custom_attributes_url, headers=headers)

# Získání odpovědi
response = conn.getresponse()
response_data = response.read()

# Zkontrolujte, zda požadavek byl úspěšný
if response.status == 200:
    custom_attributes = json.loads(response_data)
    for attribute in custom_attributes['data']:
        attribute_name = attribute['attributes']['name']
        print(f"Custom Attribute: {attribute_name}")
else:
    print(f"Chyba při získávání seznamu vlastních atributů projektu ({response.status}): {response_data}")

# Uzavřete spojení
conn.close()



# URL pro získání seznamu adresářů v top-level adresáři
top_level_directory_list_url = f"/data/v1/hubs/{hub_id}/projects/{project_id}/topFolders"

# Vytvoření připojení k serveru
conn = http.client.HTTPSConnection("developer.api.autodesk.com")

# Hlavičky pro požadavek
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Nastavení cesty pro GET požadavek na seznam top-level adresářů
conn.request("GET", top_level_directory_list_url, headers=headers)

# Získání odpovědi
response = conn.getresponse()
response_data = response.read()

# Zkontrolujte, zda požadavek byl úspěšný
if response.status == 200:
    top_level_directory_list = json.loads(response_data)
    for top_level_directory in top_level_directory_list['data']:
        directory_id = top_level_directory['id']
        directory_name = top_level_directory['attributes']['name']
        print(f"Directory ID: {directory_id}, Název: {directory_name}")
else:
    print(f"Chyba při získávání seznamu top-level adresářů ({response.status}): {response_data}")

# Uzavřete spojení
conn.close()

selected_directory_name = "09_Revit"

# URL pro získání seznamu adresářů v projektu
directory_list_url = f"/data/v1/hubs/{hub_id}/projects/{selected_project_id}/folders"

# Vytvoření připojení k serveru
conn = http.client.HTTPSConnection("developer.api.autodesk.com")

# Hlavičky pro požadavek
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Nastavení cesty pro GET požadavek na seznam adresářů
conn.request("GET", directory_list_url, headers=headers)

# Získání odpovědi
response = conn.getresponse()
response_data = response.read()
# Adresář na hubu, ze kterého chcete získat seznam souborů (nastavte na konkrétní adresář)
directory_id = None
# Nahraďte YOUR_DIRECTORY_ID za ID konkrétního adresáře

# Zkontrolujte, zda požadavek byl úspěšný
if response.status == 200:
    directory_list = json.loads(response_data)
    found_directory_id = None
    found_class_id = None

    for directory in directory_list['data']:
        if directory['attributes']['name'] == selected_directory_name:
            found_directory_id = directory['id']
            break
    """
    if found_directory_id:
        class_list_url = f"/data/v1/hubs/{hub_id}/projects/{project_id}/folders/{found_directory_id}/children"
        conn.request("GET", class_list_url, headers=headers)
        class_response = conn.getresponse()
        class_response_data = class_response.read()

        if class_response.status == 200:
            class_list = json.loads(class_response_data)
            for class_item in class_list['data']:
                if class_item['attributes']['name'] == class_name:
                    found_class_id = class_item['id']
                    break
    """
    if found_directory_id:
        print(f"Directory ID: {found_directory_id}")
        directory_id = found_directory_id
    else:
        print("Adresář nebyl nalezeny.")

else:
    print(f"Chyba při získávání seznamu adresářů ({response.status}): {response_data}")

# Uzavřete spojení
conn.close()



# URL pro získání seznamu souborů v daném adresáři
file_list_url = f"/data/v1/hubs/{hub_id}/projects/{selected_project_id}/folders/{directory_id}/files"

