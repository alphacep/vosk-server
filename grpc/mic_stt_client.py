#!/usr/bin/python3

import argparse
import grpc

import pyaudio
import sys

import stt_service_pb2
import stt_service_pb2_grpc

# config
CHUNK_SIZE = 4000
BUFFER_SIZE = 8000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = None
DEVICE_INDEX = None

p = pyaudio.PyAudio()


def list_devices():
    print("List of all devices detected by PyAudio (Index - Name) :")
    print("-------------------------------------------------------")
    for x in range(p.get_device_count()):
        info_dic = p.get_device_info_by_index(x)
        if info_dic['maxInputChannels'] > 0:
            print(str(x) + " - " + info_dic['name'])

def gen():
    specification = stt_service_pb2.RecognitionSpec(
        partial_results=True,
        audio_encoding='LINEAR16_PCM',
        sample_rate_hertz=16000
    )
    streaming_config = stt_service_pb2.RecognitionConfig(specification=specification)

    yield stt_service_pb2.StreamingRecognitionRequest(config=streaming_config)

    stream = p.open(
        format=FORMAT
        ,channels=CHANNELS
        ,rate=int(RATE)
        ,input=True
        ,input_device_index=DEVICE_INDEX
        ,frames_per_buffer=BUFFER_SIZE)

    stream.start_stream()

    while True:
        data = stream.read(CHUNK_SIZE)
        if len(data) == 0:
            break
        else:
            yield stt_service_pb2.StreamingRecognitionRequest(audio_content=data)



def run():
    channel = grpc.insecure_channel('localhost:5001')
    stub = stt_service_pb2_grpc.SttServiceStub(channel)
    it = stub.StreamingRecognize(gen())

    try:
        for r in it:
            try:
                print('Start chunk: ')
                for alternative in r.chunks[0].alternatives:
                    print('alternative: ', alternative.text)
                    print('alternative_confidence: ', alternative.confidence)
                    print('words: ', alternative.words)
                print('Is final: ', r.chunks[0].final)
                print('')
            except LookupError:
                print('No available chunks')
    except grpc._channel._Rendezvous as err:
        print('Error code %s, message: %s' % (err._state.code, err._state.details))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--device-index', required=False, help='input device index')
    parser.add_argument('--list-device', required=False, action="store_true", help='display device list') #just a flag
    args = parser.parse_args()

    if args.list_device == True:
        list_devices()
        sys.exit()

    if args.device_index is not None:
        DEVICE_INDEX = args.device_index
        RATE = p.get_device_info_by_index[DEVICE_INDEX]['defaultSampleRate']
    else :
        DEVICE_INDEX = p.get_default_input_device_info()['index']
        RATE = p.get_default_input_device_info()['defaultSampleRate']
    
    run()
