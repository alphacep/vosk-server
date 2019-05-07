%module kaldi_websocket

%include <typemaps.i>
%include <std_string.i>
%include <pybuffer.i>

namespace kaldi {
}

%pybuffer_binary(const char *data, int len)

%{
#include "kaldi_recognizer.h"
#include "model.h"
%}

%include "kaldi_recognizer.h"
%include "model.h"

