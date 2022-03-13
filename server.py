import json

import trio
from trio_websocket import serve_websocket, ConnectionClosed
from itertools import cycle

BUSES = {
    "msgType": "Buses",
    "buses": [
        {"busId": "c790сс", "lat": 55.7500, "lng": 37.600, "route": "120"},
        {"busId": "a134aa", "lat": 55.7494, "lng": 37.621, "route": "670к"},
    ]
}

BUS = {
    "msgType": "Buses",
    "buses": [
        {"busId": "c790сс", "lat": 0, "lng": 0, "route": "156"},
    ]
}



async def echo_server(request):
    with open('routes/156.json', 'r', encoding='utf8') as f:
        route_156 = json.load(f)

    ws = await request.accept()
    z = cycle(route_156['coordinates'])
    while True:

        i, j = next(z)
        BUS['buses'][0]['lat'] = i
        BUS['buses'][0]['lng'] = j
        print(BUS)

        try:
            await ws.send_message(json.dumps(BUS))
            await trio.sleep(1)
        except ConnectionClosed:
            break


async def main():
    await serve_websocket(echo_server, '127.0.0.1', 8000, ssl_context=None)


if __name__ == '__main__':
    trio.run(main)
