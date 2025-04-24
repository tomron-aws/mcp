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
"""Tests for the kendra-index-mcpserver MCP Server."""

import pytest
from awslabs.kendra_index_mcpserver_mcp_server.server import example_tool, math_tool


@pytest.mark.asyncio
async def test_example_tool():
    """Test the example_tool function returns the expected response."""
    # Arrange
    test_query = 'test query'
    expected_project_name = 'awslabs kendra-index-mcpserver MCP Server'
    expected_response = f"Hello from {expected_project_name}! Your query was {test_query}. Replace this with your tool's logic"

    # Act
    result = await example_tool(test_query)

    # Assert
    assert result == expected_response


@pytest.mark.asyncio
async def test_example_tool_failure():
    """Test the example_tool function with an incorrect expected response."""
    # Arrange
    test_query = 'test query'
    expected_project_name = 'awslabs kendra-index-mcpserver MCP Server'
    expected_response = f"Hello from {expected_project_name}! Your query was {test_query}. Replace this your tool's new logic"

    # Act
    result = await example_tool(test_query)

    # Assert
    assert result != expected_response


@pytest.mark.asyncio
class TestMathTool:
    """Test class for the math_tool function with various operations."""

    async def test_addition(self):
        """Test the addition operation of the math_tool function."""
        # Test integer addition
        assert await math_tool('add', 2, 3) == 5
        # Test float addition
        assert await math_tool('add', 2.5, 3.5) == 6.0

    async def test_subtraction(self):
        """Test the subtraction operation of the math_tool function."""
        # Test integer subtraction
        assert await math_tool('subtract', 5, 3) == 2
        # Test float subtraction
        assert await math_tool('subtract', 5.5, 2.5) == 3.0

    async def test_multiplication(self):
        """Test the multiplication operation of the math_tool function."""
        # Test integer multiplication
        assert await math_tool('multiply', 4, 3) == 12
        # Test float multiplication
        assert await math_tool('multiply', 2.5, 2) == 5.0

    async def test_division(self):
        """Test the division operation of the math_tool function."""
        # Test integer division
        assert await math_tool('divide', 6, 2) == 3.0
        # Test float division
        assert await math_tool('divide', 5.0, 2.0) == 2.5

    async def test_division_by_zero(self):
        """Test that division by zero raises a ValueError with the correct message."""
        # Test division by zero raises ValueError
        with pytest.raises(ValueError) as exc_info:
            await math_tool('divide', 5, 0)
        assert str(exc_info.value) == 'The denominator 0 cannot be zero.'

    async def test_invalid_operation(self):
        """Test that an invalid operation raises a ValueError with the correct message."""
        # Test invalid operation raises ValueError
        with pytest.raises(ValueError) as exc_info:
            await math_tool('power', 2, 3)
        assert 'Invalid operation: power' in str(exc_info.value)
