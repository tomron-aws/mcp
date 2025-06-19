"""
Okta OAuth 2.0/OIDC Authentication Example

This module demonstrates how to obtain authentication tokens from Okta
using the OAuth 2.0 Authorization Code flow with PKCE.
"""

import base64
import hashlib
import os
import secrets
import time
import webbrowser
from typing import Dict, Any, Optional
from urllib.parse import urlencode, parse_qs

import requests
from flask import Flask, request, redirect, session, jsonify

from okta_auth_client import OktaAuthClient
from config import (
    OKTA_ORG_URL,
    OKTA_CLIENT_ID,
    OKTA_CLIENT_SECRET,
    OKTA_REDIRECT_URI,
    OKTA_SCOPES,
    APP_SECRET_KEY,
    APP_HOST,
    APP_PORT,
    APP_DEBUG
)


class OktaOAuthClient(OktaAuthClient):
    """Client for Okta OAuth 2.0/OIDC authentication."""
    
    def __init__(self, client_id: str = None, client_secret: str = None,
                 redirect_uri: str = None, scopes: list = None):
        """
        Initialize the Okta OAuth client.
        
        Args:
            client_id: OAuth client ID from Okta application
            client_secret: OAuth client secret from Okta application
            redirect_uri: Redirect URI for OAuth callback
            scopes: OAuth scopes to request
        """
        super().__init__()
        self.client_id = client_id or OKTA_CLIENT_ID
        self.client_secret = client_secret or OKTA_CLIENT_SECRET
        self.redirect_uri = redirect_uri or OKTA_REDIRECT_URI
        self.scopes = scopes or OKTA_SCOPES
        
        # Authorization server
        self.authorization_server = "default"  # Use 'default' or a custom auth server ID
        
    def generate_pkce_pair(self) -> Dict[str, str]:
        """
        Generate PKCE code verifier and challenge.
        
        Returns:
            Dictionary containing code_verifier and code_challenge
        """
        # Generate a secure random string for the code verifier
        code_verifier = secrets.token_urlsafe(64)
        
        # Create code challenge by hashing verifier with SHA-256
        code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
        code_challenge = code_challenge.rstrip('=')  # Remove padding
        
        return {
            'code_verifier': code_verifier,
            'code_challenge': code_challenge
        }
    
    def get_authorization_url(self, state: str = None, code_challenge: str = None) -> str:
        """
        Generate the authorization URL for the OAuth flow.
        
        Args:
            state: Optional state parameter for CSRF protection
            code_challenge: PKCE code challenge
            
        Returns:
            Authorization URL to redirect the user to
        """
        if not state:
            state = secrets.token_urlsafe(16)
            
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': ' '.join(self.scopes),
            'redirect_uri': self.redirect_uri,
            'state': state
        }
        
        # Add PKCE parameters if provided
        if code_challenge:
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
            
        auth_url = f"{self.org_url}/oauth2/{self.authorization_server}/v1/authorize?{urlencode(params)}"
        return auth_url
    
    def exchange_code_for_tokens(self, code: str, code_verifier: str = None) -> Dict[str, Any]:
        """
        Exchange an authorization code for tokens.
        
        Args:
            code: Authorization code received from the callback
            code_verifier: PKCE code verifier (if PKCE was used)
            
        Returns:
            Dictionary containing tokens and related information
        """
        token_url = f"{self.org_url}/oauth2/{self.authorization_server}/v1/token"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        
        # Add client secret if available (for confidential clients)
        if self.client_secret:
            # Use HTTP Basic Auth for confidential clients
            auth = (self.client_id, self.client_secret)
        else:
            # For public clients, no auth is used
            auth = None
            
        # Add PKCE code verifier if provided
        if code_verifier:
            data['code_verifier'] = code_verifier
            
        try:
            response = requests.post(token_url, headers=headers, data=data, auth=auth)
            response.raise_for_status()
            
            tokens = response.json()
            
            # Add expiration timestamp for easier validation later
            if 'expires_in' in tokens:
                tokens['expires_at'] = time.time() + tokens['expires_in']
                
            # Save tokens
            self.save_tokens(tokens)
            
            return tokens
            
        except requests.RequestException as e:
            print(f"Token exchange error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return {'error': str(e)}
    
    def refresh_tokens(self) -> bool:
        """
        Refresh tokens using the refresh_token.
        
        Returns:
            True if tokens were successfully refreshed, False otherwise
        """
        self.load_tokens()
        
        if 'refresh_token' not in self.tokens:
            print("No refresh token available")
            return False
            
        token_url = f"{self.org_url}/oauth2/{self.authorization_server}/v1/token"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.tokens['refresh_token'],
            'scope': ' '.join(self.scopes)
        }
        
        # Add client authentication
        if self.client_secret:
            auth = (self.client_id, self.client_secret)
        else:
            auth = None
            data['client_id'] = self.client_id
            
        try:
            response = requests.post(token_url, headers=headers, data=data, auth=auth)
            response.raise_for_status()
            
            new_tokens = response.json()
            
            # Add expiration timestamp
            if 'expires_in' in new_tokens:
                new_tokens['expires_at'] = time.time() + new_tokens['expires_in']
                
            # If the response doesn't include a new refresh token, keep the old one
            if 'refresh_token' not in new_tokens and 'refresh_token' in self.tokens:
                new_tokens['refresh_token'] = self.tokens['refresh_token']
                
            # Save new tokens
            self.save_tokens(new_tokens)
            
            return True
            
        except requests.RequestException as e:
            print(f"Token refresh error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return False
    
    def revoke_tokens(self) -> bool:
        """
        Revoke tokens at the Okta authorization server.
        
        Returns:
            True if tokens were successfully revoked, False otherwise
        """
        self.load_tokens()
        
        if not self.tokens:
            return True  # No tokens to revoke
            
        revoke_url = f"{self.org_url}/oauth2/{self.authorization_server}/v1/revoke"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Determine which token to revoke (prefer access_token)
        token_to_revoke = self.tokens.get('access_token', self.tokens.get('refresh_token'))
        
        if not token_to_revoke:
            return False
            
        data = {
            'token': token_to_revoke,
            'token_type_hint': 'access_token' if 'access_token' in self.tokens else 'refresh_token'
        }
        
        # Add client authentication
        if self.client_secret:
            auth = (self.client_id, self.client_secret)
        else:
            auth = None
            data['client_id'] = self.client_id
            
        try:
            response = requests.post(revoke_url, headers=headers, data=data, auth=auth)
            response.raise_for_status()
            
            # Clear local tokens
            super().revoke_tokens()
            
            return True
            
        except requests.RequestException as e:
            print(f"Token revocation error: {e}")
            return False
    
    def introspect_token(self, token: str, token_type_hint: str = 'access_token') -> Dict[str, Any]:
        """
        Introspect a token to get its metadata and validity.
        
        Args:
            token: The token to introspect
            token_type_hint: Type of token ('access_token', 'refresh_token', 'id_token')
            
        Returns:
            Dictionary containing token metadata
        """
        introspect_url = f"{self.org_url}/oauth2/{self.authorization_server}/v1/introspect"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'token': token,
            'token_type_hint': token_type_hint
        }
        
        # Add client authentication
        if self.client_secret:
            auth = (self.client_id, self.client_secret)
        else:
            auth = None
            data['client_id'] = self.client_id
            
        try:
            response = requests.post(introspect_url, headers=headers, data=data, auth=auth)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            print(f"Token introspection error: {e}")
            return {'active': False, 'error': str(e)}
    
    def get_userinfo(self) -> Dict[str, Any]:
        """
        Get user information using the access token.
        
        Returns:
            Dictionary containing user information
        """
        access_token = self.get_token('access_token')
        
        if not access_token:
            return {'error': 'No access token available'}
            
        userinfo_url = f"{self.org_url}/oauth2/{self.authorization_server}/v1/userinfo"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(userinfo_url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            print(f"Userinfo error: {e}")
            return {'error': str(e)}


def start_oauth_flow():
    """Start the OAuth 2.0 flow with a local Flask server for the callback."""
    app = Flask(__name__)
    app.secret_key = APP_SECRET_KEY
    
    # Create OAuth client
    oauth_client = OktaOAuthClient()
    
    @app.route('/')
    def index():
        """Display the home page with login button."""
        return """
        <h1>Okta OAuth 2.0 Example</h1>
        <a href="/login">Login with Okta</a>
        """
    
    @app.route('/login')
    def login():
        """Initiate the OAuth flow."""
        # Generate PKCE pair
        pkce_pair = oauth_client.generate_pkce_pair()
        
        # Store PKCE verifier and state in session
        session['code_verifier'] = pkce_pair['code_verifier']
        session['state'] = secrets.token_urlsafe(16)
        
        # Get authorization URL
        auth_url = oauth_client.get_authorization_url(
            state=session['state'],
            code_challenge=pkce_pair['code_challenge']
        )
        
        # Redirect to Okta for authentication
        return redirect(auth_url)
    
    @app.route('/authorization-code/callback')
    def callback():
        """Handle the OAuth callback."""
        # Verify state to prevent CSRF
        if request.args.get('state') != session.get('state'):
            return "State mismatch. Possible CSRF attack.", 400
            
        # Exchange code for tokens
        code = request.args.get('code')
        if not code:
            return "No authorization code received.", 400
            
        # Exchange code for tokens using PKCE verifier
        tokens = oauth_client.exchange_code_for_tokens(
            code=code,
            code_verifier=session.get('code_verifier')
        )
        
        if 'error' in tokens:
            return f"Error exchanging code for tokens: {tokens['error']}", 400
            
        # Redirect to profile page
        return redirect('/profile')
    
    @app.route('/profile')
    def profile():
        """Display user profile information."""
        # Get user info using the access token
        userinfo = oauth_client.get_userinfo()
        
        if 'error' in userinfo:
            return f"Error getting user info: {userinfo['error']}", 400
            
        # Display user info and tokens
        tokens = oauth_client.load_tokens()
        
        html = """
        <h1>User Profile</h1>
        <h2>User Information</h2>
        <pre>{userinfo}</pre>
        
        <h2>Tokens</h2>
        <h3>Access Token</h3>
        <pre>{access_token}</pre>
        
        <h3>ID Token</h3>
        <pre>{id_token}</pre>
        
        <p><a href="/refresh">Refresh Tokens</a></p>
        <p><a href="/revoke">Logout (Revoke Tokens)</a></p>
        """
        
        return html.format(
            userinfo=jsonify(userinfo).data.decode('utf-8'),
            access_token=tokens.get('access_token', 'Not available'),
            id_token=tokens.get('id_token', 'Not available')
        )
    
    @app.route('/refresh')
    def refresh():
        """Refresh the tokens."""
        success = oauth_client.refresh_tokens()
        
        if success:
            return redirect('/profile')
        else:
            return "Error refreshing tokens. You may need to login again.", 400
    
    @app.route('/revoke')
    def revoke():
        """Revoke the tokens and logout."""
        oauth_client.revoke_tokens()
        
        return """
        <h1>Logged Out</h1>
        <p>Your tokens have been revoked.</p>
        <p><a href="/">Return to Home</a></p>
        """
    
    # Open browser to the app
    webbrowser.open(f"http://{APP_HOST}:{APP_PORT}")
    
    # Start the Flask app
    app.run(host=APP_HOST, port=APP_PORT, debug=APP_DEBUG)


if __name__ == '__main__':
    start_oauth_flow()
