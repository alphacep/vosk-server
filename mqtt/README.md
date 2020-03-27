## Vosk ASR via MQTT

A simple MQTT-based ASR server that might be useful to accept voice data from devices like [Matrix Voice](https://www.matrix.one/products/voice).    

### Usage

#### Prerequisites
- Install any MQTT broker on your RPi, e.g [Mosquitto](https://mosquitto.org/).
- Install `Git`.
- Install `python` >= 3.4 and `pip` >= 19.0.
- Install vosk: `pip3 install vosk`.

#### Project Setup
```shell script
# Download vosk-server
git clone https://github.com/alphacep/vosk-server.git
cd ./vosk-server/mqtt

# Prepare any lightweight model: https://github.com/alphacep/vosk-api/blob/master/doc/models.md
wget http://alphacephei.com/kaldi/alphacep-model-android-ru-0.3.tar.gz
tar xf alphacep-model-android-ru-0.3.tar.gz
mv alphacep-model-android-ru-0.3 ./model

# Configure environment
nano .env
```

Add the following environment variables (modify values for your needs):
```shell script
PID=any_project_id
VOSK_LANG=ru
VOSK_SAMPLE_RATE=16000.0
MQTT_ADDRESS=broker_ip
MQTT_USERNAME=username
MQTT_PASSWORD=password
TEST_FILE_NAME=test.wav
```

#### Execution
- Start ASR server: `./asr_server_mqtt.py`
- Run a test script: `./test_mqtt.py`

If you can't run these scripts, please grant them execution permissions:

```shell script
sudo chmod +x ./asr_server_mqtt.py
sudo chmod +x ./test_mqtt.py
```

Note that `test.wav` is recorded in Russian.
If you want to test some other model, please record a 16kHz / 16bit mono wav file.
Then put it into `./mqtt` root and change `TEST_FILE_NAME` env variable.
You should also download a new language model as it was described above.

#### Logs

When you start ASR server, you'll see the following output:

```shell script
vosk --min-active=200 --max-active=3000 --beam=10.0 --lattice-beam=2.0 --acoustic-scale=1.0 --frame-subsampling-factor=3 --endpoint.silence-phones=1:2:3:4:5:6:7:8:9:10 --endpoint.rule2.min-trailing-silence=0.5 --endpoint.rule3.min-trailing-silence=1.0 --endpoint.rule4.min-trailing-silence=2.0
LOG (vosk[5.5.641~2-79319]:ComputeDerivedVars():ivector-extractor.cc:183) Computing derived variables for iVector extractor
LOG (vosk[5.5.641~2-79319]:ComputeDerivedVars():ivector-extractor.cc:204) Done.
LOG (vosk[5.5.641~2-79319]:RemoveOrphanNodes():nnet-nnet.cc:948) Removed 1 orphan nodes.
LOG (vosk[5.5.641~2-79319]:RemoveOrphanComponents():nnet-nnet.cc:847) Removing 2 orphan components.
LOG (vosk[5.5.641~2-79319]:Collapse():nnet-utils.cc:1472) Added 1 components, removed 2
LOG (vosk[5.5.641~2-79319]:CompileLooped():nnet-compile-looped.cc:345) Spent 0.3428 seconds in looped compilation.
Connected to mqtt server
```

It means `KaldiRecognizer` and MQTT server are configured and ready for receiving audio stream.

When you start a test script, it'll literally do nothing but read a test recording and send chunks to ASR server via MQTT.
A test script will automatically close connection when the file is fully read and sent to the server.

```shell script
Connected to mqtt server
Disconnecting...
```

However, after a short delay you should also see a set of final transcripts on the server-side:
```shell script
{'result': [{'conf': 1.0, 'end': 2.97, 'start': 2.16, 'word': 'включи'}, {'conf': 1.0, 'end': 3.69, 'start': 3.09, 'word': 'свет'}], 'text': 'включи свет'}
{'result': [{'conf': 0.999962, 'end': 5.97, 'start': 5.31, 'word': 'выключил'}, {'conf': 1.0, 'end': 6.48, 'start': 6.000001, 'word': 'свет'}], 'text': 'выключил свет'}
{'result': [{'conf': 0.948885, 'end': 8.58, 'start': 8.01, 'word': 'включи'}, {'conf': 1.0, 'end': 9.39, 'start': 8.61, 'word': 'телевизор'}], 'text': 'включи телевизор'}
{'result': [{'conf': 0.719489, 'end': 11.4, 'start': 10.77, 'word': 'выключи'}, {'conf': 1.0, 'end': 12.09, 'start': 11.408416, 'word': 'телевизор'}], 'text': 'выключи телевизор'}
{'result': [{'conf': 0.991423, 'end': 14.19, 'start': 13.62, 'word': 'включил'}, {'conf': 1.0, 'end': 15.09, 'start': 14.22, 'word': 'кондиционер'}], 'text': 'включил кондиционер'}
{'result': [{'conf': 0.999582, 'end': 17.219995, 'start': 16.53, 'word': 'выключая'}, {'conf': 1.0, 'end': 17.97, 'start': 17.219995, 'word': 'кондиционер'}], 'text': 'выключая кондиционер'}
{'result': [{'conf': 1.0, 'end': 19.83, 'start': 19.41, 'word': 'какая'}, {'conf': 1.0, 'end': 20.34, 'start': 19.83, 'word': 'сегодня'}, {'conf': 1.0, 'end': 20.94, 'start': 20.34, 'word': 'погода'}], 'text': 'какая сегодня погода'}
```

#### Model Switching

If you want to switch from Russian to any other model, you can do it without restarting a server.
Just publish the following message to your MQTT broker:

```shell script
mosquitto_pub -h [MQTT_ADDRESS] -u [MQTT_USERNAME] -P [MQTT_PASSWORD] -t [PID]/lang -m [VOSK_LANG]
```

Note that you have to download, unpack and put the required model to `./mqtt/model-[VOSK_LANG]` first.
