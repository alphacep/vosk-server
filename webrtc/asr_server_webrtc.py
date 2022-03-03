#!/usr/bin/env python3

import json
import logging
import ssl
import sys
import os
import concurrent.futures
import asyncio

from pathlib import Path
from vosk import KaldiRecognizer, Model
from aiohttp import web
from aiohttp.web_exceptions import HTTPServiceUnavailable
from aiortc import RTCSessionDescription, RTCPeerConnection
from av.audio.resampler import AudioResampler

ROOT = Path(__file__).parent

vosk_interface = os.environ.get('VOSK_SERVER_INTERFACE', '0.0.0.0')
vosk_port = int(os.environ.get('VOSK_SERVER_PORT', 2700))
vosk_model_path = os.environ.get('VOSK_MODEL_PATH', 'model')
vosk_sample_rate = float(os.environ.get('VOSK_SAMPLE_RATE', 8000))
vosk_cert_file = os.environ.get('VOSK_CERT_FILE', None)
vosk_key_file = os.environ.get('VOSK_KEY_FILE', None)

model = Model(vosk_model_path)
pool = concurrent.futures.ThreadPoolExecutor((os.cpu_count() or 1))

def process_chunk(rec, message):
    try:
        res = rec.AcceptWaveform(message)
    except Exception:
        result = None
    else:
        if res > 0:
            result = rec.Result()
            o = json.loads(result)
            if 'result' in o:
                result = '{"text": "' +o['text']+ '"}'
        else:
            result = rec.PartialResult()
            o = json.loads(result)
            if o['partial'] == '':
                result = None
    return result


class KaldiTask:
    def __init__(self, user_connection):
        self.__resampler = AudioResampler(format='s16', layout='mono', rate=48000)
        self.__pc = user_connection
        self.__audio_task = None
        self.__track = None
        self.__channel = None
        self.__recognizer = KaldiRecognizer(model, 48000)


    async def set_audio_track(self, track):
        self.__track = track

    async def set_text_channel(self, channel):
        self.__channel = channel

    async def start(self):
        self.__audio_task = asyncio.create_task(self.__run_audio_xfer())

    async def stop(self):
        if self.__audio_task is not None:
            self.__audio_task.cancel()
            self.__audio_task = None

    async def __run_audio_xfer(self):
        loop = asyncio.get_running_loop()
        dataframes = bytearray(b"")
        max_frames_len = 8000
        while True:
            frame = await self.__track.recv()
            frame = self.__resampler.resample(frame)
            message = frame.planes[0].to_bytes()
            recv_frames = bytearray(message)
            dataframes += recv_frames
            if len(dataframes) > max_frames_len:
                wave_bytes = bytes(dataframes)
                result = await loop.run_in_executor(pool, process_chunk, self.__recognizer, wave_bytes)
                if result is not None:
                    print(result)
                    self.__channel.send(result)
                dataframes = bytearray(b"")

async def index(request):
    content = open(str(ROOT / 'static' / 'index.html')).read()
    return web.Response(content_type='text/html', text=content)


async def offer(request):

    params = await request.json()
    offer = RTCSessionDescription(
        sdp=params['sdp'],
        type=params['type'])

    pc = RTCPeerConnection()

    kaldi = KaldiTask(pc)

    @pc.on('datachannel')
    async def on_datachannel(channel):
        channel.send('{}') # Dummy message to make the UI change to "Listening"
        await kaldi.set_text_channel(channel)
        await kaldi.start()

    @pc.on('iceconnectionstatechange')
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == 'failed':
            await pc.close()

    @pc.on('track')
    async def on_track(track):
        if track.kind == 'audio':
            await kaldi.set_audio_track(track)

        @track.on('ended')
        async def on_ended():
            await kaldi.stop()

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)


    return web.Response(
        content_type='application/json',
        text=json.dumps({
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        }))


if __name__ == '__main__':

    if vosk_cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(vosk_cert_file, vosk_key_file)
    else:
        ssl_context = None

    app = web.Application()
    app.router.add_post('/offer', offer)

    app.router.add_get('/', index)
    app.router.add_static('/static/', path=ROOT / 'static', name='static')

    web.run_app(app, port=vosk_port, ssl_context=ssl_context)
