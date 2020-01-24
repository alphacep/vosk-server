ARG BASE_IMAGE=alphacep/kaldi-vosk-server:latest

###

FROM alpine AS build

WORKDIR /opt/kaldi-model

RUN apk add -U wget tar
RUN set -o pipefail \
   && mkdir temp \
   && wget -q -O - https://alphacephei.com/kaldi/kaldi-ru-0.6.tar.gz \
   | tar xz --strip-components=1 -C temp \
   && mv temp/exp/tdnn/ivector_extractor ivector \
   && mv temp/exp/tdnn/conf/mfcc.conf . \
   && mv temp/exp/tdnn/conf/splice.conf ivector \
   && mv temp/exp/tdnn/graph/HCLG.fst . \
   && mv temp/exp/tdnn/graph/words.txt . \
   && mv temp/data/lang_test_rescore/phones/word_boundary.int . \
   && mv temp/exp/tdnn/final.mdl . \
   && rm -rf temp

###

FROM $BASE_IMAGE
COPY --from=build /opt/kaldi-model /opt/kaldi-model
CMD ["/opt/kaldi-model"]
