A very simple server based on [Vosk-API](https://github.com/alphacep/vosk-api).

There are three implementations for different protocol - websocket, grpc, mqtt.

## Usage

Start the server

```
docker run -d -p 2700:2700 alphacep/kaldi-en:latest
```

or for Chinese. The model is based on Kaldi multi-cn recipe, thanks to [Xingyu Na](https://github.com/naxingyu).

```
docker run -d -p 2700:2700 alphacep/kaldi-cn:latest
```

or for Russian

```
docker run -d -p 2700:2700 alphacep/kaldi-ru:latest
```

or for German (model from https://github.com/uhh-lt/kaldi-tuda-de#pretrained-models)

```
docker run -d -p 2700:2700 alphacep/kaldi-de:latest
```

Run

```
git clone https://github.com/alphacep/vosk-server
cd vosk-server/websocket
./test.py test.wav
```

You can try with any wav file which has proper format - 8khz 16bit mono PCM.
Other formats has to be converted before decoding.

## Testing with microphone

You would need to install the pyaudio pip package:

```
pip install pyaudio
```

(on Windows, it's easiest to install the wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)).


To test with a microphone, run

```
./test_microphone.py localhost:2700

Connected to ws://localhost:2700
Type Ctrl-C to exit
{"partial" : ""}
{"partial" : "поднимите мне веки"}
{"partial" : "поднимите мне веки"}
{"result" : [ {"word": "поднимите", "start" : 3.45, "end" : 4.26, "conf" : 1},
{"word": "мне", "start" : 4.26, "end" : 4.47, "conf" : 1},
{"word": "веки", "start" : 4.47, "end" : 5.07, "conf" : 1}
 ], "text" : "поднимите мне веки" }
{"partial" : ""}
Closing PyAudio Stream
Terminating PyAudio object
Terminating connection
{"result" : [  ], "text" : "" }
Bye
```

## Other programming languages

Check other examples (Asterisk-EAGI, php, java, node, c#) in client-samples folder in this repository.
