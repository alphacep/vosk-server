import {
  Injectable,
  ApplicationRef,
  Inject,
  Optional,
} from '@angular/core';

@Injectable()
export class DictateService {

  // Defaults
  readonly SERVER = "wss://api.alphacephei.com/asr/en/";
  // Send blocks 4 x per second as recommended in the server doc.
  readonly INTERVAL = 250;
  // Path to worker javascript
  readonly WORKER_PATH = 'assets/recorder-worker.js';

  // Error codes (mostly following Android error names and codes)
  readonly ERR_NETWORK = 2;
  readonly ERR_AUDIO = 3;
  readonly ERR_SERVER = 4;
  readonly ERR_CLIENT = 5;

  // Event codes
  readonly MSG_WAITING_MICROPHONE = 1;
  readonly MSG_MEDIA_STREAM_CREATED = 2;
  readonly MSG_INIT_RECORDER = 3;
  readonly MSG_RECORDING = 4;
  readonly MSG_SEND = 5;
  readonly MSG_SEND_EMPTY = 6;
  readonly MSG_SEND_EOS = 7;
  readonly MSG_WEB_SOCKET = 8;
  readonly MSG_WEB_SOCKET_OPEN = 9;
  readonly MSG_WEB_SOCKET_CLOSE = 10;
  readonly MSG_STOP = 11;
  readonly MSG_SERVER_CHANGED = 12;

  private config;
  private audioContext;
  private worker;
  private ws;
  private intervalKey;
  private paused;

  constructor() {
  }

  init(cfg) {

    this.config = cfg || {};
    this.config.server = this.config.server || this.SERVER;
    this.config.audioSourceId = this.config.audioSourceId;
    this.config.interval = this.config.interval || this.INTERVAL;
    this.config.onReadyForSpeech = this.config.onReadyForSpeech || function() { };
    this.config.onEndOfSpeech = this.config.onEndOfSpeech || function() { };
    this.config.onResults = this.config.onResults || function(data) { };
    this.config.onPartialResults = this.config.onPartialResults || function(data) { };
    this.config.onEndOfSession = this.config.onEndOfSession || function() { };
    this.config.onEvent = this.config.onEvent || function(e, data) { };
    this.config.onError = this.config.onError || function(e, data) { };

    this.paused = true;

    var audioSourceConstraints = {};
    this.config.onEvent(this.MSG_WAITING_MICROPHONE, "Waiting for approval to access your microphone ...");

    try {
      (<any> window).AudioContext = (<any> window).AudioContext || (<any> window).webkitAudioContext;
      navigator.getUserMedia = navigator.getUserMedia || (<any> navigator).webkitGetUserMedia;
      this.audioContext = new AudioContext();

      if (navigator.getUserMedia) {
        if (this.config.audioSourceId) {
          (<any> audioSourceConstraints).audio = {
            optional: [{ sourceId: this.config.audioSourceId }]
          };
        } else {
          (<any> audioSourceConstraints).audio = true;
        }
        navigator.getUserMedia(audioSourceConstraints, this.startUserMedia.bind(this), function(e) {
          this.config.onError(this.ERR_CLIENT, "No live audio input in this browser: " + e);
        });
      } else {
        this.config.onError(this.ERR_CLIENT, "No user media support");
      }
    } catch (e) {
      // Firefox 24: TypeError: AudioContext is not a constructor
      // Set media.webaudio.enabled = true (in about:this.config) to fix this.
      this.config.onError(this.ERR_CLIENT, "Error initializing Web Audio browser: " + e + " " + e.stack);
    }

    try {
      this.createWebSocket();
    } catch (e) {
      this.config.onError(this.ERR_CLIENT, "No web socket support in this browser!" + e + " " + e.stack);
    }
  }

  isInitialized() {
    return this.ws != null;
  }

  pause() {
    this.paused = true;
  }

  resume() {
    this.paused = false;
  }

  isRunning() {
    return this.paused;
  }

