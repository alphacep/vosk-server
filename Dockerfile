ARG BASE_IMAGE=debian:buster

FROM $BASE_IMAGE AS build

# for use with various balenalib images; see https://www.balena.io/docs/reference/base-images/base-images
# see https://github.com/balena-io-library/armv7hf-debian-qemu/issues/18
# for some reason, checking for the presence of cross-build-start doesn't work:
# RUN if [ -f /usr/bin/cross-build-start ]; then /usr/bin/cross-build-start; fi;
# $ docker build --build-arg BASE_IMAGE=balenalib/armv7hf-debian:buster .
# Step 3/21 : RUN if [ -f /usr/bin/cross-build-start ]; then /usr/bin/cross-build-start; fi;
# ---> Running in 2651a3d21ee2
# 2020/01/24 01:32:39 link /bin/sh.real /bin/sh: no such file or directory
# The command '/bin/sh -c if [ -f /usr/bin/cross-build-start ]; then /usr/bin/cross-build-start; fi;' returned a non-zero code: 1

RUN cross-build-start || true

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    g++ \
    make \
    automake \
    autoconf \
    bzip2 \
    unzip \
    wget \
    libtool \
    git \
    subversion \
    sox \
    python2.7 \
    python3 \
    python3-dev \
    python3-websockets \
    pkg-config \
    zlib1g-dev \
    patch \
    libatlas-base-dev \
    ca-certificates \
    swig \
    libatlas3-base && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/kaldi-asr/kaldi.git /opt/kaldi

RUN cd /opt/kaldi/tools \
    && sed -i 's:status=0:exit 0:g' extras/check_dependencies.sh \
    && sed -i 's:--enable-ngram-fsts:--enable-ngram-fsts --with-pic:g' Makefile \
    && make -j $(nproc) openfst cub

RUN mkdir /opt/kaldi/tools/atlas.ext \
    && cd /opt/kaldi/tools/atlas.ext \
    && ln -s $(dirname /usr/include/*/atlas) include \
    && ln -s $(dirname /usr/lib/*/atlas) lib

RUN cd /opt/kaldi/src \
    && ./configure --mathlib=ATLAS --atlas-root=/opt/kaldi/tools/atlas.ext --shared \
    && sed -i 's:-O0 -DKALDI_PARANOID:-O2 -DNDEBUG:g' kaldi.mk \
    && make -j $(nproc) online2

ADD . /opt/kaldi-websocket-python

RUN cd /opt/kaldi-websocket-python \
    && ATLAS_ROOT=/opt/kaldi/tools/atlas.ext KALDI_ROOT=/opt/kaldi make

RUN cd /opt/kaldi-websocket-python \
    && find -name '*.so' \
    | xargs ldd \
    | awk '{print $3}' \
    | xargs dpkg -S \
    | awk -F ':' '{print $1}' \
    | sort \
    | uniq \
    > apt-deps.txt

RUN cross-build-end || true

###

FROM $BASE_IMAGE

RUN cross-build-start || true

COPY --from=build /opt/kaldi-websocket-python /opt/kaldi-websocket-python

RUN apt-get update \
    && cat /opt/kaldi-websocket-python/apt-deps.txt \
    | xargs apt-get install -y --no-install-recommends \
    python3 \
    python3-websockets \
    && rm -rf /var/lib/apt/lists/*

RUN cross-build-end || true

EXPOSE 2700
WORKDIR /opt/kaldi-websocket-python
ENTRYPOINT [ "python3", "asr_server.py" ]
