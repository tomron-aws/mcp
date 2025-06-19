"""
Amazon Q Business SDK Integration with Okta Authentication

This script demonstrates how to:
1. Obtain an authentication token from Okta
2. Use the Amazon Q Business SDK (via boto3) to interact with the service
"""

import os
import sys
import json
import uuid
from typing import Dict, Any, Optional

import boto3
from botocore.auth import SigV4Auth
from botocore.session import Session
from botocore.credentials import Credentials

# Import our Okta authentication client
from okta_oauth_example import OktaOAuthClient
from config import OKTA_ORG_URL, OKTA_CLIENT_ID, OKTA_CLIENT_SECRET, OKTA_REDIRECT_URI


class OktaCredentialsProvider:
    """Custom credentials provider that uses Okta tokens."""
    
    def __init__(self, access_token: str):
        """
        Initialize with an Okta access token.
        
        Args:
            access_token: Okta access token
        """
        self.access_token = access_token
        
        # Get AWS credentials from environment
        self.aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_session_token = os.environ.get('AWS_SESSION_TOKEN')
        
        if not self.aws_access_key or not self.aws_secret_key:
            raise ValueError("AWS credentials not found in environment variables")
    
    def get_credentials(self):
        """
        Get AWS credentials with Okta token.
        
        Returns:
            Credentials object with Okta token
        """
        credentials = Credentials(
            access_key=self.aws_access_key,
            secret_key=self.aws_secret_key,
            token=self.aws_session_token
        )
        
        # Add Okta token to the credentials
        credentials.okta_token = self.access_token
        
        return credentials


class AmazonQBusinessSDKClient:
    """Client for interacting with Amazon Q Business using the SDK."""
    
    def __init__(self, 
                 region: str,
                 application_id: str,
                 user_id: str,
                 access_token: str):
        """
        Initialize the Amazon Q Business SDK client.
        
        Args:
            region: AWS region where Amazon Q Business is deployed
            application_id: Amazon Q Business application ID
            user_id: User ID for the conversation
            access_token: Okta access token for authentication
        """
        self.region = region
        self.application_id = application_id
        self.user_id = user_id
        self.access_token = access_token
        
        # Create a custom session with Okta token
        session = Session()
        
        # Create credentials provider with Okta token
        credentials_provider = OktaCredentialsProvider(access_token)
        
        # Register the credentials provider with the session
        session.set_credentials_provider(credentials_provider)
        
        # Create the boto3 client with the custom session
        self.client = boto3.client(
            'qbusiness',
            region_name=self.region,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.environ.get('AWS_SESSION_TOKEN')
        )
        
        # Add Okta token to the client's config
        self.client._serializeRules.append(self._add_okta_token)
        
        # Initialize conversation state
        self.conversation_id = None
        self.system_message_id = None
    
    def _add_okta_token(self, request, **kwargs):
        """
        Add Okta token to the request headers.
        
        Args:
            request: The request object
            **kwargs: Additional arguments
        """
        request.headers.add('Authorization', f'Bearer {self.access_token}')
    
    def start_conversation(self) -> Dict[str, Any]:
        """
        Start a new conversation with Amazon Q Business.
        
        Returns:
            Response from the API
        """
        # Generate a unique conversation ID
        self.conversation_id = str(uuid.uuid4())
        
        try:
            response = self.client.start_conversation(
                applicationId=self.application_id,
                conversationId=self.conversation_id,
                userId=self.user_id
            )
            return response
        except Exception as e:
            print(f"Error starting conversation: {e}")
            return {"error": str(e)}
    
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
        
        try:
            response = self.client.put_message(
                applicationId=self.application_id,
                conversationId=self.conversation_id,
                messageId=message_id,
                content={
                    'text': message_text
                }
            )
            return response
        except Exception as e:
            print(f"Error sending message: {e}")
            return {"error": str(e)}
    
    def get_chat_sync(self, message_text: str) -> Dict[str, Any]:
        """
        Send a message and get a synchronous response using the ChatSync API.
        
        Args:
            message_text: The message to send
            
        Returns:
            Response from the API
        """
        # Prepare the request parameters
        params = {
            'applicationId': self.application_id,
            'userId': self.user_id,
            'text': message_text
        }
        
        # Add conversation ID if we have one
        if self.conversation_id:
            params['conversationId'] = self.conversation_id
            
        # Add system message ID if we have one
        if self.system_message_id:
            params['systemMessageId'] = self.system_message_id
            
        try:
            response = self.client.chat_sync(**params)
            
            # Update conversation state
            if 'conversationId' in response:
                self.conversation_id = response['conversationId']
            if 'systemMessageId' in response:
                self.system_message_id = response['systemMessageId']
                
            return response
        except Exception as e:
            print(f"Error in chat_sync: {e}")
            return {"error": str(e)}


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
    """Main function to demonstrate Amazon Q Business SDK integration with Okta authentication."""
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
    q_client = AmazonQBusinessSDKClient(
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
