import os, requests, json, base64, urllib, sys
from urllib.request import urlopen, Request
from urllib.error import *

import base64


def make_request(url, headers=None, data=None, method=None):
    print("MR HEADERS:" + str(headers))
    print("MR DATA:" + str(data))
    print("MR method:" + method)
    request = Request(url, headers=headers or {}, data=data, method=method)
    try:
         with urlopen(request, timeout=10) as response:
            print("response_status" + response.status)
            return response.read(), response
    except HTTPError as error:
        print("{0}".format(sys.exc_info()))
        print(error.status, error.reason)
    except HTTPError as error:
        print(error.reason)
    except TimeoutError:
         print("Request timed out")
"""
def make_request(url, headers=None, method=None):
    print("MR HEADERS:" + str(headers))
    print("MR method:" + method)
    request = Request(url, headers=headers or {}, method=method)
    try:
         with urlopen(request, timeout=10) as response:
            print("response_status" + response.status)
            return response.read(), response
    except HTTPError as error:
        print(error.status, error.reason)
    except HTTPError as error:
        print(error.reason)
    except TimeoutError:
         print("Request timed out")
"""

b = base64.b64encode(bytes('Y5XrdAWZhwscrASWKXnARt2YCV0t3CHP:PKple38AUYm7FQJc', 'utf-8')) # bytes
base64_str = b.decode('utf-8')
print("base64_str: {0}".format(base64_str))

cURLstr = r"curl -v 'https://developer.api.autodesk.com/authentication/v2/token' \
   -X 'POST' \
   -H 'Content-Type: application/x-www-form-urlencoded' \
   -H 'Accept: application/json' \
   -H 'Authorization: Basic " + base64_str + "' \
   -d 'grant_type=client_credentials' \
   -d 'scope=data:read' --silent"
responseOS = os.popen(cURLstr).read()
print(type(responseOS))
print(responseOS)
jsonResponse = json.loads(responseOS)
print(type(jsonResponse))
print(jsonResponse)
print("access_token: {0}".format(jsonResponse['access_token']))
authToken = jsonResponse['access_token']

hubCURLstr = "curl -X GET -H 'Authorization: Bearer " + authToken +  " ' 'https://developer.api.autodesk.com/project/v1/hubs'"
try:
    hubResponse = os.popen(hubCURLstr).read()
    print(type(hubResponse))
    print("hubResponse: {0}".format(hubResponse))
except HTTPError as error:
        print("{0}".format(sys.exc_info()))
        print(error.status, error.reason)

hubID = ""
projectID = "5b649deb-6042-49cc-a617-e7bfa638b662"

folderIdCURL = 'curl -X GET -H "Authorization: Bearer ' + authToken + 'nFRJxzCD8OOUr7hzBwbr06D76zAT" "https://developer.api.autodesk.com/project/v1/hubs/' + hubID + '/projects/' + projectID +'/topFolders"'


cURLstr = r"curl -v 'https://developer.api.autodesk.com/bim360/docs/v1/projects/" + projectID + "/folders/urn%3Aadsk.wipprod%3Afs.folder%3Aco.9g7HeA2wRqOxLlgLJ40UGQ/custom-attribute-definitions' \
  -H 'Authorization: Bearer " + authToken

headers = {
    'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json', 'Authorization': 'Basic ' + base64_str,
}

data = {'grant_type': 'client_credentials', 'scope': 'data:read',
}
"""
with open('request.json') as f:
    data = f.read().replace('\n', '')
"""
post_dict = data
headers_dict = headers

json_string_data = json.dumps(post_dict)
json_string_headers = json.dumps(headers_dict)
post_data = json_string_data.encode("utf-8")
headers_data = json_string_headers.encode("utf-8")
#print('post_data ' + str(post_data))
#print('headers_data ' + str(headers_data))

#body, response = make_request('https://developer.api.autodesk.com/authentication/v2/token', data=post_data, headers=headers, method='POST')

#body, response = make_request('https://developer.api.autodesk.com/authentication/v2/token', data=post_data, headers=headers, method='POST')

#print("body" + body.decode("utf-8"))

print("---------------------------")
#req = urllib.request.Request(url='https://developer.api.autodesk.com/authentication/v2/token?' + 'response_type=code&client_id=p7OfwP16gGQe4344H9mYefqXMvhlwUOj&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Foauth%2Fcallback%2F&scope=data:read')
#with urllib.request.urlopen(req) as f:
#    pass
#print(f.status)
#print(f.reason)

#response = requests.post('https://developer.api.autodesk.com/authentication/v2/token', headers=headers, data=data)
#print(response.text)



"""
import requests
url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=mykeyhere"
data = requests.get(url).json


url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=mykeyhere"
my_json_data = json.load(open("request.json"))
req = requests.post(url,data=my_json_data)
print(req.text)
"""