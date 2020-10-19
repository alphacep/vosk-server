#!/bin/bash

set -e
set -x

docker build --build-arg KALDI_MKL=0 --file Dockerfile.vosk-unimrcp --tag alphacep/vosk-unimrcp:latest .

# Run like this:
#
# docker run  -p 1544:1544 -p 8060:8060 -p 5001-5200:5001-5200 alphacep/vosk-unimrcp
#
# then test with umc, given you configured ip address in client
