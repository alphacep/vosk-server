#!/usr/bin/env python3
#
# Copyright 2020 Alpha Cephei Inc
# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the gRPC route guide server."""

from concurrent import futures
import time
import math
import logging
import json
import grpc

import stt_service_pb2
import stt_service_pb2_grpc
from google.protobuf import duration_pb2

from vosk import Model, KaldiRecognizer

class SttServiceServicer(stt_service_pb2_grpc.SttServiceServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self):
        self.model = Model("model")

    def get_duration(self, x):
        seconds = int(x)
        nanos = (int (x * 1000) % 1000) * 1000000;
        return duration_pb2.Duration(seconds = seconds, nanos=nanos)

    def get_word_info(self, x):
        return stt_service_pb2.WordInfo(start_time=self.get_duration(x['start']),
                                        end_time=self.get_duration(x['end']),
                                        word=x['word'], confidence=x['conf'])

    def get_response(self, json_res):
        res = json.loads(json_res)
        print(res)
        if 'partial' in res:
             alternatives = [stt_service_pb2.SpeechRecognitionAlternative(text=res['partial'])]
             chunks = [stt_service_pb2.SpeechRecognitionChunk(alternatives=alternatives, final=False)]
             return stt_service_pb2.StreamingRecognitionResponse(chunks=chunks)
        else:
             words = [self.get_word_info(x) for x in res['result']]
             alternatives = [stt_service_pb2.SpeechRecognitionAlternative(text=res['text'], words=words)]
             chunks = [stt_service_pb2.SpeechRecognitionChunk(alternatives=alternatives, final=True)]
             return stt_service_pb2.StreamingRecognitionResponse(chunks=chunks)

    def StreamingRecognize(self, request_iterator, context):
        request = next(request_iterator)
        partial = request.config.specification.partial_results
        recognizer = KaldiRecognizer(self.model, request.config.specification.sample_rate_hertz)
        for request in request_iterator:
            res = recognizer.AcceptWaveform(request.audio_content)
            if res:
                yield self.get_response(recognizer.Result())
            elif partial:
                yield self.get_response(recognizer.PartialResult())
        yield self.get_response(recognizer.FinalResult())

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stt_service_pb2_grpc.add_SttServiceServicer_to_server(
        SttServiceServicer(), server)
    server.add_insecure_port('[::]:5001')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
