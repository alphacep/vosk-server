#!/usr/bin/env python3

import json
import os
import sys
import asyncio
import pathlib
import websockets
import concurrent.futures
import logging
from vosk import Model, KaldiRecognizer

# Enable loging if needed
# logger = logging.getLogger('websockets')
# logger.setLevel(logging.INFO)
# logger.addHandler(logging.StreamHandler())

vosk_interface = os.environ.get('VOSK_SERVER_INTERFACE', '0.0.0.0')
vosk_port = int(os.environ.get('VOSK_SERVER_PORT', 2700))
vosk_model_path = os.environ.get('VOSK_MODEL_PATH', 'model')

if len(sys.argv) > 1:
   vosk_model_path = sys.argv[1]

model = Model(vosk_model_path)
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

    rec = None
    word_list = None
    sample_rate = 8000.0

    while True:

        message = await websocket.recv()

        # Load configuration if provided
        if isinstance(message, str) and 'config' in message:
            jobj = json.loads(message)['config']
            if 'word_list' in jobj:
                word_list = jobj['word_list']
            if 'sample_rate' in jobj:
                sample_rate = float(jobj['sample_rate'])
            continue

        # Create the recognizer, word list is temporary disabled since not every model supports it
        if not rec:
            if False and word_list:
                 rec = KaldiRecognizer(model, sample_rate, word_list)
            else:
                 rec = KaldiRecognizer(model, sample_rate)

        response, stop = await loop.run_in_executor(pool, process_chunk, rec, message)
        await websocket.send(response)
        if stop: break

start_server = websockets.serve(
    recognize, vosk_interface, vosk_port)

loop.run_until_complete(start_server)
loop.run_forever()
