KALDI_ROOT ?= $(HOME)/kaldi

CXX := g++

ATLAS_ROOT ?= /usr
ATLASLIBS := $(ATLAS_ROOT)/lib/libatlas.so.3 $(ATLAS_ROOT)/lib/libf77blas.so.3 $(ATLAS_ROOT)/lib/libcblas.so.3 $(ATLAS_ROOT)/lib/liblapack_atlas.so.3

KALDI_FLAGS := \
	-DKALDI_DOUBLEPRECISION=0 -DHAVE_POSIX_MEMALIGN \
	-Wno-sign-compare -Wno-unused-local-typedefs -Winit-self \
	-DHAVE_EXECINFO_H=1 -rdynamic -DHAVE_CXXABI_H -DHAVE_ATLAS \
	-I$(ATLAS_ROOT)/include \
	-I$(KALDI_ROOT)/tools/openfst/include -I$(KALDI_ROOT)/src

CXXFLAGS := -std=c++11 -g -Wall -DPIC -fPIC $(KALDI_FLAGS) `python3-config --includes`

KALDI_LIBS = \
	-rdynamic \
	$(KALDI_ROOT)/src/online2/kaldi-online2.a \
	$(KALDI_ROOT)/src/decoder/kaldi-decoder.a \
	$(KALDI_ROOT)/src/ivector/kaldi-ivector.a \
	$(KALDI_ROOT)/src/gmm/kaldi-gmm.a \
	$(KALDI_ROOT)/src/nnet3/kaldi-nnet3.a \
	$(KALDI_ROOT)/src/tree/kaldi-tree.a \
	$(KALDI_ROOT)/src/feat/kaldi-feat.a \
	$(KALDI_ROOT)/src/lat/kaldi-lat.a \
	$(KALDI_ROOT)/src/hmm/kaldi-hmm.a \
	$(KALDI_ROOT)/src/transform/kaldi-transform.a \
	$(KALDI_ROOT)/src/cudamatrix/kaldi-cudamatrix.a \
	$(KALDI_ROOT)/src/matrix/kaldi-matrix.a \
	$(KALDI_ROOT)/src/fstext/kaldi-fstext.a \
	$(KALDI_ROOT)/src/util/kaldi-util.a \
	$(KALDI_ROOT)/src/base/kaldi-base.a \
	$(KALDI_ROOT)/tools/openfst/lib/libfst.a \
	$(ATLASLIBS) \
	-lm -lpthread

all: _kaldi_recognizer.so

_kaldi_recognizer.so: kaldi_recognizer_wrap.cc kaldi_recognizer.cc model.cc
	$(CXX) $(CXXFLAGS) -shared -o $@ kaldi_recognizer.cc model.cc kaldi_recognizer_wrap.cc $(KALDI_LIBS)

kaldi_recognizer_wrap.cc: kaldi_recognizer.i
	swig -threads -python -c++ -o kaldi_recognizer_wrap.cc kaldi_recognizer.i

clean:
	$(RM) *.so kaldi_recognizer_wrap.cc *.o *.pyc kaldi_recognizer.py
