A very simple websocket server based on Kaldi

Requires Kaldi at least #6c816 which contain critical fixes

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
./test.py test.wav
```

You can try with any wav file which has proper format - 8khz 16bit mono PCM.
Other formats has to be converted before decoding.

## Other programming languages

Check other examples (Asterisk-EAGI, php, node, c#) in client-samples folder in this repository.
