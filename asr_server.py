#!/usr/bin/env python3

import sys
import asyncio
import pathlib
import websockets
import concurrent.futures
from vosk import Model, KaldiRecognizer

if len(sys.argv) > 1:
   model_path = sys.argv[1]
else:
   model_path = "model"

model = Model(model_path)
pool = concurrent.futures.ThreadPoolExecutor()
loop = asyncio.get_event_loop()

def process_chunk(rec, message):
    if message == '{"eof" : 1}':
        return rec.FinalResult(), True
    elif rec.AcceptWaveform(message):
        return rec.Result(), False
    else:
        return rec.PartialResult(), False

async def recognize(websocket, path):
    rec = KaldiRecognizer(model, 8000);
    while True:
        message = await websocket.recv()
        response, stop = await loop.run_in_executor(pool, process_chunk, rec, message)
        await websocket.send(response)
        if stop: break

port = int(os.environ.get("PORT", 2700))

start_server = websockets.serve(
    recognize, '0.0.0.0', port)

loop.run_until_complete(start_server)
loop.run_forever()
