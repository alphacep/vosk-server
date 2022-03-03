#!/usr/bin/env python3

import json
import os
import sys
import asyncio
import pathlib
import websockets
import logging

from vosk import BatchModel, BatchRecognizer, GpuInit


async def recognize(websocket, path):
    global args
    global loop
    global pool
    global model

    rec = None

    logging.info(f'Connection from {websocket.remote_address}');

    while True:

        message = await websocket.recv()

        # Load configuration if provided
        if isinstance(message, str) and 'config' in message:
            jobj = json.loads(message)['config']
            logging.info("Config %s", jobj)
            if 'sample_rate' in jobj:
                sample_rate = float(jobj['sample_rate'])
            continue

        # Create the recognizer, word list is temporary disabled since not every model supports it
        if not rec:
            rec = BatchRecognizer(model, sample_rate)

        if message == '{"eof" : 1}':
            rec.FinishStream()
            break

        if isinstance(message, str) and 'config' in message:
            continue

        rec.AcceptWaveform(message)

        while rec.GetPendingChunks() > 0:
            await asyncio.sleep(0.1)

        res = rec.Result()
        if len(res) == 0:
            await websocket.send('{ "partial" : "" }')
        else:
            await websocket.send(res)

    while rec.GetPendingChunks() > 0:
        await asyncio.sleep(0.1)

    res = rec.Result()
    await websocket.send(res)

def start():

    global model
    global args
    global loop

    # Enable loging if needed
    #
    # logger = logging.getLogger('websockets')
    # logger.setLevel(logging.INFO)
    # logger.addHandler(logging.StreamHandler())
    logging.basicConfig(level=logging.INFO)

    args = type('', (), {})()

    args.interface = os.environ.get('VOSK_SERVER_INTERFACE', '0.0.0.0')
    args.port = int(os.environ.get('VOSK_SERVER_PORT', 2700))

    GpuInit()

    model = BatchModel()

    loop = asyncio.get_event_loop()

    start_server = websockets.serve(
        recognize, args.interface, args.port)

    logging.info("Listening on %s:%d", args.interface, args.port)
    loop.run_until_complete(start_server)
    loop.run_forever()


if __name__ == '__main__':
    start()
