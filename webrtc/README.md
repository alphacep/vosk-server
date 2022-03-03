# webrtc vosk-server

## Setup environment and run it.

### Set model path

Setup path to ./model
The models can be download from here https://alphacephei.com/vosk/models

### Python environment

The sample can work in python 3.8

```sh
$ python3 -m pip install aiortc aiohttp aiorpc vosk
```

If your system fails installing aiortc, please install gcc in your environment and use pip to install aiortc again.

### Execution in local

Run the server:

```sh
$ python3 asr_server_webrtc.py
```

Now, open a web browser with URL http://localhost:2700/.

### Execution in LAN

To test the demo from another computer on the LAN, the web page must be served through HTTPS. This is because modern web browsers (such as Chrome, Firefox) don't allow access to the microphone unless the host is `localhost` or the page is served securely.

Thus, an SSL certificate is required to test the demo from other computers or smartphones. An untrusted self-signed certificate will work fine on most browsers (iOS Safari is the exception). You can use [mkcert](https://github.com/FiloSottile/mkcert) to make your own self-signed *cert* and *key* files.

```sh
$ export VOSK_CERT_FILE="/path/to/cert.pem"
$ export VOSK_KEY_FILE="/path/to/key.pem"
$ python3 asr_server_webrtc.py
```

Now, in the other computer, open a web browser with URL https://SERVER_IP:2700/, replacing `SERVER_IP` with the IP address of your Vosk server.

