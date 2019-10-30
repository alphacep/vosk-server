A very simple websocket server based on Kaldi

Requires Kaldi at least #6c816 which contain critical fixes

## Usage

Start the server

```
docker run -d -p 2700:2700 alphacep/kaldi-en:latest
```

or for Chinese

```
docker run -d -p 2700:2700 alphacep/kaldi-cn:latest
```

or for Russian

```
docker run -d -p 2700:2700 alphacep/kaldi-ru:latest
```

Run

```
./test.py test.wav
```

You can try with any wav file which has proper format - 8khz 16bit mono PCM.
Other formats has to be converted before decoding.

## Other programming languages

See https://github.com/alphacep/api-samples
