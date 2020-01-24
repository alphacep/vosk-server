ARG BASE_IMAGE=alphacep/kaldi-vosk-server:latest

###
FROM alpine AS build

WORKDIR /opt/kaldi-model

RUN apk add -U wget tar
RUN set -o pipefail \
   && wget -q -O - https://alphacephei.com/kaldi/kaldi-en-us-aspire-0.1.tar.gz \
   | tar xz --strip-components=1

###

FROM $BASE_IMAGE
COPY --from=build /opt/kaldi-model /opt/kaldi-model
CMD ["/opt/kaldi-model"]
