# AWS Labs Amazon Kendra Index MCP Server

An AWS Labs Model Context Protocol (MCP) server for Amazon Kendra. This MCP server allows you to use a Kendra Index as additional context for RAG. 

### Pre-Reqs:

* [Sign-Up for an AWS account](https://aws.amazon.com/free/?trk=78b916d7-7c94-4cab-98d9-0ce5e648dd5f&sc_channel=ps&ef_id=Cj0KCQjwxJvBBhDuARIsAGUgNfjOZq8r2bH2OfcYfYTht5v5I1Bn0lBKiI2Ii71A8Gk39ZU5cwMLPkcaAo_CEALw_wcB:G:s&s_kwcid=AL!4422!3!432339156162!e!!g!!aws%20sign%20up!9572385111!102212379327&gad_campaignid=9572385111&gbraid=0AAAAADjHtp99c5A9DUyUaUQVhVEoi8of3&gclid=Cj0KCQjwxJvBBhDuARIsAGUgNfjOZq8r2bH2OfcYfYTht5v5I1Bn0lBKiI2Ii71A8Gk39ZU5cwMLPkcaAo_CEALw_wcB)
* [Create an Amazon Kendra Index](https://docs.aws.amazon.com/kendra/latest/dg/create-index.html) with your RAG documentation
* Modify the MCP Config file with your Kendra Indexes properties as indicated below.

### Use Cases:

* Enhancing your existing MCP-enabled ChatBot with additional RAG indices
* Enhancing the responses from coding tools such as Cline, Cursor, Windsurf, Q Developer, etc.

### Tools:

#### KendraQueryTool

  - The KendraQueryTool takes the query specified by the user and queries the configured Kendra Index. It returns the content of the query to Amazon Kendra and the LLM will use that to augment the response generation.
  - Required Parameters: Query (str)
  - Example: `Can you help me understand how to implement a progress event in the CreateHandler using Java? Use the KendraQueryTool to gain additional context.`


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
