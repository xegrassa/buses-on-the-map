import json
import random
from itertools import cycle, islice

import trio
from trio_websocket import open_websocket_url

from helpers import generate_bus_id, load_routes

SERVER_URL = 'ws://127.0.0.1:8080'
ROUTE_COUNT = 3
BUS_ON_ROUTE_COUNT = 10


async def run_bus(url, route, bus_id):
    point_count = len(route['coordinates'])
    start_point = random.randint(0, point_count - 1)
    coordinates = islice(cycle(route['coordinates']), start_point, None)
    try:
        async with open_websocket_url(url) as ws:
            for lat, lng in coordinates:
                msg = {
                    "busId": bus_id,
                    "lat": lat,
                    "lng": lng,
                    "route": route['name']
                }
                await ws.send_message(json.dumps(msg, ensure_ascii=False))
                await trio.sleep(2)
    except OSError as ose:
        print('Connection attempt failed: %s' % ose)


async def main():
    routes = load_routes()
    async with trio.open_nursery() as nursery:
        try:
            for _ in range(ROUTE_COUNT):
                route = next(routes)
                for index in range(BUS_ON_ROUTE_COUNT):
                    bus_id = generate_bus_id(route_id=route['name'], bus_index=index)
                    nursery.start_soon(run_bus, SERVER_URL, route, bus_id)
                    print(f"Place new bus #{index} on the map. Route {route['name']}")
        except StopIteration:
            print('Запущены все возможные маршруты')


if __name__ == '__main__':
    trio.run(main)
