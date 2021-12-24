#!/bin/bash

set -e
set -x

docker build --no-cache --build-arg KALDI_MKL=0 --file Dockerfile.kaldi-vosk-server-gpu --tag alphacep/kaldi-vosk-server-gpu:latest .
docker build --no-cache --file Dockerfile.kaldi-en-gpu --tag alphacep/kaldi-en-gpu:latest .
