import json
import logging
import random
from itertools import cycle, islice
import asyncclick as click
import trio
import trio_websocket
from trio import MemorySendChannel, MemoryReceiveChannel
from trio_websocket import open_websocket_url

from helpers import (
    generate_bus_id,
    load_routes,
    configure_logger,
    relaunch_on_disconnect,
)

logger = logging.getLogger(__name__)


async def run_bus(send_channel: MemorySendChannel, route, bus_id, refresh_timeout):
    point_count = len(route["coordinates"])
    start_point = random.randint(0, point_count - 1)
    coordinates = islice(cycle(route["coordinates"]), start_point, None)
    messages = (
        {"busId": bus_id, "lat": lat, "lng": lng, "route": route["name"]}
        for lat, lng in coordinates
    )
    async with send_channel:
        for msg in messages:
            await send_channel.send(json.dumps(msg, ensure_ascii=False))
            await trio.sleep(refresh_timeout)


@relaunch_on_disconnect(timeout=5)
async def send_updates(server_address: str, receive_channel: MemoryReceiveChannel):
    """Собирает и отправляет данные."""
    async with open_websocket_url(server_address) as ws:
        logger.debug(f"Подключение к серверу: {server_address} удалось")
        while True:
            msg = await receive_channel.receive()
            await ws.send_message(msg)


@click.command()
@click.option(
    "--server", default="ws://127.0.0.1:8080", help="Host:Port. ex: 127.0.0.1:8080"
)
@click.option(
    "--emulator_id",
    default="",
    help="Префикс к busId на случай запуска нескольких экземпляров имитатора.",
)
@click.option(
    "--refresh_timeout",
    default=1,
    type=float,
    help="Задержка в обновлении координат сервера. ex: 0.5",
)
@click.option("-r", "--routes_number", default=20, help="Количество маршрутов.")
@click.option(
    "-x",
    "--buses_per_route",
    default=1,
    help="Количество автобусов на каждом маршруте.",
)
@click.option(
    "-w",
    "--websockets_number",
    "ws_number",
    default=1,
    help="Количество открытых веб-сокетов.",
)
@click.option("-v", "--verbose", count=True, default=2, help="Настройка логирования.")
async def main(
    server,
    routes_number,
    buses_per_route,
    ws_number,
    emulator_id,
    refresh_timeout,
    verbose,
):
    configure_logger(__name__, verbose)
    routes = load_routes()

    channels = [trio.open_memory_channel(0) for _ in range(ws_number)]
    async with trio.open_nursery() as nursery:
        try:
            for _ in range(routes_number):
                route = next(routes)
                for index in range(buses_per_route):
                    send_channel, _ = random.choice(channels)
                    bus_id = emulator_id + generate_bus_id(
                        route_id=route["name"], bus_index=index
                    )
                    nursery.start_soon(
                        run_bus, send_channel, route, bus_id, refresh_timeout
                    )
                    logger.debug(
                        f"Place new bus #{index} on the map. Route {route['name']}"
                    )
        except StopIteration:
            logger.info("Запущены все возможные маршруты")

        for _, receive_channel in channels:
            nursery.start_soon(send_updates, server, receive_channel)
        logger.info(f"Запущены {len(channels)} каналов для отправки сообщений серверу")


if __name__ == "__main__":
    try:
        main(_anyio_backend="trio")
    except* trio_websocket.HandshakeError as e:
        logger.critical("Не удалось соединиться с сервером")
    except* KeyboardInterrupt as e:
        logger.info("Скрипт остановлен")
