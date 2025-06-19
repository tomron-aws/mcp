#!/usr/bin/env python3
"""
Okta Authentication Token Generator
Usage: python get_okta_token.py user@example.com
"""

import sys
import asyncio
from okta.client import Client as OktaClient

# Configuration - these would need to be set in your environment or in the script
OKTA_DOMAIN = "trial-4770462.okta.com"
OKTA_API_TOKEN = "00Ys0TcDqkm7OxuZl_0AftLRqcgXGy6wCdPsXiYJUw"  # Admin API token with proper permissions

async def get_token_by_email(email):
    # Initialize the Okta client
    okta_client = OktaClient({
        'orgUrl': f'https://{OKTA_DOMAIN}',
        'token': OKTA_API_TOKEN
    })
    users, resp, err = await okta_client.list_users()
    for user in users:
        print(user.profile.first_name, user.profile.last_name)
    # Step 1: Look up the user by email
    # users, resp, err = await okta_client.list_users(query_params={'search': f'profile.email eq "{email}"'})
    # if err or not users:
    #     print(f"Error: User with email {email} not found")
    #     return None
    
    user = users[0]
    user_id = user.id
    
    # Step 2: Generate a session token for the user
    # This requires the "Session token creation" permission in your API token
    try:
        # Using the createSessionToken API endpoint
        response, err = await okta_client.create_session_token(user_id)
        if err:
            print(f"Error creating session token: {err}")
            return None
        
        return response.token
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python get_okta_token.py user@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    token = asyncio.run(get_token_by_email(email))
    
    if token:
        print(token)  # Output just the token for easy piping/usage
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
