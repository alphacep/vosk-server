import com.neovisionaries.ws.client.*;

import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.DataLine;
import javax.sound.sampled.TargetDataLine;
import java.util.concurrent.*;
import java.util.ArrayList;
import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;

public class VoiceClientWithMic {

    private ArrayList<String> results = new ArrayList<String>();
    private CountDownLatch recieveLatch;


    public static void main(String[] args) throws Exception {
        VoiceClientWithMic client = new VoiceClientWithMic();
        TargetDataLine line = client.getLine();
        ArrayList<String> asr = client.asr(line);
        for (String res : asr) {
            System.out.println(res);
        }
    }

    public ArrayList<String> asr(TargetDataLine line) throws Exception {
        WebSocketFactory factory = new WebSocketFactory();
        WebSocket ws = factory.createSocket("ws://localhost:2700");
        ws.addListener(new CustomWebSocketAdapter());
        ws.connect();

        try {
            AudioInputStream audioInputStream = new AudioInputStream(line);
            AudioFormat format = audioInputStream.getFormat();
            int bytesPerFrame = format.getFrameSize();
            if (bytesPerFrame == AudioSystem.NOT_SPECIFIED) {
                bytesPerFrame = 1;
            }

            // Let Vosk server now the sample rate of sound file
            ws.sendText("{ \"config\" : { \"sample_rate\" : " + (int)format.getSampleRate() + " } }");

            // Set an arbitrary buffer size of 1024 frames.
            int numBytes = 1024 * bytesPerFrame;
            byte[] audioBytes = new byte[numBytes];
            try {
                int numBytesRead = 0;
                // Try to read numBytes bytes from the file.
                while ((numBytesRead = audioInputStream.read(audioBytes)) != -1) {
                    recieveLatch = new CountDownLatch(1);
                    ws.sendBinary(audioBytes);
                    recieveLatch.await();
                }
                disconnect(ws);
            } catch (Exception e) {
                e.printStackTrace();
	    }
        } catch (Exception ex) {
            ex.printStackTrace();
        }
        return results;
    }

    private void disconnect(WebSocket ws) {
        recieveLatch = new CountDownLatch(1);
        ws.sendText("{\"eof\" : 1}");
        try {
            recieveLatch.await();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        ws.disconnect();
    }



    private TargetDataLine getLine() {
        TargetDataLine line;

        //It must be a 16 kHz (or 8 kHz, depending on the training data), 16bit Mono (= single channel) Big-Endian
        AudioFormat.Encoding encoding = AudioFormat.Encoding.PCM_SIGNED;
        float rate = 16000.0f;
        int channels = 1;
        int sampleSize = 16;
        boolean bigEndian = false;
        AudioFormat format = new AudioFormat(encoding, rate, sampleSize, channels, (sampleSize / 8) * channels, rate, bigEndian);
        DataLine.Info info = new DataLine.Info(TargetDataLine.class, format);

        if (!AudioSystem.isLineSupported(info)) {
            System.out.println("Line matching " + info + " not supported.");
            return null;
        } else
            System.out.println("Line matching " + info + " is supported.");

        try {
            line = (TargetDataLine) AudioSystem.getLine(info);
            line.open(format);
            line.start();

            System.out.println("Line open ");

            return line;

        } catch (Throwable e) {
            e.printStackTrace();
        }
        return null;
    }

    class CustomWebSocketAdapter extends WebSocketAdapter {
        @Override
        public void onTextMessage(WebSocket websocket, String message) {
            if (!message.contains("partial")) {
                results.add(message);
                System.out.println(message);
            }
            recieveLatch.countDown();
        }
    }
}
