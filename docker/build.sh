#!/bin/bash

set -e
set -x

docker build --squash --file Dockerfile.kaldi-ru --tag alphacep/kaldi-ru:latest .
