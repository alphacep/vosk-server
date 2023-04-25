#!/usr/bin/env python3

import wave
import sys
import traceback

from websocket import create_connection

ws = create_connection("ws://localhost:2700")

wf = wave.open(sys.argv[1], "rb")
ws.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
buffer_size = int(wf.getframerate() * 0.2) # 0.2 seconds of audio

try:

    while True:
        data = wf.readframes(buffer_size)

        if len(data) == 0:
            break

        ws.send_binary(data)
        print (ws.recv())
    ws.send('{"eof" : 1}')
    print (ws.recv())

except Exception as err:
    print(''.join(traceback.format_exception(type(err), err, err.__traceback__)))
