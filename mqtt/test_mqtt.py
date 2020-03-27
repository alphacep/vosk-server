#!/usr/bin/env python3

from os import environ
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

class VoskMqttServerTest():
    def __init__(self):
        self.pid = environ.get('PID')
        self.mqtt_address = environ.get('MQTT_ADDRESS')
        self.mqtt_username = environ.get('MQTT_USERNAME')
        self.mqtt_password = environ.get('MQTT_PASSWORD')
        self.test_file_name = environ.get('TEST_FILE_NAME')
        self.__init_mqtt_client()

    def run(self):
        self.client.connect(self.mqtt_address)
        self.client.loop_forever()

    def __on_mqtt_connect(self, client, obj, flags, rc):
        print('Connected to mqtt server')
        test_file = open(str(self.test_file_name), 'rb')

        while True:
            data = test_file.read(1024)

            if len(data) == 0:
                print('Disconnecting...')
                self.client.disconnect()
                break

            self.client.publish(self.pid + '/stream/voice', data)

    def __init_mqtt_client(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
        self.client.on_connect = self.__on_mqtt_connect


if __name__ == "__main__":
    server = VoskMqttServerTest()
    server.run()
