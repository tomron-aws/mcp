"""
Okta SAML Authentication Example

This module demonstrates how to handle SAML authentication with Okta.
It sets up a simple service provider (SP) that can process SAML assertions
from Okta as the identity provider (IdP).
"""

import base64
import os
import tempfile
import webbrowser
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

from flask import Flask, request, redirect, session, Response
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
from saml2.metadata import create_metadata_string

from okta_auth_client import OktaAuthClient
from config import (
    OKTA_ORG_URL,
    OKTA_IDP_METADATA_URL,
    OKTA_SP_ENTITY_ID,
    OKTA_SP_ACS_URL,
    APP_SECRET_KEY,
    APP_HOST,
    APP_PORT,
    APP_DEBUG
)


class OktaSamlClient(OktaAuthClient):
    """Client for Okta SAML authentication."""
    
    def __init__(self, idp_metadata_url: str = None, sp_entity_id: str = None,
                 sp_acs_url: str = None):
        """
        Initialize the Okta SAML client.
        
        Args:
            idp_metadata_url: URL to the IdP metadata XML
            sp_entity_id: Entity ID for this service provider
            sp_acs_url: Assertion Consumer Service URL for this service provider
        """
        super().__init__()
        self.idp_metadata_url = idp_metadata_url or OKTA_IDP_METADATA_URL
        self.sp_entity_id = sp_entity_id or OKTA_SP_ENTITY_ID
        self.sp_acs_url = sp_acs_url or OKTA_SP_ACS_URL
        
        # Initialize SAML client
        self.saml_client = self._create_saml_client()
        
    def _create_saml_client(self) -> Saml2Client:
        """
        Create and configure the SAML client.
        
        Returns:
            Configured SAML2 client
        """
        # Create a temporary file to store our metadata
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as temp_metadata:
            # Generate SP metadata
            sp_metadata = create_metadata_string(
                None,
                None,
                self.sp_entity_id,
                want_response_signed=False,
                want_assertions_signed=False,
                want_assertions_or_response_signed=True,
                attribute_converters=None,
                digest_methods=None,
                sign_methods=None
            )
            temp_metadata.write(sp_metadata.encode('utf-8'))
            temp_metadata_path = temp_metadata.name
        
        # Configure the SAML client
        settings = {
            'entityid': self.sp_entity_id,
            'metadata': {
                'local': [temp_metadata_path],
                'remote': [{'url': self.idp_metadata_url}]
            },
            'service': {
                'sp': {
                    'endpoints': {
                        'assertion_consumer_service': [
                            (self.sp_acs_url, BINDING_HTTP_POST)
                        ]
                    },
                    'allow_unsolicited': True,
                    'authn_requests_signed': False,
                    'want_assertions_signed': True,
                    'want_response_signed': False
                }
            }
        }
        
        config = Saml2Config()
        config.load(settings)
        config.allow_unknown_attributes = True
        
        return Saml2Client(config=config)
    
    def get_auth_request_url(self, relay_state: str = '/') -> str:
        """
        Generate a SAML authentication request URL.
        
        Args:
            relay_state: URL to redirect to after successful authentication
            
        Returns:
            URL to redirect the user to for SAML authentication
        """
        # Generate the SAML request
        reqid, info = self.saml_client.prepare_for_authenticate(relay_state=relay_state)
        
        # Store the request ID in the session for later verification
        session['saml_request_id'] = reqid
        
        # Get the URL from the SAML client's response
        for key, value in info['headers']:
            if key == 'Location':
                return value
                
        raise ValueError("No redirect URL found in SAML request")
    
    def process_saml_response(self, saml_response: str) -> Dict[str, Any]:
        """
        Process a SAML response from the IdP.
        
        Args:
            saml_response: Base64-encoded SAML response from the IdP
            
        Returns:
            Dictionary containing user attributes from the SAML assertion
        """
        # Process the SAML response
        authn_response = self.saml_client.parse_authn_request_response(
            saml_response,
            BINDING_HTTP_POST,
            outstanding=session.get('saml_request_id', {})
        )
        
        if authn_response is None:
            return {'error': 'Invalid SAML response'}
            
        # Extract user attributes from the SAML assertion
        attributes = authn_response.get_identity()
        
        # Extract the SAML session index for logout
        session_index = authn_response.assertion.authn_statement[0].session_index
        
        # Extract the NameID
        name_id = authn_response.get_subject().text
        name_id_format = authn_response.get_subject().format
        
        # Create a token-like structure to store SAML session info
        tokens = {
            'saml_session_index': session_index,
            'name_id': name_id,
            'name_id_format': name_id_format,
            'attributes': attributes,
            'issuer': authn_response.response.issuer.text,
            'authenticated': True
        }
        
        # Save the tokens
        self.save_tokens(tokens)
        
        return attributes
    
    def get_logout_url(self) -> str:
        """
        Generate a SAML logout request URL.
        
        Returns:
            URL to redirect the user to for SAML logout
        """
        # Load the current SAML session
        self.load_tokens()
        
        if not self.tokens or 'name_id' not in self.tokens:
            return '/'  # No active session, redirect to home
            
        # Prepare the logout request
        name_id = self.tokens.get('name_id')
        session_index = self.tokens.get('saml_session_index')
        
        reqid, info = self.saml_client.prepare_for_logout(
            name_id=name_id,
            session_index=session_index,
            relay_state='/'
        )
        
        # Store the request ID in the session for later verification
        session['saml_logout_request_id'] = reqid
        
        # Get the URL from the SAML client's response
        for key, value in info['headers']:
            if key == 'Location':
                return value
                
        raise ValueError("No redirect URL found in SAML logout request")
    
    def process_logout_response(self, saml_response: str) -> bool:
        """
        Process a SAML logout response from the IdP.
        
        Args:
            saml_response: Base64-encoded SAML logout response
            
        Returns:
            True if logout was successful, False otherwise
        """
        # Process the SAML logout response
        logout_response = self.saml_client.parse_logout_request_response(
            saml_response,
            BINDING_HTTP_REDIRECT
        )
        
        if logout_response is None:
            return False
            
        # Clear the local session
        super().revoke_tokens()
        
        return True


