#!/usr/bin/python3

from kaldi_recognizer import Model, KaldiRecognizer
import sys
import json

model = Model()
rec = KaldiRecognizer(model)

wf = open(sys.argv[1], "rb")
wf.read(44) # skip header

while True:
    data = wf.read(2000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        res = json.loads(rec.Result())
        print (res)
    else:
        res = json.loads(rec.PartialResult())
        print (res)

res = json.loads(rec.FinalResult())
print (res)
