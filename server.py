import logging
from functools import partial
from contextlib import suppress
from typing import Never

from helpers import configure_logger, validate_new_bounds, validate_bus_position
import trio
from trio_websocket import (
    ConnectionClosed,
    serve_websocket,
    WebSocketRequest,
    WebSocketConnection,
)
from dataclasses import asdict
import json
import argparse

from schemas import Bus, WindowBounds

logger = logging.getLogger(__name__)
buses: dict[str, Bus] = {}


async def send_buses(ws, bounds: WindowBounds):
    """Отправляет информацию браузеру о том какие автобусы видны в границах браузера."""
    visible_buses = [
        bus for bus in buses.values() if bounds.is_inside(bus.lat, bus.lng)
    ]
    logger.debug(f"{len(visible_buses)} buses inside bounds")

    message = {"msgType": "Buses", "buses": [asdict(bus) for bus in visible_buses]}
    await ws.send_message(json.dumps(message))


async def listen_browser(ws: WebSocketConnection, bounds):
    """Принимает сообщение от Браузера через WebSocket и обновляет Глобальную переменную границ окна."""
    while True:
        try:
            message = await ws.get_message()

            new_bounds, err = validate_new_bounds(message)
            if err:
                await ws.send_message(err)
                continue

            logger.debug(f"Границы окна Браузера: {message}")
            bounds.update(**new_bounds.data.model_dump())
        except Exception:
            await trio.sleep(3)


async def tell_browser(ws: WebSocketConnection, bounds) -> Never:
    """Отправляет сообщение в Браузер через WebSocket."""
    while True:
        try:
            await send_buses(ws, bounds)
            await trio.sleep(1)
        except Exception:
            await trio.sleep(3)


async def communicate_with_browser(request: WebSocketRequest) -> Never:
    # listen_browser изменяет WindowBounds, на актуальные границы браузера !!!
    bounds = WindowBounds(0, 0, 0, 0)

    ws: WebSocketConnection = await request.accept()
    async with trio.open_nursery() as nursery:
        nursery.start_soon(tell_browser, ws, bounds)
        nursery.start_soon(listen_browser, ws, bounds)


async def get_buses_position(request) -> Never:
    """Принимает данные об автобусах и сохраняет их."""
    ws: WebSocketConnection = await request.accept()
    while True:
        try:
            message = await ws.get_message()

            bus, err = validate_bus_position(message)
            if err:
                await ws.send_message(err)
                continue

            logger.debug(f"NEW Buses Positon: {message}")
            buses[bus.busId] = Bus(**bus.model_dump())
        except ConnectionClosed:
            break


async def main():
    filled_serve_websocket = partial(
        serve_websocket, host="127.0.0.1", ssl_context=None
    )
    async with trio.open_nursery() as nursery:
        nursery.start_soon(partial(filled_serve_websocket, get_buses_position, port=args.bus_port))
        nursery.start_soon(partial(filled_serve_websocket, communicate_with_browser, port=args.browser_port))


def prepare_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bus-port", type=int, default=8080)
    parser.add_argument("--browser-port", type=int, default=8001)
    parser.add_argument("-v", "--verbose", action="count", default=3, help="Enable logging")

    return parser.parse_args()


if __name__ == "__main__":
    args = prepare_args()
    configure_logger(__name__, args.verbose)
    configure_logger("helpers", args.verbose)

    logger.info("Server starting...")
    with suppress(KeyboardInterrupt):
        trio.run(main)
    logger.info("Server stop")
