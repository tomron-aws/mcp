"""
Okta Authentication Demo

This script demonstrates how to use the different Okta authentication methods
provided in this project. It serves as a unified entry point for running
the examples and provides guidance on choosing the right authentication method.
"""

import argparse
import sys
import webbrowser
import asyncio

from okta_oauth_example import start_oauth_flow, OktaOAuthClient
from okta_saml_example import start_saml_flow, OktaSamlClient
from okta_api_example import run_api_examples, OktaApiClient
from okta_sdk_example import run_sdk_examples
from config import OKTA_ORG_URL


def print_header():
    """Print the demo header."""
    print("\n" + "=" * 80)
    print(f"Okta Authentication Demo - {OKTA_ORG_URL}")
    print("=" * 80)


def print_auth_methods():
    """Print information about the available authentication methods."""
    print("\nAvailable Authentication Methods:")
    print("\n1. OAuth 2.0/OIDC Flow")
    print("   Best for: Web applications, mobile apps, SPAs")
    print("   Features: Modern, flexible, supports various flows")
    print("   Example: okta_oauth_example.py")
    
    print("\n2. SAML Authentication")
    print("   Best for: Enterprise applications, SSO scenarios")
    print("   Features: Widely supported in enterprise environments")
    print("   Example: okta_saml_example.py")
    
    print("\n3. API Token Authentication")
    print("   Best for: Server-to-server, administrative operations")
    print("   Features: Simple, powerful for backend operations")
    print("   Example: okta_api_example.py")
    
    print("\n4. Okta SDK Usage")
    print("   Best for: Comprehensive Okta management using official SDK")
    print("   Features: Type-safe, well-documented, full API coverage")
    print("   Example: okta_sdk_example.py")


def print_configuration_instructions():
    """Print instructions for configuring the examples."""
    print("\nConfiguration Instructions:")
    print("\n1. Update src/config.py with your Okta details:")
    print("   - OKTA_ORG_URL: Your Okta organization URL")
    print("   - OKTA_API_TOKEN: API token from Okta Admin Console")
    print("   - OKTA_CLIENT_ID: Client ID from your Okta OIDC application")
    print("   - OKTA_CLIENT_SECRET: Client secret from your Okta OIDC application")
    print("   - OKTA_REDIRECT_URI: Redirect URI configured in your Okta application")
    print("   - OKTA_IDP_METADATA_URL: URL to your Okta SAML metadata")
    
    print("\n2. Set up the appropriate application in Okta:")
    print("   - For OAuth: Create an OIDC application")
    print("   - For SAML: Create a SAML application")
    print("   - For API: Generate an API token in the Okta Admin Console")
    
    print("\n3. Install required dependencies:")
    print("   pip install -r requirements.txt")


def open_okta_docs():
    """Open Okta documentation in a web browser."""
    docs_urls = {
        'main': 'https://developer.okta.com/docs/guides/',
        'oauth': 'https://developer.okta.com/docs/guides/implement-oauth-for-okta/',
        'saml': 'https://developer.okta.com/docs/guides/build-sso-integration/saml2/overview/',
        'api': 'https://developer.okta.com/docs/reference/api/overview/'
    }
    
    print("\nOpening Okta documentation in your browser...")
    for url in docs_urls.values():
        webbrowser.open(url)


def run_demo():
    """Run the authentication demo based on user selection."""
    parser = argparse.ArgumentParser(description='Okta Authentication Demo')
    parser.add_argument('method', nargs='?', choices=['oauth', 'saml', 'api', 'sdk', 'info'],
                      help='Authentication method to demonstrate')
    
    args = parser.parse_args()
    
    print_header()
    
    if not args.method or args.method == 'info':
        print_auth_methods()
        print_configuration_instructions()
        
        print("\nTo run a specific demo, use:")
        print("  python auth_demo.py oauth  # Run OAuth 2.0/OIDC demo")
        print("  python auth_demo.py saml   # Run SAML authentication demo")
        print("  python auth_demo.py api    # Run API token demo")
        print("  python auth_demo.py sdk    # Run Okta SDK demo")
        
        open_docs = input("\nWould you like to open the Okta documentation? (y/n): ")
        if open_docs.lower() == 'y':
            open_okta_docs()
            
    elif args.method == 'oauth':
        print("\nRunning OAuth 2.0/OIDC Authentication Demo")
        print("This will start a local web server and open your browser.")
        print("Follow the prompts to authenticate with Okta.")
        input("Press Enter to continue...")
        start_oauth_flow()
        
    elif args.method == 'saml':
        print("\nRunning SAML Authentication Demo")
        print("This will start a local web server and open your browser.")
        print("Follow the prompts to authenticate with Okta.")
        input("Press Enter to continue...")
        start_saml_flow()
        
    elif args.method == 'api':
        print("\nRunning API Token Authentication Demo")
        print("This will demonstrate using the Okta Management API.")
        input("Press Enter to continue...")
        run_api_examples()
        
    elif args.method == 'sdk':
        print("\nRunning Okta SDK Demo")
        print("This will demonstrate using the official Okta Python SDK.")
        input("Press Enter to continue...")
        asyncio.run(run_sdk_examples())


def check_configuration():
    """Check if the configuration has been updated from defaults."""
    from config import OKTA_ORG_URL, OKTA_API_TOKEN, OKTA_CLIENT_ID, OKTA_CLIENT_SECRET
    
    default_values = [
        "https://your-org.okta.com",
        "YOUR_API_TOKEN",
        "YOUR_CLIENT_ID",
        "YOUR_CLIENT_SECRET"
    ]
    
    actual_values = [OKTA_ORG_URL, OKTA_API_TOKEN, OKTA_CLIENT_ID, OKTA_CLIENT_SECRET]
    
    for default, actual in zip(default_values, actual_values):
        if actual == default:
            print("\nWARNING: It appears you haven't updated the configuration in src/config.py.")
            print("Please update the configuration before running the demos.")
            print_configuration_instructions()
            return False
            
    return True


if __name__ == '__main__':
    if check_configuration():
        run_demo()
    else:
        sys.exit(1)
