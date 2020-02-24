//////////////////////////////// JavaScript Audio Resampler (c) 2011 - Grant Galitz

function Resampler(fromSampleRate, toSampleRate, channels, outputBufferSize, noReturn) {
  this.fromSampleRate = fromSampleRate;
  this.toSampleRate = toSampleRate;
  this.channels = channels | 0;
  this.outputBufferSize = outputBufferSize;
  this.noReturn = !!noReturn;
  this.initialize();
}

Resampler.prototype.initialize = function() {
  //Perform some checks:
  if (this.fromSampleRate > 0 && this.toSampleRate > 0 && this.channels > 0) {
    if (this.fromSampleRate == this.toSampleRate) {
      //Setup a resampler bypass:
      this.resampler = this.bypassResampler;		//Resampler just returns what was passed through.
      this.ratioWeight = 1;
    }
    else {
      //Setup the interpolation resampler:
      this.compileInterpolationFunction();
      this.resampler = this.interpolate;			//Resampler is a custom quality interpolation algorithm.
      this.ratioWeight = this.fromSampleRate / this.toSampleRate;
      this.tailExists = false;
      this.lastWeight = 0;
      this.initializeBuffers();
    }
  }
  else {
    throw (new Error("Invalid settings specified for the resampler."));
  }
}

Resampler.prototype.compileInterpolationFunction = function() {
  var toCompile = "var bufferLength = Math.min(buffer.length, this.outputBufferSize);\
	if ((bufferLength % " + this.channels + ") == 0) {\
		if (bufferLength > 0) {\
			var ratioWeight = this.ratioWeight;\
			var weight = 0;";
  for (var channel = 0; channel < this.channels; ++channel) {
    toCompile += "var output" + channel + " = 0;"
  }
  toCompile += "var actualPosition = 0;\
			var amountToNext = 0;\
			var alreadyProcessedTail = !this.tailExists;\
			this.tailExists = false;\
			var outputBuffer = this.outputBuffer;\
			var outputOffset = 0;\
			var currentPosition = 0;\
			do {\
				if (alreadyProcessedTail) {\
					weight = ratioWeight;";
  for (channel = 0; channel < this.channels; ++channel) {
    toCompile += "output" + channel + " = 0;"
  }
  toCompile += "}\
				else {\
					weight = this.lastWeight;";
  for (channel = 0; channel < this.channels; ++channel) {
    toCompile += "output" + channel + " = this.lastOutput[" + channel + "];"
  }
  toCompile += "alreadyProcessedTail = true;\
				}\
				while (weight > 0 && actualPosition < bufferLength) {\
					amountToNext = 1 + actualPosition - currentPosition;\
					if (weight >= amountToNext) {";
  for (channel = 0; channel < this.channels; ++channel) {
    toCompile += "output" + channel + " += buffer[actualPosition++] * amountToNext;"
  }
  toCompile += "currentPosition = actualPosition;\
						weight -= amountToNext;\
					}\
					else {";
  for (channel = 0; channel < this.channels; ++channel) {
    toCompile += "output" + channel + " += buffer[actualPosition" + ((channel > 0) ? (" + " + channel) : "") + "] * weight;"
  }
  toCompile += "currentPosition += weight;\
						weight = 0;\
						break;\
					}\
				}\
				if (weight == 0) {";
  for (channel = 0; channel < this.channels; ++channel) {
    toCompile += "outputBuffer[outputOffset++] = output" + channel + " / ratioWeight;"
  }
  toCompile += "}\
				else {\
					this.lastWeight = weight;";
  for (channel = 0; channel < this.channels; ++channel) {
    toCompile += "this.lastOutput[" + channel + "] = output" + channel + ";"
  }
  toCompile += "this.tailExists = true;\
					break;\
				}\
			} while (actualPosition < bufferLength);\
			return this.bufferSlice(outputOffset);\
		}\
		else {\
			return (this.noReturn) ? 0 : [];\
		}\
	}\
	else {\
		throw(new Error(\"Buffer was of incorrect sample length.\"));\
	}";
  this.interpolate = Function("buffer", toCompile);
}

Resampler.prototype.bypassResampler = function(buffer) {
  if (this.noReturn) {
    //Set the buffer passed as our own, as we don't need to resample it:
    this.outputBuffer = buffer;
    return buffer.length;
  }
  else {
    //Just return the buffer passsed:
    return buffer;
  }
}

Resampler.prototype.bufferSlice = function(sliceAmount) {
  if (this.noReturn) {
    //If we're going to access the properties directly from this object:
    return sliceAmount;
  }
  else {
    //Typed array and normal array buffer section referencing:
    try {
      return this.outputBuffer.subarray(0, sliceAmount);
    }
    catch (error) {
      try {
        //Regular array pass:
        this.outputBuffer.length = sliceAmount;
        return this.outputBuffer;
      }
      catch (error) {
        //Nightly Firefox 4 used to have the subarray function named as slice:
        return this.outputBuffer.slice(0, sliceAmount);
      }
    }
  }
}

Resampler.prototype.initializeBuffers = function(generateTailCache) {
  //Initialize the internal buffer:
  try {
    this.outputBuffer = new Float32Array(this.outputBufferSize);
    this.lastOutput = new Float32Array(this.channels);
  }
  catch (error) {
    this.outputBuffer = [];
    this.lastOutput = [];
  }
}

//////////////////////////////// 

var recLength = 0,
  recBuffers = [],
  sampleRate,
  resampler;

this.onmessage = function(e) {
  switch (e.data.command) {
    case 'init':
      init(e.data.config);
      break;
    case 'record':
      record(e.data.buffer);
      break;
    case 'exportData':
      exportData();
      break;
    case 'clear':
      clear();
      break;
  }
};

function init(config) {
  sampleRate = config.sampleRate;
  resampler = new Resampler(sampleRate, 8000, 1, 50 * 1024, false);
}

function record(inputBuffer) {
  recBuffers.push(inputBuffer[0]);
  recLength += inputBuffer[0].length;
}

function exportData() {
  var buffer = mergeBuffers(recBuffers, recLength);
  var samples = resampler.resampler(buffer);
  var dataview = encodeRAW(samples);
  var audioBlob = new Blob([dataview], { type: 'audio/raw' });
  this.postMessage(audioBlob);
  clear();
}

function clear() {
  recLength = 0;
  recBuffers = [];
}

function mergeBuffers(recBuffers, recLength) {
  var result = new Float32Array(recLength);
  var offset = 0;
  for (var i = 0; i < recBuffers.length; i++) {
    result.set(recBuffers[i], offset);
    offset += recBuffers[i].length;
  }
  return result;
}

function floatTo16BitPCM(output, offset, input) {
  for (var i = 0; i < input.length; i++ , offset += 2) {
    var s = Math.max(-1, Math.min(1, input[i]));
    output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }
}

function encodeRAW(samples) {
  var buffer = new ArrayBuffer(samples.length * 2);
  var view = new DataView(buffer);
  floatTo16BitPCM(view, 0, samples);
  return view;
}

//////////////////////////////// 