def start_saml_flow():
    """Start the SAML authentication flow with a local Flask server."""
    app = Flask(__name__)
    app.secret_key = APP_SECRET_KEY
    
    # Create SAML client
    saml_client = OktaSamlClient()
    
    @app.route('/')
    def index():
        """Display the home page with login button."""
        return """
        <h1>Okta SAML Example</h1>
        <a href="/login">Login with Okta (SAML)</a>
        """
    
    @app.route('/login')
    def login():
        """Initiate the SAML authentication flow."""
        try:
            # Generate SAML authentication request URL
            auth_url = saml_client.get_auth_request_url(relay_state='/profile')
            
            # Redirect to Okta for authentication
            return redirect(auth_url)
            
        except Exception as e:
            return f"Error initiating SAML authentication: {str(e)}", 500
    
    @app.route('/saml/acs', methods=['POST'])
    def saml_acs():
        """Handle the SAML assertion consumer service endpoint."""
        try:
            # Get the SAML response from the form
            saml_response = request.form.get('SAMLResponse')
            if not saml_response:
                return "No SAML response received", 400
                
            # Get the relay state (where to redirect after processing)
            relay_state = request.form.get('RelayState', '/')
            
            # Process the SAML response
            attributes = saml_client.process_saml_response(saml_response)
            
            if 'error' in attributes:
                return f"Error processing SAML response: {attributes['error']}", 400
                
            # Store user attributes in session for display
            session['saml_attributes'] = attributes
            
            # Redirect to the relay state URL
            return redirect(relay_state)
            
        except Exception as e:
            return f"Error processing SAML assertion: {str(e)}", 500
    
    @app.route('/profile')
    def profile():
        """Display user profile information from SAML attributes."""
        # Load tokens and attributes
        tokens = saml_client.load_tokens()
        attributes = session.get('saml_attributes', {})
        
        if not tokens or not tokens.get('authenticated'):
            return redirect('/login')
            
        # Build HTML to display user information
        html = """
        <h1>User Profile (SAML)</h1>
        <h2>User Information</h2>
        <table border="1">
            <tr>
                <th>Attribute</th>
                <th>Value</th>
            </tr>
        """
        
        # Add each attribute to the table
        for attr, values in attributes.items():
            html += f"<tr><td>{attr}</td><td>{', '.join(values)}</td></tr>"
            
        html += """
        </table>
        
        <h2>SAML Session Information</h2>
        <table border="1">
            <tr>
                <th>Property</th>
                <th>Value</th>
            </tr>
        """
        
        # Add SAML session info
        for key, value in tokens.items():
            if key != 'attributes':  # Skip the attributes we already displayed
                html += f"<tr><td>{key}</td><td>{value}</td></tr>"
                
        html += """
        </table>
        
        <p><a href="/logout">Logout</a></p>
        """
        
        return html
    
    @app.route('/logout')
    def logout():
        """Initiate SAML logout."""
        try:
            # Generate SAML logout request URL
            logout_url = saml_client.get_logout_url()
            
            # Clear the session
            session.clear()
            
            # Redirect to Okta for logout
            return redirect(logout_url)
            
        except Exception as e:
            # If there's an error, just clear the local session
            session.clear()
            saml_client.revoke_tokens()
            
            return """
            <h1>Logged Out</h1>
            <p>Your local session has been cleared.</p>
            <p><a href="/">Return to Home</a></p>
            """
    
    @app.route('/saml/metadata')
    def metadata():
        """Serve the SP metadata XML."""
        # Generate SP metadata
        metadata_xml = create_metadata_string(
            None,
            None,
            saml_client.sp_entity_id,
            want_response_signed=False,
            want_assertions_signed=True,
            want_assertions_or_response_signed=True,
            attribute_converters=None,
            digest_methods=None,
            sign_methods=None
        )
        
        return Response(metadata_xml, mimetype='text/xml')
    
    # Open browser to the app
    webbrowser.open(f"http://{APP_HOST}:{APP_PORT}")
    
    # Start the Flask app
    app.run(host=APP_HOST, port=APP_PORT, debug=APP_DEBUG)


if __name__ == '__main__':
    start_saml_flow()
