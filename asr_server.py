#!/usr/bin/env python3

import asyncio
import pathlib
import websockets
from kaldi_recognizer import Model, KaldiRecognizer

model = Model()

async def recognize(websocket, path):
    rec = KaldiRecognizer(model);
    while True:
        message = await websocket.recv()
        if message == '{"eof" : 1}':
            await websocket.send(rec.FinalResult())
            break
        if rec.AcceptWaveform(message):
            await websocket.send(rec.Result())
        else:
            await websocket.send(rec.PartialResult())

start_server = websockets.serve(
    recognize, '127.0.0.1', 2609)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
