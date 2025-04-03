import logging

from typing import Iterator

from src.mcp_server.entities.ifly_client import IFlyWorkflowClient


def test_chat():
    ifly_client = IFlyWorkflowClient()
    resp = ifly_client.chat_message(
        ifly_client.flows[0],
        {
            "AGENT_USER_INPUT": "a picture of a cat"
        }
    )
    if isinstance(resp, Iterator):
        for res in resp:
            logging.info(res)
    else:
        logging.info(resp)
