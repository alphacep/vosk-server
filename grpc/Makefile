GRPC_SOURCES = stt_service_pb2.py stt_service_pb2_grpc.py

all: $(GRPC_SOURCES)

$(GRPC_SOURCES): stt_service.proto
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. stt_service.proto

clean:
	rm $(GRPC_SOURCES)
