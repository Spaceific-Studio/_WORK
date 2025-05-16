import http.client
import urllib.request

conn = http.client.HTTPSConnection("www.python.org")
conn.request("GET", "/")
r1 = conn.getresponse()
print(r1.status, r1.reason)
while chunk := r1.read(200):
    print(repr(chunk))
    
url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"

response = urllib.request.urlopen(url)
dData = response.read()
text = dData.decode('utf-8')
print("dData {0}".format(text))