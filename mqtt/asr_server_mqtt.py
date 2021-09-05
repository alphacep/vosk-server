#!/usr/bin/env python3

from os import environ
import json
import paho.mqtt.client as mqtt
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv

load_dotenv()

class VoskMqttServer():
    def __init__(self):
        self.pid = environ.get('PID')
        self.mqtt_address = environ.get('MQTT_ADDRESS')
        self.mqtt_username = environ.get('MQTT_USERNAME')
        self.mqtt_password = environ.get('MQTT_PASSWORD')
        self.vosk_lang = environ.get('VOSK_LANG')
        self.sample_rate = float(environ.get('VOSK_SAMPLE_RATE'))

        self.__init_kaldi_recognizer(self.__get_model_path(self.vosk_lang))
        self.__init_mqtt_client()

    def run(self):
        self.client.connect(self.mqtt_address)
        self.client.loop_forever()

    def __on_mqtt_connect(self, client, obj, flags, rc):
        print('Connected to mqtt server')
        self.client.subscribe(self.pid + '/lang')
        self.client.subscribe(self.pid + '/stream/voice')
        self.client.subscribe(self.pid + '/stop')

    def __on_mqtt_message(self, client, obj, msg):

        if msg.topic.endswith('/lang'):
            self.__init_kaldi_recognizer(self.__get_model_path(msg.payload.decode('utf-8')))

        elif msg.topic.endswith('/stop'):
            transcribe = self.recognizer.FinalResult()
            data = json.loads(transcribe)
            print(data)
            if data and data['text']:
                self.client.publish(self.pid + '/finalTranscribe', str(data))
            print('Disconnecting...')
            self.client.disconnect()

        elif msg.topic.endswith('/voice'):
            if self.recognizer.AcceptWaveform(msg.payload):
                transcribe = self.recognizer.Result()
                data = json.loads(transcribe)
                print(data)
                if data and data['text']:
                    self.client.publish(self.pid + '/finalTranscribe', str(data))

    def __get_model_path(self, lang='ru'):
        return 'model-' + lang

    def __init_kaldi_recognizer(self, model_path='model-ru'):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)

    def __init_mqtt_client(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        self.client.on_connect = self.__on_mqtt_connect
        self.client.on_message = self.__on_mqtt_message


if __name__ == "__main__":
    server = VoskMqttServer()
    server.run()
