# Amazon Q Business Integration with Okta Authentication

This script demonstrates how to integrate Amazon Q Business with Okta authentication using AWS SigV4 for API requests.

## Overview

The `amazon_q_business_chat.py` script provides a complete example of:

1. Obtaining an authentication token from Okta using OAuth 2.0
2. Using that token along with AWS SigV4 authentication to make ChatSync API calls to Amazon Q Business
3. Maintaining a conversation session with Amazon Q Business

## Prerequisites

Before using this script, you need:

1. An Okta account configured with an OAuth 2.0 application (as described in the main project README)
2. An Amazon Q Business application set up in your AWS account
3. AWS credentials with permissions to access the Amazon Q Business API
4. Python 3.7+ with the required dependencies installed

## Required AWS Permissions

Your AWS credentials need the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "qbusiness:StartConversation",
                "qbusiness:SendMessage",
                "qbusiness:ChatSync"
            ],
            "Resource": "arn:aws:qbusiness:*:*:application/*"
        }
    ]
}
```

## Configuration

The script requires the following configuration:

1. **Okta Configuration**: Update `src/config.py` with your Okta details (as described in the main project README)
2. **AWS Credentials**: Set up your AWS credentials using one of the following methods:
   - Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` (optional)
   - AWS credentials file (`~/.aws/credentials`)
   - Instance profile (if running on EC2)
3. **Amazon Q Business Configuration**: You'll need:
   - AWS Region where your Amazon Q Business application is deployed
   - Amazon Q Business application ID
   - User ID for the conversation

## Usage

Run the script using:

```bash
python src/amazon_q_business_chat.py
```

The script will:

1. Prompt you for AWS region, application ID, and user ID (if not provided via environment variables)
2. Obtain an Okta access token (opening a browser for authentication if needed)
3. Start a conversation with Amazon Q Business
4. Enter an interactive chat loop where you can send messages and receive responses

## Environment Variables

You can set the following environment variables to avoid manual input:

- `AWS_REGION`: AWS region where your Amazon Q Business application is deployed
- `Q_BUSINESS_APP_ID`: Your Amazon Q Business application ID
- `USER_ID`: User ID for the conversation
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_SESSION_TOKEN`: Your AWS session token (if using temporary credentials)

## Authentication Flow

The script uses the following authentication flow:

1. **Okta Authentication**:
   - Checks for an existing valid token
   - If no valid token exists, opens a browser for authentication
   - Exchanges the authorization code for access and refresh tokens
   - Stores the tokens for future use

2. **AWS SigV4 Authentication**:
   - Creates a signed request using AWS SigV4 authentication
   - Includes the Okta access token in the Authorization header
   - Makes the authenticated request to the Amazon Q Business API

## API Endpoints Used

The script demonstrates the following Amazon Q Business API endpoints:

1. **Start Conversation**: `PUT /applications/{applicationId}/conversations/{conversationId}`
2. **Send Message**: `PUT /applications/{applicationId}/conversations/{conversationId}/messages/{messageId}`
3. **ChatSync**: `POST /applications/{applicationId}/chatsync`

## Error Handling

The script includes error handling for:

- Failed Okta authentication
- Failed AWS SigV4 signing
- API errors from Amazon Q Business
- JSON parsing errors

## Security Considerations

When using this script, consider the following security best practices:

1. **Token Storage**: The script stores tokens locally. In a production environment, use a secure storage mechanism.
2. **AWS Credentials**: Never hardcode AWS credentials. Use environment variables or the AWS credentials file.
3. **HTTPS**: The script uses HTTPS for all API calls to ensure secure communication.
4. **Least Privilege**: Use AWS IAM policies that grant only the necessary permissions.

## Customization

You can customize the script by:

1. Modifying the `AmazonQBusinessClient` class to add additional API methods
2. Changing the authentication flow to suit your specific requirements
3. Adding additional error handling or logging
4. Implementing a more sophisticated token storage mechanism

## Troubleshooting

If you encounter issues:

1. **Authentication Errors**: Verify your Okta configuration in `src/config.py`
2. **AWS Credential Errors**: Check that your AWS credentials are valid and have the necessary permissions
3. **API Errors**: Verify your Amazon Q Business application ID and ensure the application is properly configured
4. **Connection Issues**: Check your network connectivity and firewall settings

## References

- [AWS Documentation: Making SigV4 Authenticated API Calls](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/making-sigv4-authenticated-api-calls.html)
- [Okta Developer Documentation](https://developer.okta.com/docs/guides/)
- [AWS SDK for Python (Boto3) Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
