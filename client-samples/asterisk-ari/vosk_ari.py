#!/usr/bin/python3

import anyio
import asyncari
import logging
import aioudp
import os
import vosk
import array

ast_host = os.getenv("AST_HOST", '127.0.0.1')
ast_port = int(os.getenv("AST_ARI_PORT", 8088))
ast_url = os.getenv("AST_URL", 'http://%s:%d/'%(ast_host,ast_port))
ast_username = os.getenv("AST_USER", 'asterisk')
ast_password = os.getenv("AST_PASS", 'asterisk')
ast_app = os.getenv("AST_APP", 'hello-world')


model = vosk.Model(lang='en-us')
channels = {}

class Channel:

    async def rtp_handler(self, connection):
        async for message in connection:
            data = array.array('h', message[12:])
            data.byteswap()
            if self.rec.AcceptWaveform(data.tobytes()):
                res = self.rec.Result()
            else:
                res = self.rec.PartialResult()
            print(res)

    async def init(self, client, channel):
        self.port = 45000 + len(channels)
        self.rec = vosk.KaldiRecognizer(model, 16000)
        self.udp = aioudp.serve("127.0.0.1", self.port, self.rtp_handler)
        await self.udp.__aenter__()

        bridge = await client.bridges.create(type='mixing')
        media_id = client.generate_id()
        await client.channels.externalMedia(channelId=media_id, app=client._app, external_host='127.0.0.1:' + str(self.port), format='slin16')
        await bridge.addChannel(channel=[media_id, channel.id])

async def statis_handler(objs, ev, client):
    channel = objs['channel']
    channel.answer()
    if 'UnicastRTP' in channel.name:
         return

    local_channel = Channel()
    await local_channel.init(client, channel)
    channels[channel.id] = local_channel

async def main():
     async with asyncari.connect(ast_url, ast_app, ast_username,ast_password) as client:
         async with client.on_channel_event('StasisStart') as listener:
             async for objs, event in listener:
                  await statis_handler(objs, event, client)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    anyio.run(main)
