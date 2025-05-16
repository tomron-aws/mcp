# awslabs amazon-kendra-index-mcp-server MCP Server

An AWS Labs Model Context Protocol (MCP) server for Amazon Kendra. This MCP server allows you to use a Kendra Index as additional context for RAG. 

Use Cases: 
      1. Enhancing your existing MCP-enabled ChatBot with additional RAG indices
      2. Enhancing the responses from coding tools such as Cline, Cursor, Windsurf, Q Developer, etc.


### Example usage MCP Configuration:
*Example mcp.json config file*
```
{
      "mcpServers": {
            "awslabs.amazon-kendra-index-mcp-server": {
                  "command": "uv",
                  "args": [
                    "--directory",
                    "[absolute path to mcp repo]/src/amazon-kendra-index-mcp-server/awslabs/amazon_kendra_index_mcp_server",
                    "run",
                    "server.py"
                  ],
                  "env": {
                    "FASTMCP_LOG_LEVEL": "ERROR",
                    "KENDRA_INDEX_ID": "[Your Kendra Index Id]"
                    "AWS_PROFILE": "[Your AWS Profile Name]",
                    "AWS_REGION": "[Region where your Kendra Index resides]"
                  },
                  "disabled": false,
                  "autoApprove": []
                }
      }
}
```
