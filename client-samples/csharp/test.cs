// Requires at least Mono 5.0 due to TLS issues

using System;
using System.IO;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Net.WebSockets;


public class ASRTest
{
   async Task RecieveResult(ClientWebSocket ws) {
        byte[] result = new byte[4096];
        Task<WebSocketReceiveResult> receiveTask = ws.ReceiveAsync(new ArraySegment<byte>(result), CancellationToken.None);
        await receiveTask;
        var receivedString = Encoding.UTF8.GetString(result, 0, receiveTask.Result.Count);
        Console.WriteLine("Result {0}", receivedString);
   }

   async Task ProcessData(ClientWebSocket ws, byte[] data, int count) {
        await ws.SendAsync(new ArraySegment<byte>(data, 0, count), WebSocketMessageType.Binary, true, CancellationToken.None);
        await RecieveResult(ws);
   }

   async Task ProcessFinalData(ClientWebSocket ws) {
        byte[] eof = Encoding.UTF8.GetBytes("{\"eof\" : 1}");
        await ws.SendAsync(new ArraySegment<byte>(eof), WebSocketMessageType.Text, true, CancellationToken.None);
        await RecieveResult(ws);
   }

   async Task DecodeFile() {
        ClientWebSocket ws = new ClientWebSocket();
        await ws.ConnectAsync(new Uri("wss://api.alphacephei.com/asr/en/"), CancellationToken.None);

        FileStream fsSource = new FileStream("test.wav",
                   FileMode.Open, FileAccess.Read);

        byte[] data = new byte[8000];
        while (true) {
            int count = fsSource.Read(data, 0, 8000);
            if (count == 0)
                break;
            await ProcessData(ws, data, count);
        }
        await ProcessFinalData(ws);

        await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "OK", CancellationToken.None);
   }

   public static void Main() {
        Task.Run(async () => {
            await new ASRTest().DecodeFile();
        }).GetAwaiter().GetResult();
   }
}
