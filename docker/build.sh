#!/bin/bash

set -e
set -x

docker build --file Dockerfile.kaldi-ru --tag alphacep/kaldi-ru:latest .
