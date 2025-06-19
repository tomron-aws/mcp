"""
Okta SDK Example

This module demonstrates how to use the official Okta Python SDK
to interact with Okta resources.
"""

import json
import time
from typing import Dict, List, Any, Optional

from okta.client import Client as OktaClient
from okta.models.user import User, UserProfile, UserCredentials, PasswordCredential, Password
from okta.models.user_factor import UserFactor
from okta.models.application import Application

from config import OKTA_ORG_URL, OKTA_API_TOKEN


def create_okta_client() -> OktaClient:
    """
    Create and configure an Okta SDK client.
    
    Returns:
        Configured Okta client
    """
    # Configure the Okta client
    config = {
        'orgUrl': OKTA_ORG_URL,
        'token': OKTA_API_TOKEN,
        'raiseException': True  # Raise exceptions for API errors
    }
    
    return OktaClient(config)


async def list_users(client: OktaClient, limit: int = 25) -> List[User]:
    """
    List users in the Okta organization using the SDK.
    
    Args:
        client: Okta client
        limit: Maximum number of users to return
        
    Returns:
        List of User objects
    """
    users, resp, err = await client.list_users(limit=limit)
    
    if err:
        print(f"Error listing users: {err}")
        return []
        
    return users


async def get_user(client: OktaClient, user_id: str) -> Optional[User]:
    """
    Get a user by ID or login using the SDK.
    
    Args:
        client: Okta client
        user_id: User ID or login email
        
    Returns:
        User object if found, None otherwise
    """
    user, resp, err = await client.get_user(user_id)
    
    if err:
        print(f"Error getting user: {err}")
        return None
        
    return user


async def create_user_with_sdk(client: OktaClient, first_name: str, last_name: str,
                          email: str, password: str, activate: bool = True) -> Optional[User]:
    """
    Create a new user using the Okta SDK.
    
    Args:
        client: Okta client
        first_name: User's first name
        last_name: User's last name
        email: User's email address (also used as login)
        password: User's initial password
        activate: Whether to activate the user immediately
        
    Returns:
        Created User object if successful, None otherwise
    """
    # Create user profile
    profile = UserProfile({
        'firstName': first_name,
        'lastName': last_name,
        'email': email,
        'login': email
    })
    
    # Create password credential
    password_credential = PasswordCredential({
        'value': password
    })
    
    credentials = UserCredentials({
        'password': password_credential
    })
    
    # Create user object
    user = User({
        'profile': profile,
        'credentials': credentials
    })
    
    # Create the user
    created_user, resp, err = await client.create_user(user, activate=activate)
    
    if err:
        print(f"Error creating user: {err}")
        return None
        
    return created_user


async def list_applications(client: OktaClient) -> List[Application]:
    """
    List applications in the Okta organization using the SDK.
    
    Args:
        client: Okta client
        
    Returns:
        List of Application objects
    """
    apps, resp, err = await client.list_applications()
    
    if err:
        print(f"Error listing applications: {err}")
        return []
        
    return apps


async def list_user_factors(client: OktaClient, user_id: str) -> List[UserFactor]:
    """
    List authentication factors for a user using the SDK.
    
    Args:
        client: Okta client
        user_id: User ID or login
        
    Returns:
        List of UserFactor objects
    """
    factors, resp, err = await client.list_factors(user_id)
    
    if err:
        print(f"Error listing user factors: {err}")
        return []
        
    return factors


async def run_sdk_examples():
    """Run examples using the Okta SDK."""
    # Create Okta client
    client = create_okta_client()
    
    print("Okta SDK Example")
    print("=" * 50)
    
    # Example 1: List users
    print("\n1. Listing users:")
    users = await list_users(client, limit=5)
    for user in users:
        print(f"  - {user.profile.firstName} {user.profile.lastName} ({user.profile.email})")
    
    # Example 2: List applications
    print("\n2. Listing applications:")
    apps = await list_applications(client)
    for app in apps:
        print(f"  - {app.name} ({app.id})")
    
    # Example 3: Create a user (commented out to prevent accidental creation)
    """
    print("\n3. Creating a user:")
    new_user = await create_user_with_sdk(
        client,
        first_name="SDK",
        last_name="Test",
        email="sdk.test@example.com",
        password="TemporaryPassword123!",
        activate=True
    )
    if new_user:
        print(f"  User created: {new_user.profile.email} (ID: {new_user.id})")
    """
    
    print("\nNote: Some operations are commented out to prevent accidental modifications.")
    print("Review the code and uncomment sections as needed for your use case.")


if __name__ == '__main__':
    import asyncio
    asyncio.run(run_sdk_examples())
