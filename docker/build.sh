#!/bin/bash

set -e
set -x

docker build --squash --file Dockerfile.kaldi-vosk-server --tag alphacep/kaldi-vosk-server:latest .
for lang in ru en de cn; do
    docker build --squash --file Dockerfile.kaldi-${lang} --tag alphacep/kaldi-${lang}:latest .
done
