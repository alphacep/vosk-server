#!/bin/bash

set -e
set -x

#for kind in vosk-server ru en de cn vosk-server-en-atom vosk-server-fr-atom ; do
#    docker build --squash --file Dockerfile.kaldi-${kind} --tag alphacep/kaldi-${kind}:latest .
#done

for kind in vosk-server ru en de cn vosk-server-en-atom vosk-server-fr-atom ; do
    docker push alphacep/kaldi-${kind}:latest
done
