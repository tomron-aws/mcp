from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
import uvicorn
import requests
import secrets
import os
import base64
import hashlib
from urllib.parse import urlencode

app = FastAPI()

# Salesforce OAuth Configuration
SALESFORCE_DOMAIN = 'aws200-dev-ed.develop.my.salesforce.com' #os.getenv("SALESFORCE_DOMAIN", "login.salesforce.com")
SALESFORCE_CLIENT_ID = '' #os.getenv("SALESFORCE_CLIENT_ID")
SALESFORCE_CLIENT_SECRET = '' #os.getenv("SALESFORCE_CLIENT_SECRET")
LOCAL_PORT = "8080"

# OAuth endpoints
AUTHORIZATION_ENDPOINT = f"https://{SALESFORCE_DOMAIN}/services/oauth2/authorize"
TOKEN_ENDPOINT = f"https://{SALESFORCE_DOMAIN}/services/oauth2/token"
REDIRECT_URI = f"http://localhost:{LOCAL_PORT}/auth/salesforce/callback"

# Store tokens and PKCE verifiers temporarily (in production, use proper session management)
user_tokens = {}
pkce_verifiers = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <body>
            <h1>Salesforce OAuth Demo</h1>
            <a href="/login">Login with Salesforce</a>
        </body>
    </html>
    """

@app.get("/login")
async def login():
    state = secrets.token_urlsafe(16)
    
    # Generate PKCE code verifier and challenge
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    # Store the verifier for later use
    pkce_verifiers[state] = code_verifier
    
    params = {
        'response_type': 'code',
        'client_id': SALESFORCE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid email profile api',
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    
    auth_url = f"{AUTHORIZATION_ENDPOINT}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@app.get("/auth/salesforce/callback")
async def salesforce_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    
    if error:
        return HTMLResponse(f"<h1>Error</h1><p>{error}</p>")
    
    if not code:
        return HTMLResponse("<h1>Error</h1><p>No authorization code received</p>")
    
    # Get the PKCE verifier
    code_verifier = pkce_verifiers.get(state)
    if not code_verifier:
        return HTMLResponse("<h1>Error</h1><p>Invalid state parameter</p>")
    
    # Exchange code for tokens with PKCE
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': SALESFORCE_CLIENT_ID,
        'code_verifier': code_verifier
    }
    
    # Only include client_secret if it's set (some Salesforce apps don't require it with PKCE)
    if SALESFORCE_CLIENT_SECRET:
        token_data['client_secret'] = SALESFORCE_CLIENT_SECRET
    
    token_response = requests.post(TOKEN_ENDPOINT, data=token_data)
    
    if token_response.status_code != 200:
        return HTMLResponse(f"<h1>Token Error</h1><p>{token_response.text}</p>")
    
    tokens = token_response.json()
    
    # Store tokens (use proper session management in production)
    session_id = secrets.token_urlsafe(16)
    user_tokens[session_id] = tokens
    
    # Clean up the PKCE verifier
    pkce_verifiers.pop(state, None)
    
    # Get user info
    user_info = get_user_info(tokens['access_token'], tokens['instance_url'])
    
    return HTMLResponse(f"""
    <h1>Authentication Successful!</h1>
    <p>Welcome, {user_info.get('display_name', 'User')}!</p>
    <p>Email: {user_info.get('email', 'N/A')}</p>
    <p>Organization: {user_info.get('organization_id', 'N/A')}</p>
    <h3>Tokens:</h3>
    <p><strong>Access Token:</strong> {tokens['access_token'][:50]}...</p>
    <p><strong>Refresh Token:</strong> {tokens.get('refresh_token', 'N/A')[:50] if tokens.get('refresh_token') else 'N/A'}...</p>
    <p><strong>Instance URL:</strong> {tokens['instance_url']}</p>
    <br>
    <a href="/api/tokens/{session_id}">Get Tokens as JSON</a> | 
    <a href="/">Home</a>
    """)

@app.get("/api/tokens/{session_id}")
async def get_tokens(session_id: str):
    if session_id not in user_tokens:
        return JSONResponse({"error": "Session not found"}, status_code=404)
    
    return JSONResponse(user_tokens[session_id])

def get_user_info(access_token: str, instance_url: str):
    """Get user information from Salesforce"""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Get user identity
    identity_response = requests.get(f"{instance_url}/services/oauth2/userinfo", headers=headers)
    
    if identity_response.status_code == 200:
        return identity_response.json()
    return {}

if __name__ == "__main__":
    print(f"Starting Salesforce OAuth app on http://localhost:{LOCAL_PORT}")
    print("Make sure to set these environment variables:")
    print("- SALESFORCE_CLIENT_ID")
    print("- SALESFORCE_CLIENT_SECRET")
    print("- SALESFORCE_DOMAIN (optional, defaults to login.salesforce.com)")
    print("- LOCAL_PORT (optional, defaults to 8080)")
    
    uvicorn.run(app, host="localhost", port=LOCAL_PORT)