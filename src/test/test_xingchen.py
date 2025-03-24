import logging

from typing import Iterator

from src.xingchen_mcp_server.server import xingchen_api


def test_chat():

    resp = xingchen_api.chat_message(
        xingchen_api.data[0],
        {
            "AGENT_USER_INPUT": "a picture of a cat"
        }
    )
    if isinstance(resp, Iterator):
        for res in resp:
            logging.info(res)
    else:
        logging.info(resp)
