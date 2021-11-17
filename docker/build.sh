#!/bin/bash

set -e
set -x

docker build --no-cache --build-arg KALDI_MKL=0 --file Dockerfile.kaldi-vosk-server --tag alphacep/kaldi-vosk-server:latest .

for kind in ru en de cn fr es en-in grpc-en en-spk; do
    docker build --file Dockerfile.kaldi-${kind} --tag alphacep/kaldi-${kind}:latest .
done

for kind in vosk-server ru en de cn fr es en-in grpc-en en-spk; do
    docker push alphacep/kaldi-${kind}:latest
done
