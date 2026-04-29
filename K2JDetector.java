import java.net.*;
import java.io.*;
import java.util.*;
import java.time.*;

public class K2JDetector {
    
    private static Map<String, Integer> requestCount = new HashMap<>();
    private static Set<String> blockedIPs = new HashSet<>();
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
    
    static void analyzeRequest(String source, String data) {
        int count = requestCount.getOrDefault(source, 0) + 1;
        requestCount.put(source, count);
        
        if(count > 10) {
            log("DDoS PATTERN DETECTED from " + source + " - BLOCKING");
            blockedIPs.add(source);
        }
        
        log("Request from " + source + " | Count: " + count + " | Data: " + data.substring(0, Math.min(100, data.length())));
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
                        analyzeRequest("cpp_source", msg);
                        
                        // Forward to Python via separate connection? Or just log
                        log("[Java] Processing complete for: " + msg.substring(0, Math.min(50, msg.length())));
                    }
                    s.close();
                }
            } catch(Exception e) {
                log("[Java] Error: " + e.getMessage());
            }
        }
    }
    
    static class CListener extends Thread {
        public void run() {
            try(ServerSocket server = new ServerSocket(9093)) {
                log("[Java] Listening for C on port 9093");
                while(true) {
                    Socket s = server.accept();
                    BufferedReader in = new BufferedReader(new InputStreamReader(s.getInputStream()));
                    String msg = in.readLine();
                    
                    if(msg != null) {
                        analyzeRequest("c_source", msg);
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
        log("[Java] Threshold: 10 requests per source");
        log("[Java] Listening on ports 9091 (C++) and 9093 (C)");
        
        new CppListener().start();
        new CListener().start();
        
        while(true) {
            try { Thread.sleep(60000); } catch(Exception e) {}
            log("[Java] Heartbeat - Active blocks: " + blockedIPs.size());
            log("[Java] Active request counts: " + requestCount.size());
        }
    }
}
