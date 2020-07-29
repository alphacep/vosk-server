#!/usr/bin/env python3

import json
import os
import sys
import asyncio
import pathlib
import websockets
import concurrent.futures
import logging
import re
import base64
from vosk import Model, KaldiRecognizer

# Enable loging if needed
#
# logger = logging.getLogger('websockets')
# logger.setLevel(logging.INFO)
# logger.addHandler(logging.StreamHandler())

vosk_interface = os.environ.get('VOSK_SERVER_INTERFACE', '0.0.0.0')
vosk_port = int(os.environ.get('VOSK_SERVER_PORT', 2700))
vosk_model_path = os.environ.get('VOSK_MODEL_PATH', 'model')
vosk_sample_rate = float(os.environ.get('VOSK_SAMPLE_RATE', 8000))

if len(sys.argv) > 1:
   vosk_model_path = sys.argv[1]

# Gpu part, uncomment if vosk-api has gpu support
#
# from vosk import GpuInit, GpuInstantiate
# GpuInit()
# def thread_init():
#     GpuInstantiate()
# pool = concurrent.futures.ThreadPoolExecutor(initializer=thread_init)

model = Model(vosk_model_path)
pool = concurrent.futures.ThreadPoolExecutor((os.cpu_count() or 1))
loop = asyncio.get_event_loop()

def parseGram(grammar: tuple) -> dict:
    gramdata = {}
    publicgrams = {}
    for line in grammar:
        line = line.strip()
        if line.startswith('<') and line.find('=') != -1  and line.find(';') != -1:
            key = line[1:line.index('>')]
            value = line[line.index('=')+1:line.index(';')].strip()
            value = value.replace('*', '.*')
            value = value.replace(']+', ')*')
            value = value.replace('[', '(')
            value = value.replace(']', '){0,1}')
            start = 0
            while(value.find('<', start)!=-1 and value.index('>', start)!=-1):
                gram = value[value.index('<', start)+1:value.index('>', start)].strip()
                gramregexp = gramdata.pop(gram)
                start = value.index('<', start)
                value = value.replace(value[start:value.index('>', start)+1], '(' + gramregexp + ')')
                start += len(gramregexp)+1
            value = value.strip()
            if value[-1] == '|':
                value = value[0:-1]
            value = value.replace('(', '(<')
            value = value.replace(')', '>)')
            value = value.replace(' ', '><')
            value = value.replace(')>', ')')
            value = value.replace('<|', '|')
            value = value.replace('|>', '|')
            value = value.replace('<(', '(')
            value = value.replace('}>', '}')
            value = value.replace('<<', '<')
            value = value.replace('>>', '>')
            if not value[0] in ['(', '<']:
                value = '<' + value
            if not value[-1] in [')', '}', '>']:
                value = value + '>'
            value = value.replace('<', '\\s*\\b')
            value = value.replace('>', '\\b\\s*')
            value = value.replace('\\b\\b', '\\b')
            value = value.replace('\\b\\s*\\b', '\\b')
            gramdata[key] = value
        if line.startswith('public ') and line.find('=') != -1  and line.find(';') != -1:
            key = line[line.index('<')+1:line.index('>')]
            value = line[line.index('=')+1:line.index(';')].strip()
            grams = []
            while(value.find('<')!=-1 and value.index('>')!=-1):
                gram = value[value.index('<')+1:value.index('>')].strip()
                grams.append(gram)
                value = value.replace(value[value.index('<'):value.index('>')+1], '')               
            publicgrams[key] = grams
    return gramdata, publicgrams

def testPhrase(phrase: str, grams: dict, publicgrams: tuple):
    matchedgram = None
    for variant in publicgrams:
        validgrams = publicgrams[variant]
        for gram in validgrams:
            pattern = re.compile(grams[gram])
            if pattern.search(phrase):
                matchedgram = gram
                break
        if matchedgram != None:
            break
    if matchedgram == None:
        matchedgram = 'unknown'
    return matchedgram

def process_chunk(rec, message, activegrammar, activepublicgrammar, last_text):
    if message == '{"eof" : 1}':
        result = json.loads(rec.FinalResult())
        if activegrammar != None and activepublicgrammar != None:
            result['grammar'] = testPhrase(result['text'], activegrammar, activepublicgrammar)
        result = json.dumps(result)
        return result, True
    elif rec.AcceptWaveform(message):
        result = json.loads(rec.Result())
        if activegrammar != None and activepublicgrammar != None:
            result['grammar'] = testPhrase(result['text'], activegrammar, activepublicgrammar)
        result = json.dumps(result)
        return result, False
    else:
        result = json.loads(rec.PartialResult())
        if activegrammar != None and activepublicgrammar != None:
            if result['partial'] != '':
                if result['partial'] in last_text:
                    if len(last_text) >= 2:
                        last_text.clear()
                        result = json.loads(rec.Result())
                        result['grammar'] = testPhrase(result['text'], activegrammar, activepublicgrammar)
                    else:
                        last_text.append(result['partial'])
                else:
                    last_text.clear()
                    last_text.append(result['partial'])
            else:
                last_text.clear()
        result = json.dumps(result)
        return result, False

async def recognize(websocket, path):

    rec = None
    word_list = None
    sample_rate = vosk_sample_rate
    last_text = []
    grammars = {}
    activegrammar = None
    activepublicgrammar = None
    print('Connect')

    while True:

        #Try to receive data, otherwise trait as socket closed by the remote side
        try:
            message = await websocket.recv()
        except:
            print('Connection broken')
            break

        # Load configuration if provided
        if isinstance(message, str) and 'config' in message:
            print('Config')
            jobj = json.loads(message)['config']
            if 'word_list' in jobj:
                word_list = jobj['word_list']
            if 'sample_rate' in jobj:
                sample_rate = float(jobj['sample_rate'])
            continue

        if isinstance(message, str) and 'newgrammar' in message:
            print('Load grammar')
            jobj = json.loads(message)
            if 'newgrammar' in jobj and 'grammar_data' in jobj:
                grammars[jobj['newgrammar']] = base64.b64decode(jobj['grammar_data']).decode('utf-8').splitlines()
            continue

        if isinstance(message, str) and 'setgrammar' in message:
            print('Activate grammar')
            jobj = json.loads(message)
            if 'setgrammar' in jobj:
                if jobj['setgrammar'] in grammars:
                    activegrammar, activepublicgrammar = parseGram(grammars[jobj['setgrammar']])
                else:
                    activegrammar = None
                    activepublicgrammar = None
            continue

        if isinstance(message, str) and 'delgrammar' in message:
            print('Unload grammar')
            jobj = json.loads(message)
            if 'delgrammar' in jobj:
                if jobj['delgrammar'] in grammars:
                    grammars.pop(jobj['delgrammar'])
            continue

        # Create the recognizer, word list is temporary disabled since not every model supports it
        if not rec:
            if False and word_list:
                 rec = KaldiRecognizer(model, sample_rate, word_list)
            else:
                 rec = KaldiRecognizer(model, sample_rate)

        response, stop = await loop.run_in_executor(pool, process_chunk, rec, message, activegrammar, activepublicgrammar, last_text)
        await websocket.send(response)
        if stop: break

start_server = websockets.serve(
    recognize, vosk_interface, vosk_port)

loop.run_until_complete(start_server)
loop.run_forever()
