# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""awslabs Amazon Q MCP Server implementation."""

from loguru import logger
import argparse
import os
from awslabs.amazon_q_mcp_server.util import get_qbusiness_client, get_identity_aware_qbusiness_client
from mcp.server.fastmcp import FastMCP
from typing import Any, Dict, List, Optional

mcp = FastMCP(
    "awslabs.amazon-q-mcp-server",
    instructions='This can be used by clients to query Amazon Q Business to aid in answering the users prompt.',
    dependencies=[
        'pydantic',
        'loguru',
    ],
)


@mcp.tool(name='QBusinessListApplicationsTool')
async def qbusiness_list_applications_tool(
    region: Optional[str] = None,
    maxResults: Optional[int] = None,
    nextToken: Optional[str] = None,
) -> Dict[str, Any]:
    """List all Amazon Q Business applications in the user's account.

    This tool lists all Amazon Q Business applications available in the user's account
    and returns details including description, applicationId, retrieverId, and application name.

    Parameters:
        region (str, optional): The AWS region where the Amazon Q Business applications are located.
        maxResults (int, optional): The maximum number of results to return.
        nextToken (str, optional): The token for the next set of results from a previous call.

    Returns:
        Dict containing the list of Amazon Q Business applications with their details.
    """
    try:
        if region:
            qbusiness_client = get_qbusiness_client(region)
        else:
            qbusiness_client = get_qbusiness_client()

        # Prepare the request parameters
        request_params = {}
        if maxResults is not None:
            request_params['maxResults'] = maxResults
        if nextToken is not None:
            request_params['nextToken'] = nextToken

        # Call the ListApplications API
        response = qbusiness_client.list_applications(**request_params)

        # Process and return the results
        applications = []
        for app in response.get('applications', []):
            # Get application details
            app_info = {
                'applicationId': app.get('applicationId'),
                'name': app.get('name'),
                'description': app.get('description')
            }
            
            # Get retrievers for this application
            try:
                retrievers_response = qbusiness_client.list_retrievers(applicationId=app.get('applicationId'))
                retrievers = []
                for retriever in retrievers_response.get('retrievers', []):
                    retriever_info = {
                        'retrieverId': retriever.get('retrieverId'),
                        'name': retriever.get('name'),
                        'type': retriever.get('type')
                    }
                    retrievers.append(retriever_info)
                app_info['retrievers'] = retrievers
            except Exception as e:
                app_info['retrievers_error'] = str(e)
            
            applications.append(app_info)

        # Handle pagination if there are more results
        result = {
            'region': region or os.environ.get('AWS_REGION', 'us-east-1'),
            'count': len(applications),
            'applications': applications,
            'nextToken': response.get('nextToken')
        }
        
        return result

    except Exception as e:
        return {'error': str(e), 'region': region or os.environ.get('AWS_REGION', 'us-east-1')}


@mcp.tool(name='QBusinessSearchRelevantContentTool')
async def qbusiness_search_relevant_content_tool(
    queryText: str,
    applicationId: str,
    retrieverId: str,
    region: Optional[str] = None,
    maxResults: Optional[int] = None,
    nextToken: Optional[str] = None,
) -> Dict[str, Any]:
    """Search for relevant content in an Amazon Q Business application.

    This tool searches for relevant content in the specified Amazon Q Business application
    based on a query text. It uses the SearchRelevantContent API to find and return
    content items that match the query.

    Parameters:
        queryText (str): The text to search for.
        applicationId (str): The unique identifier of the Amazon Q Business application to search.
        retrieverId (str): The unique identifier of the retriever to use as the content source.
        region (str, optional): The AWS region where the Amazon Q Business application is located.
        maxResults (int, optional): The maximum number of results to return.
        nextToken (str, optional): The token for the next set of results from a previous call.

    Returns:
        Dict containing the search results from Amazon Q Business.
    """
    try:
        if region:
            qbusiness_client = get_identity_aware_qbusiness_client(region)
        else:
            qbusiness_client = get_identity_aware_qbusiness_client()

        # Prepare the request parameters
        request_params = {
            'applicationId': applicationId,
            'queryText': queryText,
            'contentSource': {
                'retriever': {
                    'retrieverId': retrieverId
                }
            }
        }

        # Add optional parameters if provided
        if maxResults is not None:
            request_params['maxResults'] = maxResults
        if nextToken is not None:
            request_params['nextToken'] = nextToken

        # Call the SearchRelevantContent API
        response = qbusiness_client.search_relevant_content(**request_params)

        # Process and return the results
        results = {
            'query': queryText,
            'applicationId': applicationId,
            'retrieverId': retrieverId,
            'nextToken': response.get('nextToken'),
            'results': []
        }

        # Extract relevant information from each content item
        for item in response.get('relevantContent', []):
            content_item = {
                'content': item.get('content'),
                'documentId': item.get('documentId'),
                'documentTitle': item.get('documentTitle'),
                'documentUri': item.get('documentUri'),
                'scoreConfidence': item.get('scoreAttributes', {}).get('scoreConfidence') if item.get('scoreAttributes') else None
            }

            # Add document attributes if available
            if 'documentAttributes' in item and item['documentAttributes']:
                attributes = []
                for attr in item['documentAttributes']:
                    attr_info = {
                        'name': attr.get('name'),
                        'value': attr.get('value')
                    }
                    attributes.append(attr_info)
                content_item['documentAttributes'] = attributes

            results['results'].append(content_item)

        return results

    except Exception as e:
        return {
            'error': str(e),
            'query': queryText,
            'applicationId': applicationId,
            'retrieverId': retrieverId
        }


