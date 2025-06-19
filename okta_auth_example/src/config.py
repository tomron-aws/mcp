"""
Configuration settings for Okta authentication examples.
Replace these values with your own Okta application details.
"""

# Okta Organization Settings
OKTA_ORG_URL = "https://your-org.okta.com"  # Your Okta organization URL
OKTA_API_TOKEN = "YOUR_API_TOKEN"  # API token from Okta Admin Console

# OAuth 2.0 / OIDC Settings
OKTA_CLIENT_ID = "YOUR_CLIENT_ID"  # Client ID from your Okta application
OKTA_CLIENT_SECRET = "YOUR_CLIENT_SECRET"  # Client secret from your Okta application
OKTA_REDIRECT_URI = "http://localhost:8080/authorization-code/callback"  # Must match Okta app config
OKTA_SCOPES = ["openid", "profile", "email"]  # Scopes to request

# SAML Settings
OKTA_IDP_METADATA_URL = "https://your-org.okta.com/app/YOUR_APP_ID/sso/saml/metadata"
OKTA_SP_ENTITY_ID = "http://your-service-provider-entity-id"
OKTA_SP_ACS_URL = "http://localhost:8080/saml/acs"  # Assertion Consumer Service URL

# Application Settings
APP_SECRET_KEY = "your-secret-key-for-flask"  # Random secret key for Flask sessions
APP_HOST = "localhost"
APP_PORT = 8080
APP_DEBUG = True

# Token Storage Settings
TOKEN_STORAGE_FILE = "tokens.json"  # Local file to store tokens (for demo purposes only)
