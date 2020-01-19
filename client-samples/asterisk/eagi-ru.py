#!/usr/bin/python3

from asterisk.agi import *
import os
from websocket import create_connection
import json
import uuid

AUDIO_FD = 3
CONTENT_TYPE = 'audio/l16; rate=8000; channels=1'
ACCEPT = 'audio/pcm'

def play_text(agi, text):
    fn = str(uuid.uuid4())
    os.system("espeak -v ru -w /tmp/%s.22.wav \"%s\"" % (fn, text))
    os.system("sox /tmp/%s.22.wav -r 8000 /tmp/%s.wav" % (fn, fn))
    agi.stream_file("/tmp/%s" % (fn))
    os.remove("/tmp/%s.22.wav" % (fn)) 
    os.remove("/tmp/%s.wav" % (fn)) 
    os.read(AUDIO_FD, 1000000) # Read remaining chunks

def process_chunk(agi, ws, buf):
    ws.send_binary(buf)
    res = json.loads(ws.recv())
    agi.verbose(str(res))
    if 'text' in res:
        play_text(agi, "Распознано " + res['text'])

def startAGI():
    agi = AGI()
    agi.verbose("EAGI script started...")
    ani = agi.env['agi_callerid']
    did = agi.env['agi_extension']
    agi.verbose("Call answered from: %s to %s" % (ani, did))
    play_text(agi, "Привет")

    ws = create_connection("ws://localhost:2700")
    try:
        while True:
            data = os.read(AUDIO_FD, 8000)
            if not data:
                break
            process_chunk(agi, ws, data)
    finally:
        ws.close()

startAGI()
