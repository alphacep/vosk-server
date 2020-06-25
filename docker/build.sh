#!/bin/bash

set -e
set -x

for kind in vosk-server ru en de cn fr grpc-en ; do
    docker build --file Dockerfile.kaldi-${kind} --tag alphacep/kaldi-${kind}:latest .
done

for kind in vosk-server ru en de cn fr grpc-en ; do
    docker push alphacep/kaldi-${kind}:latest
done
