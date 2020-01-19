const websocket = require('ws');
const fs = require('fs');
const ws = new websocket('wss://api.alphacephei.com/asr/en/');

ws.on('open', function open() {
  var readStream = fs.createReadStream('test.wav');
  readStream.on('data', function (chunk) {
      ws.send(chunk);
  });
  readStream.on('end', function () {
      ws.send('{"eof" : 1}');
  });
});

ws.on('message', function incoming(data) {
  console.log(data);
});

ws.on('close', function close() {
  process.exit()
});
