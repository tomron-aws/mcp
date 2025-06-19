# Okta Authentication with Python - Comprehensive Guide

This guide provides detailed instructions on how to set up and use the Okta authentication examples in this project. It covers the configuration of your Okta account, setting up the necessary applications, and running the examples.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Setting Up Your Okta Account](#setting-up-your-okta-account)
4. [Configuring the Examples](#configuring-the-examples)
5. [Running the Examples](#running-the-examples)
6. [Authentication Methods Explained](#authentication-methods-explained)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)
9. [Additional Resources](#additional-resources)

## Project Overview

This project demonstrates four common methods for authenticating with Okta using Python:

1. **OAuth 2.0/OIDC Flow**: Modern authentication for web and mobile applications
2. **SAML Authentication**: Enterprise-grade single sign-on (SSO)
3. **API Token Authentication**: Direct access to Okta's Management API
4. **Okta SDK Integration**: Using the official Okta Python SDK for comprehensive management

Each method is implemented in a separate module with a clean, reusable design that you can adapt for your own applications.

## Prerequisites

Before you begin, ensure you have:

- Python 3.7 or higher installed
- An Okta developer account (free tier available at [developer.okta.com](https://developer.okta.com/))
- Basic understanding of authentication concepts
- Required Python packages installed:
  ```
  pip install -r requirements.txt
  ```

## Setting Up Your Okta Account

### 1. Create an Okta Developer Account

If you don't already have an Okta account:

1. Go to [developer.okta.com](https://developer.okta.com/) and sign up for a free developer account
2. Activate your account through the email you receive
3. Log in to your Okta Admin Console

### 2. Create an API Token

For API access and administrative operations:

1. In the Okta Admin Console, go to **Security** > **API**
2. Select the **Tokens** tab
3. Click **Create Token**
4. Enter a name for your token (e.g., "Python Auth Examples")
5. Copy the token value immediately (you won't be able to see it again)
6. Store this token securely for use in the configuration

### 3. Set Up an OAuth 2.0/OIDC Application

For the OAuth example:

1. In the Okta Admin Console, go to **Applications** > **Applications**
2. Click **Create App Integration**
3. Select **OIDC - OpenID Connect** as the Sign-in method
4. Choose **Web Application** as the Application type
5. Click **Next**
6. Enter a name for your application (e.g., "Python OAuth Example")
7. Add the following Redirect URI: `http://localhost:8080/authorization-code/callback`
8. Under "Assignments", select "Allow everyone in your organization to access"
9. Click **Save**
10. On the next screen, note the **Client ID** and **Client Secret**

### 4. Set Up a SAML Application

For the SAML example:

1. In the Okta Admin Console, go to **Applications** > **Applications**
2. Click **Create App Integration**
3. Select **SAML 2.0** as the Sign-in method
4. Click **Next**
5. Enter a name for your application (e.g., "Python SAML Example")
6. Click **Next**
7. For **Single sign on URL**, enter: `http://localhost:8080/saml/acs`
8. For **Audience URI (SP Entity ID)**, enter: `http://localhost:8080/saml/metadata`
9. Under "Attribute Statements", add:
   - Name: `email`, Value: `user.email`
   - Name: `firstName`, Value: `user.firstName`
   - Name: `lastName`, Value: `user.lastName`
10. Click **Next**, then **Finish**
11. On the application page, click the **Sign On** tab
12. Find the "SAML Signing Certificates" section
13. Click **View IdP metadata** and copy the URL (or download the XML)

## Configuring the Examples

### Update the Configuration File

Edit `src/config.py` with your Okta details:

```python
# Okta Organization Settings
OKTA_ORG_URL = "https://your-org.okta.com"  # Your Okta organization URL
OKTA_API_TOKEN = "YOUR_API_TOKEN"  # API token from Okta Admin Console

# OAuth 2.0 / OIDC Settings
OKTA_CLIENT_ID = "YOUR_CLIENT_ID"  # Client ID from your Okta application
OKTA_CLIENT_SECRET = "YOUR_CLIENT_SECRET"  # Client secret from your Okta application
OKTA_REDIRECT_URI = "http://localhost:8080/authorization-code/callback"  # Must match Okta app config

# SAML Settings
OKTA_IDP_METADATA_URL = "https://your-org.okta.com/app/YOUR_APP_ID/sso/saml/metadata"
OKTA_SP_ENTITY_ID = "http://localhost:8080/saml/metadata"
OKTA_SP_ACS_URL = "http://localhost:8080/saml/acs"
```

Replace the placeholder values with your actual Okta configuration details.

## Running the Examples

### Using the Demo Script

The easiest way to run the examples is using the `auth_demo.py` script:

```bash
# Show information about authentication methods
python src/auth_demo.py info

# Run the OAuth 2.0/OIDC example
python src/auth_demo.py oauth

# Run the SAML example
python src/auth_demo.py saml

# Run the API example
python src/auth_demo.py api

# Run the SDK example
python src/auth_demo.py sdk
```

### Running Individual Examples

You can also run each example directly:

```bash
# OAuth 2.0/OIDC example
python src/okta_oauth_example.py

# SAML example
python src/okta_saml_example.py

# API example
python src/okta_api_example.py

# SDK example
python src/okta_sdk_example.py
```

## Authentication Methods Explained

### OAuth 2.0/OIDC Flow

The OAuth 2.0 and OpenID Connect (OIDC) flow is ideal for modern web and mobile applications. It provides:

- Secure user authentication
- Access to user profile information
- Token-based authorization for APIs
- Support for various flows (Authorization Code, Implicit, etc.)

Our example implements the Authorization Code flow with PKCE (Proof Key for Code Exchange), which is the most secure option for web applications. The flow works as follows:

1. The user clicks "Login with Okta"
2. They are redirected to Okta for authentication
3. After successful authentication, Okta redirects back with an authorization code
4. The application exchanges this code for access and ID tokens
5. The tokens are used to access protected resources and user information

### SAML Authentication

SAML (Security Assertion Markup Language) is widely used in enterprise environments for Single Sign-On (SSO). It provides:

- Centralized authentication across multiple applications
- Rich user attribute sharing
- Enterprise-grade security

Our example sets up a simple Service Provider (SP) that integrates with Okta as the Identity Provider (IdP). The flow works as follows:

1. The user clicks "Login with Okta (SAML)"
2. They are redirected to Okta for authentication
3. After successful authentication, Okta generates a SAML assertion
4. The assertion is posted back to the application's Assertion Consumer Service (ACS)
5. The application validates the assertion and establishes a session

### API Token Authentication

API token authentication provides direct access to Okta's Management API for administrative operations. It's ideal for:

- Server-to-server communication
- Administrative tasks
- Automation scripts

Our example demonstrates how to use an API token to:

- List users in your Okta organization
- List applications
- Create and manage users
- Generate tokens for users

### Okta SDK Authentication

The Okta SDK approach provides a more structured and type-safe way to interact with Okta's APIs. It's ideal for:

- Applications requiring comprehensive Okta management
- Projects that benefit from a well-documented, official SDK
- Developers who prefer working with objects rather than raw API calls

Our example demonstrates how to use the Okta Python SDK to:

- List users and applications
- Create and manage users
- Work with authentication factors
- Perform administrative operations

## Security Considerations

When implementing authentication in production environments, consider the following:

1. **Token Storage**: Never store tokens in client-side JavaScript or in code repositories
2. **HTTPS**: Always use HTTPS in production environments
3. **Token Validation**: Validate tokens on every request
4. **Scopes**: Request only the scopes your application needs
5. **Token Expiration**: Handle token expiration and refresh properly
6. **API Token Security**: Treat API tokens like passwords and rotate them regularly
7. **Error Handling**: Implement proper error handling for authentication failures

## Troubleshooting

### Common Issues

1. **"Invalid redirect URI"**: Ensure the redirect URI in your code exactly matches the one configured in Okta
2. **"Invalid client"**: Double-check your client ID and secret
3. **"CORS error"**: CORS is not properly configured in your Okta application
4. **"Token validation failed"**: Check clock synchronization between servers

### Debugging Tips

1. Enable debug logging in Flask: `app.run(debug=True)`
2. Check the Okta System Log in the Admin Console
3. Use the Network tab in browser developer tools to inspect requests
4. Verify your Okta application settings

## Additional Resources

- [Okta Developer Documentation](https://developer.okta.com/docs/guides/)
- [OAuth 2.0 Simplified](https://www.oauth.com/)
- [SAML Technical Overview](https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)
- [Python Requests Library](https://docs.python-requests.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PySAML2 Documentation](https://pysaml2.readthedocs.io/)

---

This guide should help you get started with Okta authentication in Python. If you encounter any issues or have questions, please refer to the official Okta documentation or reach out to Okta support.
