# Salesforce OAuth Application

A complete FastAPI application that demonstrates Salesforce OAuth 2.0 authentication flow.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Salesforce Connected App:**
   - Go to Salesforce Setup → App Manager → New Connected App
   - Enable OAuth Settings
   - Add callback URL: `http://localhost:8080/auth/salesforce/callback`
   - Select OAuth Scopes: `openid`, `email`, `profile`, `api`
   - Save and get Client ID and Client Secret

3. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your Salesforce credentials
   ```

4. **Run the application:**
   ```bash
   python salesforce_oauth_app.py
   ```

5. **Test the flow:**
   - Visit `http://localhost:8080`
   - Click "Login with Salesforce"
   - Complete Salesforce authentication
   - View tokens and user info

## API Endpoints

- `GET /` - Home page with login link
- `GET /login` - Initiates OAuth flow
- `GET /auth/salesforce/callback` - Handles OAuth callback
- `GET /api/tokens/{session_id}` - Returns tokens as JSON

## Environment Variables

- `SALESFORCE_CLIENT_ID` - Your Salesforce Connected App Client ID
- `SALESFORCE_CLIENT_SECRET` - Your Salesforce Connected App Client Secret  
- `SALESFORCE_DOMAIN` - Salesforce domain (default: login.salesforce.com)
- `LOCAL_PORT` - Local server port (default: 8080)