import json
import logging
from functools import partial

import trio
from trio_websocket import ConnectionClosed, serve_websocket

logger = logging.getLogger(__name__)
buses = {}


async def get_buses_position(request):
    """Принимает данные о автобусах и сохраняет их."""
    ws = await request.accept()
    while True:
        try:
            message = await ws.get_message()
            logger.debug(f'{message=}')
            bus_info = json.loads(message)
            buses[bus_info['busId']] = bus_info
        except ConnectionClosed:
            break


async def talk_to_browser(request):
    buses_message = {
        "msgType": "Buses",
        "buses": None
    }
    ws = await request.accept()
    while True:
        try:
            buses_message['buses'] = [bus_info for bus_info in buses.values()]
            logger.debug(f'{buses_message=}')
            await ws.send_message(json.dumps(buses_message))
            await trio.sleep(1)
        except ConnectionClosed:
            break


async def main():
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(filename)s | %(levelname)-8s | [%(asctime)s] | %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    async with trio.open_nursery() as nursery:
        filled_serve_websocket = partial(serve_websocket, host='127.0.0.1', ssl_context=None)
        nursery.start_soon(partial(filled_serve_websocket, get_buses_position, port=8080))
        nursery.start_soon(partial(filled_serve_websocket, talk_to_browser, port=8001))
        # await serve_websocket(echo_server, '127.0.0.1', 8000, ssl_context=None)


if __name__ == '__main__':
    trio.run(main)
