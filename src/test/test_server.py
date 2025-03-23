from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",  # Executable
    args=["/Users/hygao1024/Projects/src/github.com/hygao1024/xingchen-mcp-server/src/xingchen_mcp_server/server.py"],  # Optional command line arguments
    env={
        "CONFIG_PATH": "/Users/hygao1024/Projects/src/github.com/hygao1024/xingchen-mcp-server/config.yaml"
    },  # Optional environment variables
)


# Optional: create a sampling callback
async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello, world! from model",
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )


async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=handle_sampling_message
        ) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(tools)

            # # Call a tool
            result = await session.call_tool("test", arguments={"AGENT_USER_INPUT": "你好"})
            print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())