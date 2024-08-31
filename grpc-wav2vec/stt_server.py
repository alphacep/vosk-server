#!/usr/bin/env python3
#
# Copyright 2024 Alpha Cephei Inc
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
import os
import sys
import time
import math
import logging
import json
import grpc
import time
import numpy as np
import torch
import torchaudio

import stt_service_pb2
import stt_service_pb2_grpc
from google.protobuf import duration_pb2

from vosk import Model, KaldiRecognizer

from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, Wav2Vec2ProcessorWithLM
from pyctcdecode import build_ctcdecoder

# Uncomment for better memory usage
# import gc
# gc.set_threshold(0)

vosk_interface = os.environ.get('VOSK_SERVER_INTERFACE', '0.0.0.0')
vosk_port = int(os.environ.get('VOSK_SERVER_PORT', 5001))
vosk_model_path = os.environ.get('VOSK_MODEL_PATH', 'model')
vosk_sample_rate = float(os.environ.get('VOSK_SAMPLE_RATE', 16000))

if len(sys.argv) > 1:
   vosk_model_path = sys.argv[1]

import threading
import queue
import time
import uuid

qmutex = threading.Lock()
in_queues = {}
out_queues = {}



def Worker():

    model_id = "mms-model/mms-1b-fl102"
    processor = Wav2Vec2Processor.from_pretrained(model_id)
    model = Wav2Vec2ForCTC.from_pretrained(model_id)
    processor.tokenizer.set_target_lang("eng")
    model.load_adapter("eng")

    vocab_dict = processor.tokenizer.get_vocab()
    sorted_vocab_dict = {k.lower(): v for k, v in sorted(vocab_dict.items(), key=lambda item: item[1])}
    print(sorted_vocab_dict)
    unigrams = [x.strip() for x in open("mms-model/lms/en/en.vocab").readlines()]
    decoder = build_ctcdecoder(
        labels=list(sorted_vocab_dict.keys()),
        kenlm_model_path="mms-model/lms/en/en.kenlm",
        unigrams=unigrams,
    )

    processor_with_lm = Wav2Vec2ProcessorWithLM(
        feature_extractor=processor.feature_extractor,
        tokenizer=processor.tokenizer,
        decoder=decoder
    )

    while True:
        inputs_list = []
        keys_list = []
        with qmutex:
            for key, q in in_queues.items():
                print (key, q.empty())
                if q.empty():
                    continue
                data = q.get_nowait()
                inputs = processor(data, sampling_rate=16_000, return_tensors="pt").input_values
                inputs_list.append(inputs)
                keys_list.append(key)
                q.task_done()

        if len(inputs_list) == 0:
            time.sleep(0.1)
            continue

        print (f"Processing batch of {len(inputs_list)} chunks")
        inputs = torch.cat(inputs_list, dim=0)
        with torch.no_grad():
            logits = model(inputs).logits
            all_transcripts = processor_with_lm.batch_decode(logits.cpu().numpy()).text
            for key, transcription in zip(keys_list, all_transcripts):
                out_queues[key].put(transcription)

class Stats:
    def __init__(self):
        self.n_streams = 0
        self.n_total_streams = 0
        self.max_chunk_rtf = 0
        self.max_stream_rtf = 0

stats = Stats()

class SttServiceServicer(stt_service_pb2_grpc.SttServiceServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self):
        self.model = Model(vosk_model_path)

    def get_partial_response(self):
        alternatives = [stt_service_pb2.SpeechRecognitionAlternative(text='')]
        chunks = [stt_service_pb2.SpeechRecognitionChunk(alternatives=alternatives, final=False)]
        return stt_service_pb2.StreamingRecognitionResponse(chunks=chunks)

    def get_response(self, uid, data, sampling_rate):
        speech_array = torch.frombuffer(np.array(data, copy=True), dtype=torch.int16).float()
        resampler = torchaudio.transforms.Resample(sampling_rate, 16_000)
        sound = resampler(speech_array).squeeze()
        in_queues[uid].put(sound)
        print ("Added to ", uid)
        transcription = out_queues[uid].get()
        out_queues[uid].task_done() 
        alternatives = [stt_service_pb2.SpeechRecognitionAlternative(text=transcription)]
        chunks = [stt_service_pb2.SpeechRecognitionChunk(alternatives=alternatives, final=True)]
        return stt_service_pb2.StreamingRecognitionResponse(chunks=chunks)

    def StreamingRecognize(self, request_iterator, context):

        uid = uuid.uuid4()
        with qmutex:
            in_queues[uid] = queue.Queue()
            out_queues[uid] = queue.Queue()

        request = next(request_iterator)
        partial = request.config.specification.partial_results
        sample_rate = request.config.specification.sample_rate_hertz
        recognizer = KaldiRecognizer(self.model, sample_rate)
        recognizer.SetMaxAlternatives(request.config.specification.max_alternatives)
        recognizer.SetWords(request.config.specification.enable_word_time_offsets)

        start_time = time.time()
        processed_bytes = 0
        max_chunk_rtf = 0
        stats.n_streams = stats.n_streams + 1
        stats.n_total_streams = stats.n_total_streams + 1
        audiobuf = []

        for request in request_iterator:

            start_chunk_time = time.time()
            chunk_processed_bytes = len(request.audio_content)
            processed_bytes += chunk_processed_bytes

            res = recognizer.AcceptWaveform(request.audio_content)
            audiobuf.append(request.audio_content)

            chunk_time = time.time() - start_chunk_time
            max_chunk_rtf = max(max_chunk_rtf, chunk_time / (chunk_processed_bytes / (2 * sample_rate)))

            if res:
                recognizer.Result()
                data = b''.join(audiobuf)
                audiobuf = []
                yield self.get_response(uid, data, sample_rate)
            elif partial:
                yield self.get_partial_response()

        data = b''.join(audiobuf)
        audiobuf = []
        yield self.get_response(uid, data, sample_rate)

        execution_time = time.time() - start_time
        audio_time = processed_bytes / (2 * sample_rate)
        rtf = execution_time / audio_time
        stats.max_stream_rtf = max(stats.max_stream_rtf, rtf)
        stats.max_chunk_rtf = max(stats.max_chunk_rtf, max_chunk_rtf)

        stats.n_streams = stats.n_streams - 1
        with qmutex:
            del in_queues[uid]
            del out_queues[uid]


class StatsServiceServicer(stt_service_pb2_grpc.StatsServiceServicer):

    def GetStats(self, reqest, context):

        return stt_service_pb2.StatsResponse(n_streams=stats.n_streams,
                n_total_streams=stats.n_total_streams,
                max_stream_rtf = stats.max_stream_rtf,
                max_chunk_rtf = stats.max_chunk_rtf)

def serve():
    pool_server = futures.ThreadPoolExecutor(8)
    server = grpc.server(pool_server)
    stt_service_pb2_grpc.add_SttServiceServicer_to_server(SttServiceServicer(), server)
    stt_service_pb2_grpc.add_StatsServiceServicer_to_server(StatsServiceServicer(), server)

    threading.Thread(target=Worker).start()    

    server.add_insecure_port('{}:{}'.format(vosk_interface, vosk_port))
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
