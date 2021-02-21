# webrtc vosk-server  


## Setup environment and run it. 
### Set model path  
Setup path to ./model  
The models can be download from here https://alphacephei.com/vosk/models   

### python environment   
The sample can work in python 3.8 
$ pip install aiortc aiohttp aiorpc vosk  
If your system install aiortc failed, please install gcc in your environment and use pip to install aiortc again.  

### Execution in local 
$ python asr_server_webrtc.py  
Open chrome browser with URL http://0.0.0.0:2700 and demo is there.   

But if your environment cannot run ,then do the following steps. 

chrome://flags/#enable-webrtc-hide-local-ips-with-mdns  
Enable this flag.   

chrome://flags/#unsafely-treat-insecure-origin-as-secure  
Enable this flag and add http://0.0.0.0:2700 in list.   

Click Relaunch button.  

Chrome reopen URL http://0.0.0.0:2700 again.  


