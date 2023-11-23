import http.server
import socketserver
import webbrowser
import urllib
from urllib.parse import parse_qs, urlparse

# Třída pro obsluhu požadavků s přidáním cesty

#print("http.server.SimpleHTTPRequestHandler dir({0}".format(dir(http.server.SimpleHTTPRequestHandler)))
print("socketserver.TCPServer dir({0}".format(dir(socketserver.TCPServer)))
class MyCode(object):
    code = ""
    def __init__(self):
        pass
    
    @classmethod    
    def setCode(cls, inText):
        cls.code = inText
        
    @classmethod
    def getCode(cls):
        return cls.code
    


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Získání adresy z TCPServer
        server_host, server_port = self.server.server_address

        # Zpracování zbytku kódu...
        parsed_path = urllib.parse.urlparse(self.path)
        print("parsed_path {0}".format(parsed_path))
        
        if "code" in parsed_path.query:
            MyCode.setCode(parsed_path.query.split('=')[1])
            #self.send_response(200)
            #self.end_headers()
            #response_text = f'Hello, this is a response from {server_host}:{server_port}'
            #print(response_text)
            #self.wfile.write(response_text.encode())
        else:
            super().do_GET()
    def getRequestLine():
        return self.requestline

# Definujte funkci pro otevření okna s přihlašovacími údaji

def get_authorization_code():
    # Nastavte potřebné proměnné
    client_id = 'Y5XrdAWZhwscrASWKXnARt2YCV0t3CHP'
    #redirect_uri = 'http://localhost:8080'
    redirect_uri = 'http%3A%2F%2Flocalhost%3A8080%2F'
    # Spusťte HTTP server na lokálním portu pro přesměrování URI
    with socketserver.TCPServer(("", 8080), MyHandler) as httpd:
        try:
            # Otevře prohlížeč s přihlašovacím URL
            webbrowser.open(f"https://developer.api.autodesk.com/authentication/v1/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=data:read")

            # Čekáme na přesměrování na naši URI a získáme autorizační kód
            #httpd.handle_request()  # Blocking call
            #print(f"Serving on {httpd.server_address}")
            httpd.handle_request()
            #authorization_code = parse_qs(urlparse(httpd.path).query).get("code")
            #authorization_code = str(httpd.parse_request())
            
            authorization_code = ""
            print("authorization_code : {0}".format(authorization_code))

            # Zobrazíme autorizační kód
            return authorization_code[0] if authorization_code else None
        except Exception as e:
            print(f"Chyba: {e}")
            return None
get_authorization_code()
OUT = MyCode.getCode()
print('Authorization code: {0}'.format(OUT))