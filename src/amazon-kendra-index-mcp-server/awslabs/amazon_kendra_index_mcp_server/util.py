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
"""Utility functions for AWS Documentation MCP Server."""

import boto3
import os
from mypy_boto3_kendra.client import KendraClient
from typing import Any
from awslabs.amazon_kendra_index_mcp_server.tvm_client import TVMClient


def get_kendra_client(region=None) -> KendraClient:
    """Get a Kendra runtime client.

    Allows access to Kendra Indexes for RAG via the Kendra runtime client.

    Returns:
        boto3.client: A boto3 Kendra client instance.
    """
    # Initialize the Kendra client with given region or profile
    AWS_PROFILE = os.environ.get('AWS_PROFILE')
    AWS_REGION = region or os.environ.get('AWS_REGION', 'us-east-1')
    if AWS_PROFILE:
        kendra_client = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION).client(
            'kendra'
        )
        return kendra_client

    kendra_client = boto3.client('kendra', region_name=AWS_REGION)
    return kendra_client


def get_qbusiness_client(region=None) -> Any:
    """Get an Amazon Q Business runtime client.

    Allows access to Amazon Q Business APIs via the boto3 client.

    Args:
        region (str, optional): AWS region to use. Defaults to None.

    Returns:
        boto3.client: A boto3 Amazon Q Business client instance.
    """
    # Initialize the Amazon Q Business client with given region or profile
    AWS_PROFILE = os.environ.get('AWS_PROFILE')
    AWS_REGION = region or os.environ.get('AWS_REGION', 'us-east-1')
    if AWS_PROFILE:
        qbusiness_client = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION).client(
            'qbusiness'
        )
        return qbusiness_client

    qbusiness_client = boto3.client('qbusiness', region_name=AWS_REGION)
    return qbusiness_client

def get_identity_aware_qbusiness_client(region=None) -> Any:
    """Get an Amazon Q Business runtime client.

    Allows access to Amazon Q Business APIs via the boto3 client.

    Args:
        region (str, optional): AWS region to use. Defaults to None.

    Returns:
        boto3.client: A boto3 Amazon Q Business client instance.
    """
    token_client = TVMClient(
        issuer="https://obrcaik025.execute-api.us-east-1.amazonaws.com/prod/",
        client_id="oidc-tvm-239122513475",
        client_secret="fbe06e868dc34f8bb5e4ee246eefad37",
        role_arn="arn:aws:iam::239122513475:role/tvm-qbiz-custom-oidc-role",
        region="us-east-1"
    )
    credentials_q = token_client.get_sigv4_credentials(email="tomron@amazon.com")
    qbusiness_client = boto3.client(
        'qbusiness',
        region_name="us-east-1",
        **credentials_q
    )
    return qbusiness_client
