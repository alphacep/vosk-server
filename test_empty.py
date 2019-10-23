#!/usr/bin/python3

from kaldi_recognizer import Model, KaldiRecognizer
import sys
import json

model = Model("model")
rec = KaldiRecognizer(model)

res = json.loads(rec.FinalResult())
print (res)
