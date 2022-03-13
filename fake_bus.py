import json
from itertools import cycle

import trio
from trio_websocket import open_websocket_url


async def main():
    with open('routes/156.json', 'r', encoding='utf8') as f:
        route_156 = json.load(f)
    coordinates = cycle(route_156['coordinates'])

    try:
        async with open_websocket_url('ws://127.0.0.1:8000') as ws:
            while True:
                lat, lng = next(coordinates)
                msg = {
                    "busId": "156-0",
                    "lat": lat,
                    "lng": lng,
                    "route": "156"
                }
                await ws.send_message(json.dumps(msg))
                await trio.sleep(1)
    except OSError as ose:
        print('Connection attempt failed: %s' % ose)


if __name__ == '__main__':
    trio.run(main)
