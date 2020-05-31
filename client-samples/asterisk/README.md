## Asterisk Plugin

Plugin for Asterisk is avialable in a separate project:

https://github.com/alphacep/vosk-asterisk

We decided to provide asterisk modules to make integration really easy,
you can just have dialplan like this:

```
[internal]
exten = 1,1,Answer
same = n,Wait(1)
same = n,SpeechCreate
same = n,SpeechBackground(hello)
same = n,Verbose(0,Result was ${SPEECH_TEXT(0)})
```

## EAGI

It is also possible to forward audio to AMI/ARI/AGI and process audio
from the separate web appication, but in a long term you'll have to
recreate all asterisk on Statis by yourself, so we don't consider
it as a relevant way to impelment voice interface.

In a long term, the best way to implement user input with the natural user
experience is asynchronous process. And asynchronous input processing
requires something more complicated than current asterisk speech API. We
might implement more complex modules for speech  processing in asterisk
in the future.

Still, you can find the code todemo EAGI here in eagi.py file, to use it:

### Install dependencies

 - asterisk
 - docker
 - TTS packages:

        sudo apt install sox espeak

 - AGI and websocket package

        sudo pip3 install pyst2 websocket-client

### Start recognition server with docker

```
docker run -d -p 2700:2700 alphacep/kaldi-en:latest
```

alternatively, you can run https://github.com/alphacep/vosk-server with your models.

### Test EAGI script

Script [eagi.py](https://github.com/alphacep/api-samples/blob/master/asterisk/eagi.py) is located here:

```
cd /home/user
git clone https://github.com/alphacep/api-samples
cd api-samples/asterisk
python3 eagi.py
ARGS: ['eagi.py']
^C
```

### Configure dialplan for Asterisk

В etc/extensions.conf

```
exten => 200,1,Answer()
same = n,EAGI(/home/user/api-samples/asterisk/eagi.py)
same = n,Hangup()
```

### Call and check you get the response

For more advanced chatbot, database interoperation and other callflow
adjustments modify eagi.py according to your needs. You can also use
PHP/Perl, see other examples in this package.
