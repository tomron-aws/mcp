"""
Core Okta Authentication Client

This module provides a base class for Okta authentication operations.
It handles common functionality like token storage, validation, and refresh.
"""

import json
import os
import time
from typing import Dict, List, Optional, Any

import requests
from requests.exceptions import RequestException

from config import (
    OKTA_ORG_URL,
    OKTA_API_TOKEN,
    TOKEN_STORAGE_FILE
)


class OktaAuthClient:
    """Base class for Okta authentication operations."""
    
    def __init__(self, org_url: str = None, api_token: str = None):
        """
        Initialize the Okta authentication client.
        
        Args:
            org_url: Okta organization URL (e.g., https://your-org.okta.com)
            api_token: Okta API token for management operations
        """
        self.org_url = org_url or OKTA_ORG_URL
        self.api_token = api_token or OKTA_API_TOKEN
        self.tokens = {}
        
        # Ensure org_url doesn't end with a slash
        if self.org_url.endswith('/'):
            self.org_url = self.org_url[:-1]
            
        # Set up API headers
        self.api_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'SSWS {self.api_token}'
        }
    
    def load_tokens(self) -> Dict[str, Any]:
        """
        Load tokens from storage file.
        
        Returns:
            Dictionary containing stored tokens
        """
        if os.path.exists(TOKEN_STORAGE_FILE):
            try:
                with open(TOKEN_STORAGE_FILE, 'r') as f:
                    self.tokens = json.load(f)
                return self.tokens
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading tokens: {e}")
        
        return {}
    
    def save_tokens(self, tokens: Dict[str, Any]) -> None:
        """
        Save tokens to storage file.
        
        Args:
            tokens: Dictionary containing tokens to save
        """
        self.tokens = tokens
        try:
            with open(TOKEN_STORAGE_FILE, 'w') as f:
                json.dump(tokens, f, indent=2)
        except IOError as e:
            print(f"Error saving tokens: {e}")
    
    def is_token_valid(self, token_type: str = 'access_token') -> bool:
        """
        Check if a token is valid and not expired.
        
        Args:
            token_type: Type of token to check ('access_token', 'id_token', etc.)
            
        Returns:
            True if token is valid and not expired, False otherwise
        """
        self.load_tokens()
        
        if not self.tokens or token_type not in self.tokens:
            return False
            
        # Check expiration if we have it
        if 'expires_at' in self.tokens:
            current_time = time.time()
            # Add a 60-second buffer to avoid edge cases
            if current_time >= (self.tokens['expires_at'] - 60):
                return False
                
        return True
    
    def get_token(self, token_type: str = 'access_token') -> Optional[str]:
        """
        Get a specific token, refreshing if necessary and possible.
        
        Args:
            token_type: Type of token to retrieve ('access_token', 'id_token', etc.)
            
        Returns:
            The requested token if available, None otherwise
        """
        if not self.is_token_valid(token_type):
            # Try to refresh the token if we have a refresh token
            if 'refresh_token' in self.tokens:
                self.refresh_tokens()
                
        self.load_tokens()
        return self.tokens.get(token_type)
    
    def refresh_tokens(self) -> bool:
        """
        Refresh tokens using the refresh_token if available.
        
        Returns:
            True if tokens were successfully refreshed, False otherwise
        """
        # This is a base implementation that should be overridden by subclasses
        # that implement specific OAuth flows
        return False
    
    def revoke_tokens(self) -> bool:
        """
        Revoke all tokens and clear local storage.
        
        Returns:
            True if tokens were successfully revoked, False otherwise
        """
        # This is a base implementation that should be overridden by subclasses
        if os.path.exists(TOKEN_STORAGE_FILE):
            try:
                os.remove(TOKEN_STORAGE_FILE)
                self.tokens = {}
                return True
            except IOError as e:
                print(f"Error removing token file: {e}")
        
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
        # This is a base implementation that should be overridden by subclasses
        # that implement specific OAuth flows
        return {'active': False}
    
    def make_api_request(self, endpoint: str, method: str = 'GET', 
                        data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to the Okta API.
        
        Args:
            endpoint: API endpoint (without the base URL)
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Data to send with the request
            
        Returns:
            Dictionary containing the API response
        """
        url = f"{self.org_url}/api/v1/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.api_headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.api_headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.api_headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.api_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except RequestException as e:
            print(f"API request error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return {'error': str(e)}
