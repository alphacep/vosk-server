var source;
var context;
var processor;
var streamLocal;
var inputArea;
var webSocket;
const sampleRate = 8000;
const wsURL = 'ws://localhost:2700';


(function () {
    document.addEventListener('DOMContentLoaded', (event) => {
        inputArea = document.getElementById('q');

        const listenButton = document.getElementById('listen');

        listenButton.addEventListener('mousedown', function (event) {
            initWS();
            navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    channelCount: 1,
                    sampleRate
                }, video: false
            }).then(handleSuccess);
            listenButton.style.color= 'green';
        });

        listenButton.addEventListener('mouseup', function (event) {
            webSocket.send('{"eof" : 1}');
            webSocket.close();

            processor.port.close();
            source.disconnect(processor);
            context.close();

            if (streamLocal.active) {
                streamLocal.getTracks()[0].stop();
            }
            listenButton.style.color= 'black';
        });

    });
}())


const handleSuccess = function (stream) {
    streamLocal = stream;

    context = new AudioContext({sampleRate: sampleRate});

    context.audioWorklet.addModule('data-conversion-processor.js').then(
        function () {
            processor = new AudioWorkletNode(context, 'data-conversion-processor', {
                channelCount: 1,
                numberOfInputs: 1,
                numberOfOutputs: 1
            });
            let constraints = {audio: true};
            navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
                source = context.createMediaStreamSource(stream);

                source.connect(processor);
                processor.connect(context.destination);

                processor.port.onmessage = event => webSocket.send(event.data)
                processor.port.start()
            });
        }
    );
};

function initWS() {
    webSocket = new WebSocket(wsURL);
    webSocket.binaryType = "arraybuffer";

    webSocket.onopen = function (event) {
        console.log('New connection established');
    };

    webSocket.onerror = function (event) {
        console.error(event.data);
    };

    webSocket.onmessage = function (event) {
        if (event.data) {
            let parsed = JSON.parse(event.data);
            if (parsed.result) console.log(parsed.result);
            if (parsed.text) inputArea.innerText = parsed.text;
        }
    };
}

