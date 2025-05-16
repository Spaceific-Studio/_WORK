import clr

# Import knihoven pro práci s okny
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
clr.AddReference('System.Net.Http')
from System.Windows.Forms import Form, Label, TextBox, Button

# Definujte funkci pro otevření okna s přihlašovacími údaji

def get_authorization_code():
    # Spusťte HTTP server na lokálním portu pro přesměrování URI
    listener = Http.HttpListener()
    listener.Prefixes.Add(redirect_uri)
    listener.Start()
    client_id = 'Y5XrdAWZhwscrASWKXnARt2YCV0t3CHP'
    redirect_uri = 'http%3A%2F%2Flocalhost%3A8080%2Foauth%2Fcallback%2F'

    # Otevře prohlížeč s přihlašovacím URL
    Forms.WebBrowser().Navigate(f"https://developer.api.autodesk.com/authentication/v1/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=data:read")

    # Čekáme na přesměrování na naši URI a získáme autorizační kód
    context = listener.GetContext()
    query = context.Request.Url.Query
    authorization_code = Http.HttpUtility.ParseQueryString(query).Get("code")
    
    # Ukončíme HTTP listener
    listener.Close()

    # Zobrazíme autorizační kód
    return authorization_code
    
OUT = get_authorization_code()
