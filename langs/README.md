Final Docker images, each containing the Websocket server and the language model.

We are building an intermediate image for each language containing only the architecture-independent data files.
Docker caching of these intermediate stages means that we avoid needlessly downloading the same large file several times.

The model is placed into `/opt/kaldi-model`. See `model.cc` to grok which files are required:

```
final.mdl
HCLG.fst
ivector/final.dubm
ivector/final.ie
ivector/final.mat
ivector/global_cmvn.stats
ivector/online_cmvn.conf
ivector/splice.conf
mfcc.conf
word_boundary.int
words.txt
```
