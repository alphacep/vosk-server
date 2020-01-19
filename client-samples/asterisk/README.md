# Using kaldi-websocket-python server with Asterisk

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

alternatively, you can run https://github.com/alphacep/kaldi-websocket-python with your models.

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

For more advanced chatbot, database interoperation and other callflow adjustments modify eagi.py according to your needs.
You can also use PHP/Perl, see other examples in this package.
