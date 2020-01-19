#!/usr/bin/python3

import requests

r = requests.post("https://api.alphacephei.com/tts", data={'text' : "Hello world!"})
fn = open("tts.wav", "wb")
fn.write(r.content)
fn.close()
