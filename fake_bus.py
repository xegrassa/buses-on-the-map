import json
import random
from itertools import cycle, islice

import trio
from trio import MemorySendChannel, MemoryReceiveChannel
from trio_websocket import open_websocket_url

from helpers import generate_bus_id, load_routes

SERVER_URL = 'ws://127.0.0.1:8080'
CHANNEL_COUNT = 5

ROUTE_COUNT = 10
BUS_ON_ROUTE_COUNT = 20


async def run_bus(send_channel: MemorySendChannel, route, bus_id):
    point_count = len(route['coordinates'])
    start_point = random.randint(0, point_count - 1)
    coordinates = islice(cycle(route['coordinates']), start_point, None)
    messages = (
        {
            "busId": bus_id,
            "lat": lat,
            "lng": lng,
            "route": route['name']
        } for lat, lng in coordinates
    )
    async with send_channel:
        for msg in messages:
            await send_channel.send(json.dumps(msg, ensure_ascii=False))
            await trio.sleep(1)


async def send_updates(server_address: str, receive_channel: MemoryReceiveChannel):
    """Собирает и отправляет данные."""
    try:
        async with open_websocket_url(server_address) as ws:
            while True:
                msg = await receive_channel.receive()
                await ws.send_message(msg)
    except OSError as ose:
        print('Connection attempt failed: %s' % ose)


async def main():
    routes = load_routes()

    channels = [trio.open_memory_channel(0) for _ in range(CHANNEL_COUNT)]
    async with trio.open_nursery() as nursery:
        try:
            for _ in range(ROUTE_COUNT):
                route = next(routes)
                for index in range(BUS_ON_ROUTE_COUNT):
                    send_channel, _ = random.choice(channels)
                    bus_id = generate_bus_id(route_id=route['name'], bus_index=index)
                    nursery.start_soon(run_bus, send_channel, route, bus_id)
                    print(f"Place new bus #{index} on the map. Route {route['name']}")
        except StopIteration:
            print('Запущены все возможные маршруты')

        for _, receive_channel in channels:
            nursery.start_soon(send_updates, SERVER_URL, receive_channel)
        print(f'Запущены {len(channels)} каналов для отправки сообщений серверу')


if __name__ == '__main__':
    trio.run(main)
