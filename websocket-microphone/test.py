#!/usr/bin/env python3

import asyncio
import websockets
import sys

async def listen_results(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            print (await websocket.recv())

asyncio.get_event_loop().run_until_complete(
    listen_results('ws://localhost:2700'))
