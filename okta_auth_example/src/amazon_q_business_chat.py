"""
Amazon Q Business ChatSync API Integration with Okta Authentication

This script demonstrates how to:
1. Obtain an authentication token from Okta
2. Use that token with AWS SigV4 authentication to make ChatSync API calls to Amazon Q Business
"""

import json
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

# Import our Okta authentication client
from okta_oauth_example import OktaOAuthClient
from config import OKTA_ORG_URL, OKTA_CLIENT_ID, OKTA_CLIENT_SECRET, OKTA_REDIRECT_URI


class AmazonQBusinessClient:
    """Client for making authenticated requests to Amazon Q Business."""
    
    def __init__(self, 
                 region: str,
                 application_id: str,
                 user_id: str,
                 access_token: str = None,
                 aws_access_key: str = None,
                 aws_secret_key: str = None,
                 aws_session_token: str = None):
        """
        Initialize the Amazon Q Business client.
        
        Args:
            region: AWS region where Amazon Q Business is deployed
            application_id: Amazon Q Business application ID
            user_id: User ID for the conversation
            access_token: Okta access token for authentication
            aws_access_key: AWS access key (optional, will use environment variables if not provided)
            aws_secret_key: AWS secret key (optional, will use environment variables if not provided)
            aws_session_token: AWS session token (optional, will use environment variables if not provided)
        """
        self.region = region
        self.application_id = application_id
        self.user_id = user_id
        self.access_token = access_token
        
        # Set up AWS credentials
        self.aws_access_key = aws_access_key or os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = aws_secret_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_session_token = aws_session_token or os.environ.get('AWS_SESSION_TOKEN')
        
        # Validate required parameters
        if not self.region:
            raise ValueError("AWS region must be provided")
        if not self.application_id:
            raise ValueError("Amazon Q Business application ID must be provided")
        if not self.user_id:
            raise ValueError("User ID must be provided")
        if not self.aws_access_key or not self.aws_secret_key:
            raise ValueError("AWS credentials must be provided or available in environment variables")
            
        # Set up the API endpoint
        self.endpoint = f"https://qbusiness.{self.region}.api.aws"
        self.service = "qbusiness"
        
        # Create AWS credentials object
        self.credentials = Credentials(
            access_key=self.aws_access_key,
            secret_key=self.aws_secret_key,
            token=self.aws_session_token
        )
        
        # Initialize conversation state
        self.conversation_id = None
        self.system_message_id = None
    
    def start_conversation(self) -> Dict[str, Any]:
        """
        Start a new conversation with Amazon Q Business.
        
        Returns:
            Response from the API
        """
        # Generate a unique conversation ID
        self.conversation_id = str(uuid.uuid4())
        
        # API path for starting a conversation
        path = f"/applications/{self.application_id}/conversations/{self.conversation_id}"
        
        # Request body
        body = {
            "userId": self.user_id
        }
        
        # Make the request
        response = self._make_signed_request(
            method="PUT",
            path=path,
            body=body
        )
        
        return response
    
    def send_message(self, message_text: str) -> Dict[str, Any]:
        """
        Send a message to Amazon Q Business.
        
        Args:
            message_text: The message to send
            
        Returns:
            Response from the API
        """
        if not self.conversation_id:
            # Start a conversation if one doesn't exist
            self.start_conversation()
            
        # Generate a unique message ID
        message_id = str(uuid.uuid4())
        
        # API path for sending a message
        path = f"/applications/{self.application_id}/conversations/{self.conversation_id}/messages/{message_id}"
        
        # Request body
        body = {
            "content": {
                "text": message_text
            }
        }
        
        # Make the request
        response = self._make_signed_request(
            method="PUT",
            path=path,
            body=body
        )
        
        return response
    
    def get_chat_sync(self, message_text: str) -> Dict[str, Any]:
        """
        Send a message and get a synchronous response using the ChatSync API.
        
        Args:
            message_text: The message to send
            
        Returns:
            Response from the API
        """
        # API path for ChatSync
        path = f"/applications/{self.application_id}/chatsync"
        
        # Request body
        body = {
            "userId": self.user_id,
            "text": message_text
        }
        
        # Add conversation ID if we have one
        if self.conversation_id:
            body["conversationId"] = self.conversation_id
            
        # Add system message ID if we have one
        if self.system_message_id:
            body["systemMessageId"] = self.system_message_id
            
        # Make the request
        response = self._make_signed_request(
            method="POST",
            path=path,
            body=body
        )
        
        # Update conversation state
        if "conversationId" in response:
            self.conversation_id = response["conversationId"]
        if "systemMessageId" in response:
            self.system_message_id = response["systemMessageId"]
            
        return response
    
    def _make_signed_request(self, method: str, path: str, body: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a signed request to the Amazon Q Business API.
        
        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            path: API path
            body: Request body
            
        Returns:
            Response from the API
        """
        # Construct the full URL
        url = f"{self.endpoint}{path}"
        
        # Create the request
        request = AWSRequest(
            method=method,
            url=url,
            data=json.dumps(body) if body else None
        )
        
        # Add headers
        request.headers.add("Content-Type", "application/json")
        request.headers.add("Accept", "application/json")
        
        # Add Okta access token if available
        if self.access_token:
            request.headers.add("Authorization", f"Bearer {self.access_token}")
            
        # Sign the request with SigV4
        SigV4Auth(self.credentials, self.service, self.region).add_auth(request)
        
        # Convert to a requests-compatible format
        prepared_request = request.prepare()
        
        # Make the request
        response = requests.request(
            method=prepared_request.method,
            url=prepared_request.url,
            headers=dict(prepared_request.headers),
            data=prepared_request.body
        )
        
        # Check for errors
        if response.status_code >= 400:
            print(f"Error: {response.status_code} - {response.text}")
            return {"error": response.text, "status_code": response.status_code}
            
        # Parse and return the response
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "raw_response": response.text}


def get_okta_token() -> Optional[str]:
    """
    Get an access token from Okta using the OAuth 2.0 flow.
    
    Returns:
        Access token if successful, None otherwise
    """
    print("Obtaining Okta access token...")
    
    # Create OAuth client
    oauth_client = OktaOAuthClient()
    
    # Check if we have a valid token already
    if oauth_client.is_token_valid():
        print("Using existing valid token")
        return oauth_client.get_token()
        
    # We need to get a new token
    print("\nNo valid token found. You need to authenticate with Okta.")
    print("This will open a browser window for you to log in.")
    input("Press Enter to continue...")
    
    # This would normally be done in a web application with a proper redirect URI
    # For this script, we'll use a simplified approach that requires manual intervention
    
    # Generate PKCE pair
    pkce_pair = oauth_client.generate_pkce_pair()
    
    # Get authorization URL
    auth_url = oauth_client.get_authorization_url(
        state="script-auth",
        code_challenge=pkce_pair['code_challenge']
    )
    
    # Open browser for authentication
    import webbrowser
    webbrowser.open(auth_url)
    
    # Wait for the user to authenticate and get the authorization code
    print("\nAfter logging in, you will be redirected to a page that might show an error.")
    print("Copy the 'code' parameter from the URL and paste it here.")
    print("The URL will look like: http://localhost:8080/authorization-code/callback?code=XXXX&state=script-auth")
    
    auth_code = input("\nEnter the authorization code: ")
    
    # Exchange code for tokens
    tokens = oauth_client.exchange_code_for_tokens(
        code=auth_code,
        code_verifier=pkce_pair['code_verifier']
    )
    
    if 'error' in tokens:
        print(f"Error getting tokens: {tokens['error']}")
        return None
        
    print("Successfully obtained access token")
    return tokens.get('access_token')


def main():
    """Main function to demonstrate Amazon Q Business integration with Okta authentication."""
    # Get configuration from environment or command line
    region = os.environ.get('AWS_REGION') or input("Enter AWS region (e.g., us-east-1): ")
    application_id = os.environ.get('Q_BUSINESS_APP_ID') or input("Enter Amazon Q Business application ID: ")
    user_id = os.environ.get('USER_ID') or input("Enter user ID: ")
    
    # Get Okta token
    access_token = get_okta_token()
    if not access_token:
        print("Failed to obtain Okta access token")
        sys.exit(1)
    
    # Create Amazon Q Business client
    q_client = AmazonQBusinessClient(
        region=region,
        application_id=application_id,
        user_id=user_id,
        access_token=access_token
    )
    
    # Start a conversation
    print("\nStarting a conversation with Amazon Q Business...")
    start_response = q_client.start_conversation()
    if 'error' in start_response:
        print(f"Error starting conversation: {start_response['error']}")
        sys.exit(1)
    
    print(f"Conversation started with ID: {q_client.conversation_id}")
    
    # Interactive chat loop
    print("\nAmazon Q Business Chat (type 'exit' to quit)")
    print("=" * 50)
    
    while True:
        # Get user input
        user_message = input("\nYou: ")
        if user_message.lower() in ('exit', 'quit'):
            break
            
        # Send message and get response
        print("\nAmazon Q: ", end="", flush=True)
        
        response = q_client.get_chat_sync(user_message)
        if 'error' in response:
            print(f"Error: {response['error']}")
            continue
            
        # Display the response
        if 'text' in response:
            print(response['text'])
        else:
            print("No text response received")
            print(f"Full response: {json.dumps(response, indent=2)}")
    
    print("\nChat session ended")


if __name__ == "__main__":
    main()
