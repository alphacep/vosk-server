#!/usr/bin/python3

from asterisk.agi import *
import os
from websocket import create_connection
import json
import traceback

AUDIO_FD = 3
CONTENT_TYPE = 'audio/l16; rate=8000; channels=1'
ACCEPT = 'audio/pcm'

def process_chunk(agi, ws, buf):
    agi.verbose("Processing chunk")
    ws.send_binary(buf)
    res = json.loads(ws.recv())
    agi.verbose("Result: " + str(res))
    if 'result' in res:
        text = " ".join([w['word'] for w in res['result']])
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
    ws.send('{ "config" : { "sample_rate" : 8000 } }')
    agi.verbose("Connection created")

    try:
        while True:
            data = os.read(AUDIO_FD, 8000)
            if not data:
                break
            process_chunk(agi, ws, data)
    except Exception as err:
        agi.verbose(''.join(traceback.format_exception(type(err), err, err.__traceback__)).replace('\n', ' '))
    finally:
        ws.close()

startAGI()