@mcp.tool(name='QBusinessChatSyncTool')
async def qbusiness_chat_sync_tool(
    userMessage: str,
    region: Optional[str] = None,
    conversationId: Optional[str] = None,
    attributionToken: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a message to Amazon Q Business ChatSync API with a specific plugin.

    This tool sends a message to the Amazon Q Business ChatSync API using a specific plugin
    and returns the response.

    Parameters:
        userMessage (str): The message from the user to send to Amazon Q Business.
        region (str, optional): The AWS region where the Amazon Q Business application is located.
        conversationId (str, optional): The unique identifier of an existing conversation.
        attributionToken (str, optional): The attribution token for the conversation.

    Returns:
        Dict containing the response from Amazon Q Business ChatSync API.
    """
    try:
        if region:
            qbusiness_client = get_identity_aware_qbusiness_client(region)
        else:
            qbusiness_client = get_identity_aware_qbusiness_client()

        # Prepare the request parameters
        request_params = {
            'applicationId': '43b53b94-f607-4c3d-8938-d05937db8d62',
            'userMessage': userMessage,
            'chatMode': 'PLUGIN_MODE',
            'chatModeConfiguration':{
                'pluginConfiguration': {
                    'pluginId': 'e3873c23-5455-44c6-bea1-fbaadf3b22c4'
                }
            },
            'authChallengeResponse': {
                'responseMap': {
                    'access_token': '00Dbm00000Iyskm!AQEAQLU_nn3W2.LPFwxYO2mC5874YKBNx0',
                    'instance_url': 'https://aws200-dev-ed.develop.lightning.force.com/services/data/v60.0'
                }
            }
        }

        # Add optional parameters if provided
        if conversationId is not None:
            request_params['conversationId'] = conversationId
        if attributionToken is not None:
            request_params['attributionToken'] = attributionToken

        # Call the ChatSync API
        response = qbusiness_client.chat_sync(**request_params)

        # Process and return the results
        result = {
            'conversationId': response.get('conversationId'),
            'systemMessage': response.get('systemMessage'),
            'userMessage': userMessage,
            'attributionToken': response.get('attributionToken')
        }

        # Add plugin results if available
        if 'pluginResult' in response:
            result['pluginResult'] = {
                'pluginId': response['pluginResult'].get('pluginId'),
                'status': response['pluginResult'].get('status'),
                'body': response['pluginResult'].get('body')
            }

        # Add citations if available
        if 'citations' in response and response['citations']:
            citations = []
            for citation in response['citations']:
                citation_info = {
                    'title': citation.get('title'),
                    'url': citation.get('url'),
                    'snippet': citation.get('snippet')
                }
                citations.append(citation_info)
            result['citations'] = citations

        return result

    except Exception as e:
        return {
            'error': str(e),
            'applicationId': '43b53b94-f607-4c3d-8938-d05937db8d62',
            'userMessage': userMessage,
            'pluginId': 'e3873c23-5455-44c6-bea1-fbaadf3b22c4'
        }



def main():
    """Run the MCP server with CLI argument support."""

    logger.trace('A trace message.')
    logger.debug('A debug message.')
    logger.info('An info message.')
    logger.success('A success message.')
    logger.warning('A warning message.')
    logger.error('An error message.')
    logger.critical('A critical message.')

    mcp.run()


if __name__ == '__main__':
    main()
