import json
import os
from itertools import cycle

import trio
from trio_websocket import open_websocket_url

SERVER_URL = 'ws://127.0.0.1:8080'


def load_routes(directory_path='routes'):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf8') as file:
                yield json.load(file)


async def run_bus(url, route, bus_id, sem):
    async with sem:
        coordinates = cycle(route['coordinates'])
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
    sem = trio.Semaphore(2)
    async with trio.open_nursery() as nursery:
        for route in load_routes():
            async with sem:
                bus_id = route['name'] + '-qwerty'
                nursery.start_soon(run_bus, SERVER_URL, route, bus_id, sem)
                print(f'Запустил {bus_id}')


if __name__ == '__main__':
    trio.run(main)
