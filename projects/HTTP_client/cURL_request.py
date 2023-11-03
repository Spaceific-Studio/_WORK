import requests, json, base64

import base64
b = base64.b64encode(bytes('Y5XrdAWZhwscrASWKXnARt2YCV0t3CHP:PKple38AUYm7FQJc', 'utf-8')) # bytes
base64_str = b.decode('utf-8')
print("base64_str: {0}".format(base64_str))

headers = {
    'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json', 'Authorization': 'Basic ' + base64_str,
}

data = {'grant_type': 'client_credentials', 'scope': 'data:read',
}
"""
with open('request.json') as f:
    data = f.read().replace('\n', '')
"""
response = requests.post('https://developer.api.autodesk.com/authentication/v2/token', headers=headers, data=data)
print(response.text)



"""
import requests
url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=mykeyhere"
data = requests.get(url).json


url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=mykeyhere"
my_json_data = json.load(open("request.json"))
req = requests.post(url,data=my_json_data)
print(req.text)
"""