from flask import Flask, request, redirect
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load configuration variables from .env
load_dotenv()

@app.route('/')
def authenticate():
  return redirect(f"https://developer.api.autodesk.com/authentication/v2/authorize?response_type=code&client_id={os.getenv('CLIENT_ID')}&redirect_uri={os.getenv('CALLBACK_URL')}&scope={os.getenv('SCOPES')}")

@app.route('/api/auth/callback', methods=['POST','GET'])
def callback():
  # Get credential code
  code = request.args.get('code')
  payload = f"grant_type=authorization_code&code={code}&client_id={os.getenv('CLIENT_ID')}&client_secret={os.getenv('CLIENT_SECRET')}&redirect_uri={os.getenv('CALLBACK_URL')}"
  tokenUrl = "https://developer.api.autodesk.com/authentication/v2/token"
  headers = {
      "Content-Type": "application/x-www-form-urlencoded"
  }
  resp = requests.request("POST", tokenUrl, data=payload, headers=headers)
  respJson = resp.json()
  # Return success response
  return f"{respJson}", 200

if __name__ == '__main__':
  app.run(debug=True, port=8080)