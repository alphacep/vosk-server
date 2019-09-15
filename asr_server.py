#!/usr/bin/env python3

import asyncio
import pathlib
import websockets
import concurrent.futures
from kaldi_recognizer import Model, KaldiRecognizer

model = Model("model")
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
    rec = KaldiRecognizer(model);
    while True:
        message = await websocket.recv()
        response, stop = await loop.run_in_executor(pool, process_chunk, rec, message)
        await websocket.send(response)
        if stop: break

start_server = websockets.serve(
    recognize, '127.0.0.1', 2609)

loop.run_until_complete(start_server)
loop.run_forever()
