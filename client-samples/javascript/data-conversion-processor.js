class DataConversionAudioProcessor extends AudioWorkletProcessor {

    constructor(options){
        super()
    }

    process(inputs, outputs, parameters) {
        const inputData = inputs[0][0];
        if (inputData) {
            const targetBuffer = new Int16Array(inputData.length);
            for (let index = inputData.length; index > 0; index--) {
                targetBuffer[index] = 32767 * Math.min(1, inputData[index]);
            }
            this.port.postMessage(targetBuffer.buffer);
        }
        return true;
    }
}

registerProcessor('data-conversion-processor', DataConversionAudioProcessor)