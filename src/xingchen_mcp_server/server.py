import asyncio
import json
import os
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Dict, Any

import mcp.server.stdio
import mcp.types as types
import requests
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from omegaconf import OmegaConf


@dataclass
class Param:
    name: str
    type: str
    description: str
    required: bool


@dataclass
class Flow:
    flow_id: str
    name: str
    description: str
    api_key: str
    params: List[Param] = field(default_factory=list)


class XFXingchenAPI(ABC):
    def __init__(self,
                 config_path):
        if not config_path:
            raise ValueError("config path not provided")

        def load_flows_from_yaml(file_path: str) -> List[Flow]:
            data = OmegaConf.load(file_path)
            return [Flow(**flow) for flow in data]

        self.data = load_flows_from_yaml(config_path)
        self.name_idx: Dict[str, int] = {}
        for i, flow in enumerate(self.data):
            self.name_idx[flow.name] = i

    def chat_message(
            self,
            flow: Flow,
            inputs: Dict[str, Any],
            stream: bool = True
    ):
        url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {flow.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "flow_id": flow.flow_id,
            "parameters": inputs,
            "stream": stream
        }
        response = requests.post(
            url, headers=headers, json=data, stream=stream)
        response.raise_for_status()
        if stream:
            for line in response.iter_lines():
                if line:
                    if line.startswith(b'data:'):
                        try:
                            json_data = json.loads(line[5:].decode('utf-8'))
                            yield json_data
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {line}")
        else:
            return response.json()


config_path = os.getenv("CONFIG_PATH")
# config_path = "/Users/hygao1024/Projects/src/github.com/hygao1024/xingchen-mcp-server/config.yaml"
server = Server("xingchen_mcp_server")
xingchen_api = XFXingchenAPI(config_path)


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    tools = []
    for i, flow in enumerate(xingchen_api.data):
        inputSchema = {
            "type": "object",
            "properties": {
                param.name: {
                    "type": param.type,
                    "description": param.description
                } for param in flow.params
            },
            "required": [param.name for param in flow.params if param.required]
        }

        tools.append(
            types.Tool(
                name=flow.name,
                description=flow.description,
                inputSchema=inputSchema,
            )
        )
    return tools


@server.call_tool()
async def handle_call_tool(
        name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name in xingchen_api.name_idx:
        flow = xingchen_api.data[xingchen_api.name_idx[name]]
        responses = xingchen_api.chat_message(
            flow,
            arguments,
        )
        mcp_out = []
        for res in responses:
            mcp_out.append(
                types.TextContent(
                    type='text',
                    text=res["choices"][0]["delta"]["content"]
                )
            )
        return mcp_out
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="xingchen_mcp_server",
                server_version="0.0.1",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
