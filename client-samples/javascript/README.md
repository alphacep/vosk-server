### Vanilla JS Microphone Client - Audio Worklet vs Script Processor Node

This code shows two examples of communicating to a remote Vosk server using a microphone in javascript.  

One example is using the latest Audio Worklet API, the other example is using a deprecated Script Processor Node.

[Audio Worklet](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Using_AudioWorklet) has replaced a deprecated ScriptProcessorNode.  One issue with the new AudioWorkletProcessor, is that it only runs over https (see [this](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorkletNode) doc). 
In order to test it, one must run it on a secure server and streaming over to another (Vosk) secure server.  It should work in local environment if a localhost Vosk is running, 
but it won't work with a remote server over plain http.

Now deprecated ScriptProcessorNode is added as another example (voice_client_with_script_processor.js), so it is possible to still use ScriptProcessorNode instead, 
which will communicate over plain http.  

A pair of listen/stop listening buttons is added in the html to compare the two solutions.