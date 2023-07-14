#!/usr/bin/python3

import anyio
import asyncari
import logging
import aioudp

import os
ast_host = os.getenv("AST_HOST", '127.0.0.1')
ast_port = int(os.getenv("AST_ARI_PORT", 8088))
ast_url = os.getenv("AST_URL", 'http://%s:%d/'%(ast_host,ast_port))
ast_username = os.getenv("AST_USER", 'asterisk')
ast_password = os.getenv("AST_PASS", 'asterisk')
ast_app = os.getenv("AST_APP", 'hello-world')

import vosk

model = vosk.Model(lang='en-us')
recognizer = vosk.KaldiRecognizer(model, 16000)

import array

async def rtp_handler(connection):
    async for message in connection:
        data = array.array('h', message[12:])
        data.byteswap()
        if recognizer.AcceptWaveform(data.tobytes()):
               print (recognizer.Result())
        else:
               print (recognizer.PartialResult())

async def statis_handler(objs, ev, client):
    channel = objs['channel']
    channel.answer()
    if 'UnicastRTP' in channel.name:
         return

    bridge = await client.bridges.create(type='mixing')

    media_id = client.generate_id()
    await client.channels.externalMedia(channelId=media_id, app=client._app, external_host='localhost:45000', format='slin16')

    await bridge.addChannel(channel=[media_id, channel.id])


async def main():
     async with asyncari.connect(ast_url, ast_app, ast_username,ast_password) as client:
        async with aioudp.serve("localhost", 45000, rtp_handler) as udpserv:
             async with client.on_channel_event('StasisStart') as listener:
                 async for objs, event in listener:
                      await statis_handler(objs, event, client)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    anyio.run(main)
