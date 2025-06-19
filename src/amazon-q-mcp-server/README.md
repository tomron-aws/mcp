# AWS Labs Amazon Q MCP Server

An AWS Labs Model Context Protocol (MCP) server for Amazon Q

## Instructions

This can be used by clients to query Amazon Q Business to aid in answering the users prompt.

## TODO (REMOVE AFTER COMPLETING)

* [ ] Optionally add an ["RFC issue"](https://github.com/awslabs/mcp/issues) for the community to review
* [ ] Generate a `uv.lock` file with `uv sync` -> See [Getting Started](https://docs.astral.sh/uv/getting-started/)
* [ ] Remove the example tools in `./awslabs/amazon_q_mcp_server/server.py`
* [ ] Add your own tool(s) following the [DESIGN_GUIDELINES.md](https://github.com/awslabs/mcp/blob/main/DESIGN_GUIDELINES.md)
* [ ] Keep test coverage at or above the `main` branch - NOTE: GitHub Actions run this command for CodeCov metrics `uv run --frozen pytest --cov --cov-branch --cov-report=term-missing`
* [ ] Document the MCP Server in this "README.md"
* [ ] Add a section for this Amazon Q MCP Server at the top level of this repository "../../README.md"
* [ ] Create the "../../doc/servers/amazon-q-mcp-server.md" file with these contents:

    ```markdown
    ---
    title: Amazon Q MCP Server
    ---

    {% include "../../src/amazon-q-mcp-server/README.md" %}
    ```
  
* [ ] Reference within the "../../doc/index.md" like this:

    ```markdown
    ### Amazon Q MCP Server
    
    An AWS Labs Model Context Protocol (MCP) server for Amazon Q
    
    **Features:**
    
    - Feature one
    - Feature two
    - ...

    This can be used by clients to query Amazon Q Business to aid in answering the users prompt.
    
    [Learn more about the Amazon Q MCP Server](servers/amazon-q-mcp-server.md)
    ```

* [ ] Submit a PR and pass all the checks
