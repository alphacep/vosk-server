FROM debian:9.8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
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
        libatlas-dev \
        ca-certificates \
        swig \
        libatlas3-base && \
    rm -rf /var/lib/apt/lists/*

RUN \
    git clone --depth 1 https://github.com/kaldi-asr/kaldi.git /opt/kaldi \
    && cd /opt/kaldi/tools \
    && sed -i 's:status=0:exit 0:g' extras/check_dependencies.sh \
    && sed -i 's:--enable-ngram-fsts:--enable-ngram-fsts --with-pic:g' Makefile \
    && make -j $(nproc) openfst cub \
    && cd /opt/kaldi/src \
    && ./configure --mathlib=ATLAS --shared \
    && make -j $(nproc) online2 \
    && git clone https://github.com/alphacep/kaldi-websocket-python /opt/kaldi-websocket-python \
    && cd /opt/kaldi-websocket-python \
    && KALDI_ROOT=/opt/kaldi make \
    && rm -rf /opt/kaldi
