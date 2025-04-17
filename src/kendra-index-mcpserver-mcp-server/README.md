# awslabs kendra-index-mcpserver MCP Server

An AWS Labs Model Context Protocol (MCP) server for kendra-index-mcpserver

## TODO

* Remove the examples
* Add your tool(s)
* Keep test coverage
* Document the MCP in this `README.md`
* Document in the top level `../../README.md`
* Reference within the `../../doc/index.md`
* Add include to `../../doc/servers/`
Example usage MCP COnfiguration:
"awslabs.aws-kendra-index-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute path to mcp repo/src/kendra-index-mcpserver-mcp-server/awslabs/kendra_index_mcpserver_mcp_server",
        "run",
        "server.py"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "KENDRA_INDEX_ID": "[your kendra index id]"
      },
      "disabled": false,
      "autoApprove": []
    },
