from typing import Iterator

from src.xingchen_mcp_server.server import XFXingchenAPI


def test_chat():
    config_path = "../../config.yaml"
    xingchen_api = XFXingchenAPI(config_path)
    resp = xingchen_api.chat_message(
        xingchen_api.data[0],
        {
            "AGENT_USER_INPUT": "a picture of a cat"
        }
    )
    if isinstance(resp, Iterator):
        for res in resp:
            print(res)
    else:
        print(resp)
