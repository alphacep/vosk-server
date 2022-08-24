import { isNull } from "lodash";
import http from "../http";
import endpoint from "./endpoint";

const SERVER = endpoint.SOCKET_BASE_URL;

// Send blocks 4 x per second as recommended in the server doc.
const INTERVAL = 500;
// Path to this.worker javascript
const WORKER_PATH = "recorder-worker.js";
// import '../assets/recorder-worker'
// Error codes (mostly following Android error names and codes)
const ERR_NETWORK = 2;
const ERR_AUDIO = 3;
const ERR_SERVER = 4;
const ERR_CLIENT = 5;

// Event codes
const MSG_WAITING_MICROPHONE = 1;
const MSG_MEDIA_STREAM_CREATED = 2;
const MSG_INIT_RECORDER = 3;
const MSG_RECORDING = 4;
const MSG_SEND = 5;
const MSG_SEND_EMPTY = 6;
const MSG_SEND_EOS = 7;
const MSG_WEB_SOCKET = 8;
const MSG_WEB_SOCKET_OPEN = 9;
const MSG_WEB_SOCKET_CLOSE = 10;
const MSG_SERVER_CHANGED = 12;

let isOpendedOnce = false;

let audioContext = null;

let intervalKey = null;
let paused = null;
export default {
    config: null,
    worker: null,
    ws: null,
    MSG_STOP: 11,
    isEndOfFile: false,
    session_id: null,

    init(cfg) {
        this.isEndOfFile = false;
        this.session_id = null;
        this.config = cfg || {};
        this.config.server = this.config.server || SERVER;
        this.config.audioSourceId = this.config.audioSourceId;
        this.config.interval = this.config.interval || INTERVAL;
        this.config.onReadyForSpeech =
            this.config.onReadyForSpeech || function() {};
        this.config.onEndOfSpeech = this.config.onEndOfSpeech || function() {};
        this.config.onResults = this.config.onResults || function(data) {};
        this.config.onPartialResults =
            this.config.onPartialResults || function(data) {};
        this.config.onEndOfSession = this.config.onEndOfSession || function() {};
        this.config.onEvent = this.config.onEvent || function(e, data) {};
        this.config.onError = this.config.onError || function(e, data) {};

        paused = true;
        // console.log(cfg);

        var audioSourceConstraints = {};
        this.config.onEvent(
            MSG_WAITING_MICROPHONE,
            "Waiting for approval to access your microphone ..."
        );

        try {
            window.AudioContext = window.AudioContext || window.webkitAudioContext;
            navigator.getUserMedia =
                navigator.getUserMedia ||
                navigator.mozGetUserMedia ||
                navigator.webkitGetUserMedia;
            audioContext = new AudioContext();

            if (navigator.getUserMedia) {
                if (this.config.audioSourceId) {
                    audioSourceConstraints.audio = {
                        optional: [{ sourceId: this.config.audioSourceId }],
                    };
                } else {
                    audioSourceConstraints.audio = true;
                }
                if (!isOpendedOnce) {
                    navigator.getUserMedia(
                        audioSourceConstraints,
                        this.startUserMedia.bind(this),
                        function(e) {
                            this.config.onError(
                                ERR_CLIENT,
                                "No live audio input in this browser: " + e
                            );
                        }
                    );
                }
            } else {
                this.config.onError(ERR_CLIENT, "No user media support");
            }
        } catch (e) {
            // Firefox 24: TypeError: AudioContext is not a constructor
            // Set media.webaudio.enabled = true (in about:this.config) to fix
            this.config.onError(
                ERR_CLIENT,
                "Error initializing Web Audio browser: " + e + " " + e.stack
            );
        }

        try {
            this.createWebSocket();
        } catch (e) {
            this.config.onError(
                ERR_CLIENT,
                "No web socket support in this browser!" + e + " " + e.stack
            );
        }
        isOpendedOnce = true;
    },

    isInitialized() {
        return this.ws != null;
    },

    pause() {
        paused = true;
    },

    resume() {
        paused = false;
    },

    isRunning() {
        return paused;
    },

    // Cancel everything without waiting on the server
    cancel() {
        // Stop the regular sending of audio (if present)
        clearInterval(this.intervalKey);
        // console.log(this.worker);
        // console.log(this.ws);
        if (this.worker) {
            console.log("worker", this.worker);
            this.pause();
            this.clearWorker();
            this.config.onEvent(this.MSG_STOP, "Stopped recording");
        }
        if (this.ws) {
            console.log("ws", this.ws);
            this.ws.close();
            this.ws = null;
        }
    },

    startUserMedia(stream) {
        var input = audioContext.createMediaStreamSource(stream);
        this.config.onEvent(MSG_MEDIA_STREAM_CREATED, "Media stream created");
        //Firefox loses the audio input stream every five seconds
        // To fix added the input to window.source
        window.source = input;

        // make the analyser available in window context
        window.userSpeechAnalyser = audioContext.createAnalyser();
        input.connect(window.userSpeechAnalyser);

        this.initWorker(input);
        this.config.onEvent(MSG_INIT_RECORDER, "Recorder initialized");
    },

    socketSend(blob) {
        if (paused) return;
        if (this.ws) {
            var state = this.ws.readyState;
            if (state == 1) {
                // If blob is an audio blob
                if (blob instanceof Blob) {
                    if (blob.size > 0 && localStorage.getItem("session_id")) {
                        this.ws.send(blob);
                        this.config.onEvent(
                            MSG_SEND,
                            "Send: blob: " + blob.type + ", " + blob.size
                        );
                    } else {
                        this.config.onEvent(
                            MSG_SEND_EMPTY,
                            "Send: blob: " + blob.type + ", EMPTY"
                        );
                    }
                    // Otherwise it's the EOS tag (string)
                } else {
                    if (localStorage.getItem("session_id")) {
                        this.ws.send(blob);
                    }
                    this.config.onEvent(MSG_SEND_EOS, "Send tag: " + blob);
                }
            } else {
                setTimeout(() => {
                    // errorMessage('alert.Someissueinnetworkhappens')
                }, 1500);
                this.config.onError(
                    ERR_NETWORK,
                    "Connection problem; please retry"
                    // "WebSocket: readyState!=1: " + state + ": failed to send: " + blob
                );
            }
        } else {
            setTimeout(() => {
                //   errorMessage('alert.Someissueinnetworkhappens')
            }, 1500);
            this.config.onError(
                ERR_CLIENT,
                "Connection problem; please retry"
                // "No web socket connection: failed to send: " + blob
            );
        }
    },
    endOfFile() {
        this.pause();
        if (localStorage.getItem("session_id")) {
            this.ws.send('{"eof" : 1}');
        }
        this.isEndOfFile = true
    },

    saveModifiedData(body) {
        return http.post(endpoint.MODIFYING, body);
    },

    createWebSocket() {
        this.ws = new WebSocket(this.config.server);
        // console.log(this.ws);

        this.ws.onmessage = (e) => {
            let data = e.data;
            data = data
                .replace(/'/g, '"')
                .replace(/True/g, '"True"')
                .replace(/None/g, "[]")

            .replace(/False/g, '"False"');
            // debugger
            data = JSON.parse(data);
            if (data.hasOwnProperty('session_id')) {
                if (data.session_id) {
                    localStorage.setItem("session_id", data.session_id);
                    this.session_id = data.session_id;
                } else {
                    this.ws.close();
                    this.ws = null;
                }
            }

            if (data.socket_status) {
                if (data.socket_status == 503) {
                    this.ws.close();
                    this.ws = null;
                }
            }

            if (data) {
                if (data.partial) {
                    this.config.onPartialResults(data);
                }
                if (data.text) {
                    this.config.onResults(data);
                }
            }
            this.config.onEvent(MSG_WEB_SOCKET, data);
            if (data instanceof Object && !(data instanceof Blob)) {
                // this.config.onError(ERR_SERVER, 'WebSocket: onEvent: got Object that is not a Blob');
            } else if (data instanceof Blob) {
                // this.config.onError(ERR_SERVER, 'WebSocket: got Blob');
            } else {
                var res = data;
                if (res.continue) {
                    // do nothing
                } else if (res.partial) {
                    this.config.onPartialResults(res.partial);
                } else if (res.text) {
                    this.config.onResults(res.text);
                }
            }
        };

        // Start recording only if the socket becomes open
        this.ws.onopen = (e) => {
            intervalKey = setInterval(() => {
                this.exportWorkerData();
            }, this.config.interval);

            // Start recording
            this.resume();
            this.config.onReadyForSpeech();
            this.config.onEvent(
                MSG_WEB_SOCKET_OPEN,
                "Opened the socket successfully"
            );
        };

        // This can happen if the blob was too big
        // E.g. "Frame size of 65580 bytes exceeds maximum accepted frame size"
        // Status codes
        // http://tools.ietf.org/html/rfc6455#section-7.4.1
        // 1005:
        // 1006:
        this.ws.onclose = (e) => {
            this.config.onEndOfSession();
            this.config.onEvent(
                MSG_WEB_SOCKET_CLOSE,
                e.code + "/" + e.reason + "/" + e.wasClean
            );
        };

        this.ws.onerror = (e) => {
            setTimeout(() => {
                //   errorMessage('alert.Someissueinnetworkhappens')
            }, 1500);
            this.config.onError(ERR_NETWORK, "Some issue in network happens");
        };
    },

    initWorker(source) {
        if (window.Worker) {
            var node = source.context.createScriptProcessor(1024, 1, 1);
            if (isOpendedOnce) this.worker = new Worker(WORKER_PATH);
            // console.log(worker,'worker path');

            this.worker.onmessage = (e) => {
                if (paused) return;

                var blob = e.data;
                console.log(blob);
                this.socketSend(blob);
            };
            node.onaudioprocess = (e) => {
                if (paused) return;

                this.worker.postMessage({
                    command: "record",
                    buffer: [e.inputBuffer.getChannelData(0)],
                });
            };

            this.worker.postMessage({
                command: "init",
                config: {
                    sampleRate: 44000, //source.context.sampleRate
                },
            });
        }

        source.connect(node);
        node.connect(source.context.destination); //TODO: this should not be necessary (try to remove it)
    },

    clearWorker() {
        this.worker.postMessage({ command: "clear" });
    },

    exportWorkerData() {
        this.worker.postMessage({ command: "exportData" });
    },
};

window.onbeforeunload = function() {
    localStorage.removeItem('session_id');
}
