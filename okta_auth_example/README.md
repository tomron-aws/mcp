# Okta Authentication with Python

This project demonstrates various methods to obtain authentication tokens from Okta using Python.

## Project Structure

- `src/okta_auth_client.py`: Core client for Okta authentication
- `src/okta_oauth_example.py`: Example using OAuth 2.0/OIDC flow
- `src/okta_saml_example.py`: Example using SAML authentication
- `src/okta_api_example.py`: Example using Okta Management API
- `src/okta_sdk_example.py`: Example using the official Okta Python SDK
- `src/auth_demo.py`: Unified demo script to run all examples
- `src/config.py`: Configuration settings (replace with your Okta details)
- `requirements.txt`: Required Python packages

## Prerequisites

1. An Okta account with admin access
2. Python 3.7+
3. Registered Okta application with proper redirect URIs

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Update `src/config.py` with your Okta domain, client ID, and client secret
2. Run the desired example:

```bash
python src/okta_oauth_example.py
```

## Authentication Methods

This project demonstrates four common authentication methods with Okta:

1. **OAuth 2.0/OIDC Flow**: For web and mobile applications
2. **SAML Authentication**: For enterprise SSO scenarios
3. **Direct API Access**: Using Okta Management API with API tokens
4. **Okta SDK**: Using the official Okta Python SDK for comprehensive management

Choose the method that best fits your application's requirements.

## Running the Demo

The easiest way to explore all examples is using the demo script:

```bash
# Show information about all authentication methods
python src/auth_demo.py info

# Run a specific example
python src/auth_demo.py oauth  # OAuth 2.0/OIDC example
python src/auth_demo.py saml   # SAML example
python src/auth_demo.py api    # API example
python src/auth_demo.py sdk    # SDK example
```

## Amazon Q Business Integration

This project also includes examples of integrating Okta authentication with Amazon Q Business:

- `src/amazon_q_business_chat.py`: Script that demonstrates how to obtain an Okta token and use it with AWS SigV4 authentication to make direct API calls to Amazon Q Business
- `src/amazon_q_business_sdk_example.py`: Script that uses the Amazon Q Business SDK (via boto3) with Okta authentication
- `src/AMAZON_Q_BUSINESS_README.md`: Detailed documentation for the Amazon Q Business integration

To run the Amazon Q Business integration:

```bash
# Using direct API calls with SigV4
python src/amazon_q_business_chat.py

# Using the Amazon Q Business SDK
python src/amazon_q_business_sdk_example.py
```

Both scripts will:
1. Obtain an authentication token from Okta
2. Use AWS credentials to authenticate with Amazon Q Business
3. Provide an interactive chat interface to Amazon Q Business

See `src/AMAZON_Q_BUSINESS_README.md` for detailed instructions and requirements.
