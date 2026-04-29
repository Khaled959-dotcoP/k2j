import java.net.*;
import java.io.*;
import java.util.*;
import java.time.*;

public class K2JDetector {
    
    private static Map<String, Integer> requestCount = new HashMap<>();
    private static PrintWriter logWriter;
    
    static {
        try {
            logWriter = new PrintWriter(new FileWriter("k2j_java.log", true));
        } catch(Exception e) {}
    }
    
    static void log(String msg) {
        String timestamp = Instant.now().toString();
        logWriter.println("[" + timestamp + "] [JAVA] " + msg);
        logWriter.flush();
    }
    
    static class CppListener extends Thread {
        public void run() {
            try(ServerSocket server = new ServerSocket(9091)) {
                log("[Java] Listening for C++ on port 9091");
                while(true) {
                    Socket s = server.accept();
                    BufferedReader in = new BufferedReader(new InputStreamReader(s.getInputStream()));
                    String msg = in.readLine();
                    if(msg != null) {
                        int count = requestCount.getOrDefault(msg, 0) + 1;
                        requestCount.put(msg, count);
                        log("[Java] DDoS check: " + msg.substring(0, Math.min(50, msg.length())) + " | Count: " + count);
                    }
                    s.close();
                }
            } catch(Exception e) {
                log("[Java] Error: " + e.getMessage());
            }
        }
    }
    
    public static void main(String[] args) {
        log("[Java] K2J DDoS Detector Started");
        new CppListener().start();
        while(true) {
            try { Thread.sleep(60000); } catch(Exception e) {}
            log("[Java] Heartbeat - Active monitors: " + requestCount.size());
        }
    }
}
