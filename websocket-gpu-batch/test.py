#!/usr/bin/env python3

import asyncio
import websockets
import sys
import wave

async def run_test(uri):
    async with websockets.connect(uri) as websocket:

        wf = wave.open(sys.argv[1], "rb")
        await websocket.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
        buffer_size = 6400 # 0.4 seconds of audio, don't make it too small otherwise compute will be slow
        while True:
            data = wf.readframes(buffer_size)

            if len(data) == 0:
                break

            await websocket.send(data)
            print (await websocket.recv())

        await websocket.send('{"eof" : 1}')
        print (await websocket.recv())

asyncio.run(run_test('ws://localhost:2700'))
