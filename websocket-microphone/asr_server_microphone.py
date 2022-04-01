#!/usr/bin/env python3

import json
import os
import sys
import asyncio
import websockets
import logging
import sounddevice as sd
import argparse
import queue

from vosk import Model, KaldiRecognizer

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    loop.call_soon_threadsafe(audio_queue.put_nowait, bytes(indata))

async def serve_client(websocket, path):
    clients.add(websocket)
    print ("Client connected from", websocket)
    await websocket.wait_closed()
    clients.remove(websocket)

async def recognize_microphone():
    global audio_queue

    model = Model(args.model)
    audio_queue = asyncio.Queue()
    
    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 2000, device=args.device, dtype='int16',
                            channels=1, callback=callback) as device:

        logging.info("Running recognition")
        rec = KaldiRecognizer(model, device.samplerate)
        while True:
            data = await audio_queue.get()
            if rec.AcceptWaveform(data):
                result = rec.Result()
                logging.info(result)
                websockets.broadcast(clients, result)

async def main():

    global args
    global clients
    global loop

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-l', '--list-devices', action='store_true',
                        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(description="ASR Server",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     parents=[parser])
    parser.add_argument('-m', '--model', type=str, metavar='MODEL_PATH',
                        help='Path to the model', default='model')
    parser.add_argument('-i', '--interface', type=str, metavar='INTERFACE',
                        help='Bind interface', default='0.0.0.0')
    parser.add_argument('-p', '--port', type=int, metavar='PORT',
                        help='Port', default=2700)
    parser.add_argument('-d', '--device', type=int_or_str,
                        help='input device (numeric ID or substring)')
    parser.add_argument('-r', '--samplerate', type=int, help='sampling rate', default=16000)
    args = parser.parse_args(remaining)
    
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_running_loop()
    clients = set()

    logging.info("Listening on %s:%d", args.interface, args.port)

    await asyncio.gather(
        websockets.serve(serve_client, args.interface, args.port),
                         recognize_microphone())

if __name__ == '__main__':
    asyncio.run(main())
