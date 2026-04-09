#!/bin/bash

set -e
set -x

docker buildx build --platform linux/amd64,linux/arm64 --no-cache --build-arg KALDI_MKL=0 --file Dockerfile.kaldi-vosk-server --tag alphacep/kaldi-vosk-server:latest --push .

for kind in ru en de cn fr es en-in grpc-en en-spk ja hi; do
    docker buildx build --platform linux/amd64,linux/arm64 --file Dockerfile.kaldi-${kind} --tag alphacep/kaldi-${kind}:latest --push .
done
