#!/usr/bin/python3.6

from websocket import create_connection

import sys
import wave

inf = "test.wav"
if len(sys.argv) > 1:
    inf = sys.argv[1]

def process_chunk(chan_id, ws, buf):
    ws.send_binary(buf)
    res = ws.recv()
    print(chan_id, res)

def process_final_chunk(chan_id, ws):
    ws.send('{"eof" : 1}')
    res = ws.recv()
    print(chan_id, res)
    ws.close()

def split_stereo(buf):
    buf1 = b""
    buf2 = b""
    for i in range(0, len(buf), 4):
        buf1 += buf[i:i+2]
        buf2 += buf[i+2:i+4]
    return buf1, buf2

def test_stream():
    ws1 = create_connection("wss://api.alphacephei.com/asr/en/")
    ws2 = create_connection("wss://api.alphacephei.com/asr/en/")

    infile = wave.open(inf, "rb")
    assert (infile.getnchannels() == 2)

    while True:
        buf = infile.readframes(8000)
        if not buf:
            break
        buf1, buf2 = split_stereo(buf)
        process_chunk(1, ws1, buf1)
        process_chunk(2, ws2, buf2)

    process_final_chunk(1, ws1)
    process_final_chunk(2, ws2)

test_stream()
