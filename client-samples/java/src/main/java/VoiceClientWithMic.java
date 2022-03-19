import com.neovisionaries.ws.client.*;

import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.DataLine;
import javax.sound.sampled.TargetDataLine;
import java.util.concurrent.*;
import java.util.ArrayList;

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

        byte[] buf = new byte[8000];
        while (true) {
            line.read(buf, 0, buf.length);
            if (results.size() > 0 && results.get(results.size() - 1).contains("exit")) {
                disconnect(ws);
                break;
            }
            recieveLatch = new CountDownLatch(1);
            ws.sendBinary(buf);
            recieveLatch.await();
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

        //It must be a 16 kHz (or 8 kHz, depending on the training data), 16bit Mono (= single channel) Little-Endian file
        AudioFormat.Encoding encoding = AudioFormat.Encoding.PCM_SIGNED;
        float rate = 8000.0f;
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
