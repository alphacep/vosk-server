#!/usr/bin/env python3

import asyncio
import websockets
import sys
import wave

async def hello(uri):
    async with websockets.connect(uri) as websocket:
        wf = wave.open(sys.argv[1], "rb")
        await websocket.send('''{"config" : 
                    { "word_list" : "zero one two three four five six seven eight nine oh",
                      "sample_rate" : 16000.0}}''')
        while True:
            data = wf.readframes(4000)

            if len(data) == 0:
                break

            await websocket.send(data)
            print (await websocket.recv())

        await websocket.send('{"eof" : 1}')
        print (await websocket.recv())

asyncio.get_event_loop().run_until_complete(
    hello('ws://localhost:2700'))
