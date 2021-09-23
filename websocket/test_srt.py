#!/usr/bin/env python3

import asyncio
import websockets
import sys
import srt
import json
import datetime

WORDS_PER_LINE = 7

async def run_test(uri):
    async with websockets.connect(uri) as websocket:
        wf = open(sys.argv[1], "rb")

        results = []
        while True:
            data = wf.read(8000)

            if len(data) == 0:
                break

            await websocket.send(data)
            results.append(await websocket.recv())

        await websocket.send('{"eof" : 1}')
        results.append(await websocket.recv())

        subs = []
        for i, res in enumerate(results):
           jres = json.loads(res)
           if not 'result' in jres:
               continue
           words = jres['result']
           for j in range(0, len(words), WORDS_PER_LINE):
               line = words[j : j + WORDS_PER_LINE] 
               s = srt.Subtitle(index=len(subs), 
                   content=" ".join([l['word'] for l in line]),
                   start=datetime.timedelta(seconds=line[0]['start']), 
                   end=datetime.timedelta(seconds=line[-1]['end']))
               subs.append(s)

        print(srt.compose(subs))


asyncio.get_event_loop().run_until_complete(
    run_test('ws://localhost:2700'))
