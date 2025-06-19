"""
Okta API Authentication Example

This module demonstrates how to use the Okta Management API to perform
administrative operations and obtain tokens for users.
"""

import json
import time
from typing import Dict, List, Any, Optional

import requests
from requests.exceptions import RequestException

from okta_auth_client import OktaAuthClient
from config import OKTA_ORG_URL, OKTA_API_TOKEN


class OktaApiClient(OktaAuthClient):
    """Client for Okta Management API operations."""
    
    def __init__(self, org_url: str = None, api_token: str = None):
        """
        Initialize the Okta API client.
        
        Args:
            org_url: Okta organization URL (e.g., https://your-org.okta.com)
            api_token: Okta API token for management operations
        """
        super().__init__(org_url, api_token)
        
    def list_users(self, query: str = None, limit: int = 25) -> List[Dict[str, Any]]:
        """
        List users in the Okta organization.
        
        Args:
            query: Search query to filter users
            limit: Maximum number of users to return
            
        Returns:
            List of user objects
        """
        params = {'limit': limit}
        if query:
            params['search'] = query
            
        response = self.make_api_request('users', params=params)
        
        if isinstance(response, list):
            return response
        elif 'error' in response:
            print(f"Error listing users: {response['error']}")
            return []
        else:
            return []
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user by ID or login.
        
        Args:
            user_id: User ID or login email
            
        Returns:
            User object
        """
        return self.make_api_request(f'users/{user_id}')
    
    def create_user(self, profile: Dict[str, Any], credentials: Dict[str, Any] = None,
                   activate: bool = True) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            profile: User profile information
            credentials: User credentials
            activate: Whether to activate the user immediately
            
        Returns:
            Created user object
        """
        data = {
            'profile': profile
        }
        
        if credentials:
            data['credentials'] = credentials
            
        params = {'activate': 'true' if activate else 'false'}
        
        return self.make_api_request('users', method='POST', data=data, params=params)
    
    def update_user(self, user_id: str, profile: Dict[str, Any] = None,
                   credentials: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update an existing user.
        
        Args:
            user_id: User ID or login
            profile: User profile information to update
            credentials: User credentials to update
            
        Returns:
            Updated user object
        """
        data = {}
        
        if profile:
            data['profile'] = profile
            
        if credentials:
            data['credentials'] = credentials
            
        return self.make_api_request(f'users/{user_id}', method='PUT', data=data)
    
    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user.
        
        Args:
            user_id: User ID or login
            
        Returns:
            True if successful, False otherwise
        """
        response = self.make_api_request(f'users/{user_id}/lifecycle/deactivate', method='POST')
        return 'error' not in response
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID or login
            
        Returns:
            True if successful, False otherwise
        """
        response = self.make_api_request(f'users/{user_id}', method='DELETE')
        return 'error' not in response
    
    def list_applications(self, filter_query: str = None) -> List[Dict[str, Any]]:
        """
        List applications in the Okta organization.
        
        Args:
            filter_query: Filter query for applications
            
        Returns:
            List of application objects
        """
        params = {}
        if filter_query:
            params['filter'] = filter_query
            
        response = self.make_api_request('apps', params=params)
        
        if isinstance(response, list):
            return response
        elif 'error' in response:
            print(f"Error listing applications: {response['error']}")
            return []
        else:
            return []
    
    def get_application(self, app_id: str) -> Dict[str, Any]:
        """
        Get an application by ID.
        
        Args:
            app_id: Application ID
            
        Returns:
            Application object
        """
        return self.make_api_request(f'apps/{app_id}')
    
    def list_application_users(self, app_id: str) -> List[Dict[str, Any]]:
        """
        List users assigned to an application.
        
        Args:
            app_id: Application ID
            
        Returns:
            List of user objects
        """
        response = self.make_api_request(f'apps/{app_id}/users')
        
        if isinstance(response, list):
            return response
        elif 'error' in response:
            print(f"Error listing application users: {response['error']}")
            return []
        else:
            return []
    
    def assign_user_to_application(self, app_id: str, user_id: str,
                                 profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Assign a user to an application.
        
        Args:
            app_id: Application ID
            user_id: User ID or login
            profile: Application user profile
            
        Returns:
            Assignment object
        """
        data = {
            'id': user_id
        }
        
        if profile:
            data['profile'] = profile
            
        return self.make_api_request(f'apps/{app_id}/users', method='POST', data=data)
    
    def generate_token_for_user(self, user_id: str, app_id: str) -> Dict[str, Any]:
        """
        Generate an access token for a user for a specific application.
        
        Args:
            user_id: User ID or login
            app_id: Application ID
            
        Returns:
            Token object
        """
        # This is a simplified example. In a real implementation, you would need to:
        # 1. Ensure the application is OAuth/OIDC enabled
        # 2. Use the appropriate grant type for your use case
        # 3. Handle token storage and refresh properly
        
        # For this example, we'll use the client credentials flow with token minting
        # Note: This requires appropriate permissions and configuration in Okta
        
        # Get the application's client ID and secret
        app = self.get_application(app_id)
        
        if 'error' in app:
            return {'error': f"Error getting application: {app['error']}"}
            
        client_id = app.get('credentials', {}).get('oauthClient', {}).get('client_id')
        client_secret = app.get('credentials', {}).get('oauthClient', {}).get('client_secret')
        
        if not client_id or not client_secret:
            return {'error': 'Application is not configured for OAuth'}
            
        # Get the authorization server ID
        # For simplicity, we'll use the 'default' server
        auth_server_id = 'default'
        
        # Generate a token using the client credentials flow
        token_url = f"{self.org_url}/oauth2/{auth_server_id}/v1/token"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'okta.users.read'  # Adjust scope as needed
        }
        
        auth = (client_id, client_secret)
        
        try:
            response = requests.post(token_url, headers=headers, data=data, auth=auth)
            response.raise_for_status()
            
            tokens = response.json()
            
            # Add expiration timestamp
            if 'expires_in' in tokens:
                tokens['expires_at'] = time.time() + tokens['expires_in']
                
            # Add user context
            tokens['user_id'] = user_id
            tokens['app_id'] = app_id
            
            # Save tokens
            self.save_tokens(tokens)
            
            return tokens
            
        except RequestException as e:
            print(f"Token generation error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return {'error': str(e)}
    
    def make_api_request(self, endpoint: str, method: str = 'GET', 
                        data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Any:
        """
        Make a request to the Okta API.
        
        Args:
            endpoint: API endpoint (without the base URL)
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Data to send with the request
            params: Query parameters
            
        Returns:
            API response
        """
        url = f"{self.org_url}/api/v1/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.api_headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.api_headers, json=data, params=params)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.api_headers, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.api_headers, params=params)
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


def run_api_examples():
    """Run examples of using the Okta Management API."""
    # Create API client
    api_client = OktaApiClient()
    
    print("Okta API Example")
    print("=" * 50)
    
    # Example 1: List users
    print("\n1. Listing users:")
    users = api_client.list_users(limit=5)
    if users and not isinstance(users, dict):
        for user in users:
            print(f"  - {user.get('profile', {}).get('firstName')} {user.get('profile', {}).get('lastName')} ({user.get('profile', {}).get('email')})")
    else:
        print("  No users found or error occurred.")
    
    # Example 2: List applications
    print("\n2. Listing applications:")
    apps = api_client.list_applications()
    if apps and not isinstance(apps, dict):
        for app in apps:
            print(f"  - {app.get('name')} ({app.get('id')})")
    else:
        print("  No applications found or error occurred.")
    
    # Example 3: Create a user (commented out to prevent accidental creation)
    """
    print("\n3. Creating a user:")
    new_user = api_client.create_user(
        profile={
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'testuser@example.com',
            'login': 'testuser@example.com'
        },
        credentials={
            'password': {'value': 'TemporaryPassword123!'}
        },
        activate=True
    )
    if 'id' in new_user:
        print(f"  User created: {new_user.get('profile', {}).get('email')} (ID: {new_user.get('id')})")
    else:
        print(f"  Error creating user: {new_user.get('error', 'Unknown error')}")
    """
    
    # Example 4: Generate token for a user (requires valid user_id and app_id)
    print("\n4. To generate a token for a user, you would use:")
    print("  api_client.generate_token_for_user('user_id', 'app_id')")
    
    print("\nNote: Some operations are commented out to prevent accidental modifications.")
    print("Review the code and uncomment sections as needed for your use case.")


if __name__ == '__main__':
    run_api_examples()
