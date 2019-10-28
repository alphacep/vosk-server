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

RUN git clone --depth 1 https://github.com/kaldi-asr/kaldi.git /opt/kaldi && \
    cd /opt/kaldi && \
    cd /opt/kaldi/tools && \
    make -j $(nproc) && \
    cd /opt/kaldi/src && \
    ./configure --mathlib=ATLAS --shared && \
    make depend -j $(nproc) && \
    make -j $(nproc) online2 && \
    find /opt/kaldi -name "*.o" | xargs rm

RUN mkdir /opt/kaldi-websocket \
   && cd /opt/kaldi-websocket \
   && git clone https://github.com/alphacep/kaldi-websocket-python \
   && cd kaldi-websocket-python \
   && KALDI_ROOT=/opt/kaldi make \
   && cd /opt/kaldi/src \
   && make clean

ENV MODEL_VERSION 0.1
RUN mkdir /opt/kaldi-en \
   && cd /opt/kaldi-en \
   && wget http://alphacephei.com/kaldi/kaldi-en-us-aspire-${MODEL_VERSION}.tar.gz \
   && tar xf kaldi-en-us-aspire-${MODEL_VERSION}.tar.gz \
   && mv kaldi-en-us-aspire-${MODEL_VERSION} model \
   && rm -rf kaldi-en-us-aspire-${MODEL_VERSION}.tar.gz

EXPOSE 2700
WORKDIR /opt/kaldi-websocket/kaldi-websocket-python
CMD [ "python3", "./asr_server.py", "/opt/kaldi-en/model" ]
