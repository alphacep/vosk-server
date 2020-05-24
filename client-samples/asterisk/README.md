Plugin for Asterisk is avialable in a separate project:

https://github.com/alphacep/vosk-asterisk

We decided to provide asterisk modules to make integration really easy,
you can just have dialplan like this:

```
[internal]
exten = 1,1,Answer
same = n,Wait(1)
same = n,SpeechCreate
same = n,SpeechBackground(hello)
same = n,Verbose(0,Result was ${SPEECH_TEXT(0)})
```

It is also possible to forward audio to AMI/ARI/AGI and process audio
from the separate web appication, but in a long term you'll have to
recreate all asterisk on Statis by yourself, so we don't consider
it as a relevant way to impelment voice interface.

In a long term, the best way to implement user input with the natural user
experience is asynchronous process. And asynchronous input processing
requires something more complicated than current asterisk speech API. We
might implement more complex modules for speech  processing in asterisk
in the future.