  // Cancel everything without waiting on the server
  cancel() {
    // Stop the regular sending of audio (if present)
    clearInterval(this.intervalKey);
    if (this.worker) {
      this.pause();
      this.clearWorker();
      this.config.onEvent(this.MSG_STOP, 'Stopped recording');
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  public startUserMedia(stream) {
    var input = this.audioContext.createMediaStreamSource(stream);
    this.config.onEvent(this.MSG_MEDIA_STREAM_CREATED, 'Media stream created');
    //Firefox loses the audio input stream every five seconds
    // To fix added the input to window.source
    (<any> window).source = input;

    // make the analyser available in window context
    (<any> window).userSpeechAnalyser = this.audioContext.createAnalyser();
    input.connect((<any> window).userSpeechAnalyser);

    this.initWorker(input);
    this.config.onEvent(this.MSG_INIT_RECORDER, 'Recorder initialized');
  }

  private socketSend(blob) {
    if (this.paused)
      return;
    if (this.ws) {
      var state = this.ws.readyState;
      if (state == 1) {
        // If blob is an audio blob
        if (blob instanceof Blob) {
          if (blob.size > 0) {
            this.ws.send(blob);
            this.config.onEvent(this.MSG_SEND, 'Send: blob: ' + blob.type + ', ' + blob.size);
          } else {
            this.config.onEvent(this.MSG_SEND_EMPTY, 'Send: blob: ' + blob.type + ', EMPTY');
          }
          // Otherwise it's the EOS tag (string)
        } else {
          this.ws.send(blob);
          this.config.onEvent(this.MSG_SEND_EOS, 'Send tag: ' + blob);
        }
      } else {
        this.config.onError(this.ERR_NETWORK, 'WebSocket: readyState!=1: ' + state + ": failed to send: " + blob);
      }
    } else {
      this.config.onError(this.ERR_CLIENT, 'No web socket connection: failed to send: ' + blob);
    }
  }

  private createWebSocket() {
    this.ws = new WebSocket(this.config.server);

    this.ws.onmessage = (e) => {
      var data = e.data;
      this.config.onEvent(this.MSG_WEB_SOCKET, data);
      if (data instanceof Object && !(data instanceof Blob)) {
        this.config.onError(this.ERR_SERVER, 'WebSocket: onEvent: got Object that is not a Blob');
      } else if (data instanceof Blob) {
        this.config.onError(this.ERR_SERVER, 'WebSocket: got Blob');
      } else {
        var res = JSON.parse(data);
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
      this.intervalKey = setInterval(() => {
        this.exportWorkerData();
      }, this.config.interval);

      // Start recording
      this.resume();
      this.config.onReadyForSpeech();
      this.config.onEvent(this.MSG_WEB_SOCKET_OPEN, "Opened the socket successfully");
    };

    // This can happen if the blob was too big
    // E.g. "Frame size of 65580 bytes exceeds maximum accepted frame size"
    // Status codes
    // http://tools.ietf.org/html/rfc6455#section-7.4.1
    // 1005:
    // 1006:
    this.ws.onclose = (e) => {
      var code = e.code;
      var reason = e.reason;
      var wasClean = e.wasClean;
      // The server closes the connection (only?)
      // when its endpointer triggers.
      this.config.onEndOfSession();
      this.config.onEvent(this.MSG_WEB_SOCKET_CLOSE, e.code + "/" + e.reason + "/" + e.wasClean);
    };

    this.ws.onerror = (e) => {
      var data = e.data;
      this.config.onError(this.ERR_NETWORK, data);
    };
  }

  private initWorker(source) {
    var node = source.context.createScriptProcessor(4096, 1, 1);
    this.worker = new Worker(this.WORKER_PATH);

    this.worker.onmessage = (e) => {
      if (this.paused) return;

      var blob = e.data;
      this.socketSend(blob);
    };

    node.onaudioprocess = (e) => {
      if (this.paused) return;

      this.worker.postMessage({
        command: 'record',
        buffer: [
          e.inputBuffer.getChannelData(0)
        ]
      });
    };

    this.worker.postMessage({
      command: 'init',
      config: {
        sampleRate: source.context.sampleRate
      }
    });

    source.connect(node);
    node.connect(source.context.destination);    //TODO: this should not be necessary (try to remove it)
  }

  private clearWorker() {
    this.worker.postMessage({ command: 'clear' });
  }

  private exportWorkerData() {
    this.worker.postMessage({ command: 'exportData' });
  }

}
