#!/usr/bin/env python3

import asyncio
import websockets
import sys
import srt
import json
import datetime
import wave

WORDS_PER_LINE = 7

async def run_test(uri):
    async with websockets.connect(uri) as websocket:
        wf = wave.open(sys.argv[1], "rb")
        await websocket.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))

        results = []
        buffer_size = int(wf.getframerate() * 0.2) # 0.2 seconds of audio
        while True:
            data = wf.readframes(buffer_size)

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


asyncio.run(run_test('ws://localhost:2700'))
