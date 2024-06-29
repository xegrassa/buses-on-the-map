import trio
import logging

from trio_websocket import open_websocket_url

logger = logging.getLogger(__name__)


INVALID_JSON = "a"
EMPTY_JSON = "{}"


async def main():
    try:
        async with open_websocket_url("ws://127.0.0.1:8080") as ws:
            await ws.send_message(INVALID_JSON)
            await ws.send_message(EMPTY_JSON)

            while True:
                message = await ws.get_message()
                print(f"Response: {message}")
    except OSError as ose:
        logging.error("Connection attempt failed: %s", ose)


trio.run(main)
