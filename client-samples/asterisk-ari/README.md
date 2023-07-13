This is an example of channel transcription through ARI/externalMedia

To configure statis make sure modules are loaded:

```
load = res_rtp_multicast.so
load = res_ari.so ; Asterisk RESTful Interface
load = res_ari_applications
load = res_ari_asterisk.so
load = res_ari_bridges
load = res_ari_channels.so
load = res_ari_device_states.so ; RESTful API module - Device state resources
load = res_ari_endpoints.so
load = res_ari_events.so
load = res_ari_model.so ; ARI Model validators
load = res_ari_playbacks.so
load = res_ari_recordings.so
load = res_ari_sounds
load = res_stasis.so ; Stasis application support
load = app_stasis.so ; Stasis dialplan application
load = res_stasis_answer.so
load = res_stasis_device_state.so ; Stasis application device state support
load = res_stasis_playback.so ; Stasis application playback support
load = res_stasis_recording.so ; Stasis application recording support
load = res_stasis_snoop.so ; Stasis application snoop support
```

then check ari.conf:

```
[general]
enabled = yes          
pretty = yes           
allowed_origins = *

[asterisk]
type = user
read_only = no
password = asterisk
```

Then the dialplan

```
exten => 4,1,Answer()
same =  n,Stasis(hello-world)
same =  n,Hangup()
```

Install required python modules


```
pip3 install aioudp asyncari vosk
```

And start the statis app:

```
python3 vosk_ari.py
```

Dial the extension, you should see the transcript on console
