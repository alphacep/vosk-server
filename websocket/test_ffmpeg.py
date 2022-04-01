#!/usr/bin/env python3

import asyncio
import websockets
import sys

async def run_test(uri):
    async with websockets.connect(uri) as websocket:

        proc = await asyncio.create_subprocess_exec(
                       'ffmpeg', '-nostdin', '-loglevel', 'quiet', '-i', sys.argv[1],
                       '-ar', '16000', '-ac', '1', '-f', 's16le', '-',
                       stdout=asyncio.subprocess.PIPE)

        await websocket.send('{ "config" : { "sample_rate" : 16000 } }')

        while True:
            data = await proc.stdout.read(8000)

            if len(data) == 0:
                break

            await websocket.send(data)
            print (await websocket.recv())

        await websocket.send('{"eof" : 1}')
        print (await websocket.recv())

        await proc.wait()

asyncio.run(run_test('ws://localhost:2700'))
