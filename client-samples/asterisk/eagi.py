#!/usr/bin/python3

from asterisk.agi import *
import os
from websocket import create_connection
import json

AUDIO_FD = 3
CONTENT_TYPE = 'audio/l16; rate=8000; channels=1'
ACCEPT = 'audio/pcm'


def process_chunk(agi, ws, buf):
    ws.send_binary(buf)
    res = json.loads(ws.recv())
    if 'result' in res:
        text = " ".join([w['word'] for w in res['result']])
        agi.verbose(text)
        os.system("espeak -w /tmp/response22.wav \"" + text.encode('utf-8') + "\"")
        os.system("sox /tmp/response22.wav -r 8000 /tmp/response.wav")
        agi.stream_file("/tmp/response")
        os.remove("/tmp/response.wav")

def startAGI():
    agi = AGI()
    agi.verbose("EAGI script started...")
    ani = agi.env['agi_callerid']
    did = agi.env['agi_extension']
    agi.verbose("Call answered from: %s to %s" % (ani, did))

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
