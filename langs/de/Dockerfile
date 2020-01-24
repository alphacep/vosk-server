ARG BASE_IMAGE=alphacep/kaldi-vosk-server:latest

###
FROM alpine AS build

WORKDIR /opt/kaldi-model
RUN apk add -U wget tar

RUN set -o pipefail \
   && mkdir temp \
   && wget -q -O - https://ltdata1.informatik.uni-hamburg.de/kaldi_tuda_de/de_400k_nnet3chain_tdnn1f_2048_sp_bi.tar.bz2 \
   | tar xj --strip-components=1 -C temp \
   && mkdir ivector \
   && mv temp/HCLG.fst . \
   && mv temp/final.mdl . \
   && mv temp/words.txt . \
   && mv temp/conf/mfcc_hires.conf mfcc.conf \
   && mv temp/phones/word_boundary.int . \
   && mv temp/ivector_extractor/final.dubm ivector \
   && mv temp/ivector_extractor/final.ie ivector \
   && mv temp/ivector_extractor/final.mat ivector \
   && mv temp/ivector_extractor/global_cmvn.stats ivector \
   && mv temp/ivector_extractor/splice.conf ivector \
   && mv temp/ivector_extractor/online_cmvn.conf ivector \
   && rm -rf temp

###

FROM $BASE_IMAGE
COPY --from=build /opt/kaldi-model /opt/kaldi-model
CMD ["/opt/kaldi-model"]
