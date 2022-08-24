FROM alphacep/kaldi-vosk-server:latest

ENV MODEL_VERSION 0.42
RUN mkdir /opt/vosk-model-es \
   && cd /opt/vosk-model-es \
   && wget -q https://alphacephei.com/vosk/models/vosk-model-es-${MODEL_VERSION}.zip \
   && unzip vosk-model-es-${MODEL_VERSION}.zip \
   && mv vosk-model-es-${MODEL_VERSION} model \
   && rm -rf vosk-model-es-${MODEL_VERSION}.zip

EXPOSE 2700
WORKDIR /opt/vosk-server/websocket
CMD [ "python3", "./asr_server.py", "/opt/vosk-model-es/model" ]
