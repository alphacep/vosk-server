import com.neovisionaries.ws.client.*;
import java.io.*;
import java.nio.file.*;
import java.util.concurrent.*;
import java.util.ArrayList;

public class VoskClient {

    private ArrayList<String> results = new ArrayList<String>();
    private CountDownLatch recieveLatch;

    public ArrayList<String> transcribe(String path) throws Exception {
            WebSocketFactory factory = new WebSocketFactory();
            WebSocket ws = factory.createSocket("ws://localhost:2700");
            ws.addListener(new WebSocketAdapter() {
                @Override
                public void onTextMessage(WebSocket websocket, String message) {
                    results.add(message);
                    recieveLatch.countDown();
                }
            });
            ws.connect();

            FileInputStream fis = new FileInputStream(new File(path));
            DataInputStream dis = new DataInputStream(fis);
            byte[] buf = new byte[8000];
            while (true) {
                int nbytes = dis.read(buf);
                if (nbytes < 0) break;
                recieveLatch = new CountDownLatch(1);
                ws.sendBinary(buf);
                recieveLatch.await();
            }
            recieveLatch = new CountDownLatch(1);
            ws.sendText("{\"eof\" : 1}");
            recieveLatch.await();
            ws.disconnect();

            return results;
    }

    public static void main(String[] args) throws Exception {
        VoskClient client = new VoskClient();
        for (String res : client.transcribe("test.wav")) {
             System.out.println(res);
        }
    }
}

