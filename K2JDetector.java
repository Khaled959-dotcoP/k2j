import java.net.*;
import java.io.*;
import java.util.*;
import java.time.*;

public class K2JDetector {
    
    private static Set<String> bannedIPs = new HashSet<>();
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
    
    // Listen for C++ messages
    static class CPPListener extends Thread {
        public void run() {
            try(ServerSocket server = new ServerSocket(8082)) {
                log("Listening for C++ on port 8082");
                while(true) {
                    Socket s = server.accept();
                    BufferedReader in = new BufferedReader(new InputStreamReader(s.getInputStream()));
                    String msg = in.readLine();
                    
                    log("Received: " + msg);
                    
                    // DDoS pattern detection
                    if(msg != null && msg.contains("LOGIN")) {
                        String[] parts = msg.split("\"username\":\"");
                        if(parts.length > 1) {
                            String username = parts[1].split("\"")[0];
                            int count = requestCount.getOrDefault(username, 0) + 1;
                            requestCount.put(username, count);
                            
                            if(count > 10) {
                                log("DDoS PATTERN DETECTED! User: " + username);
                                bannedIPs.add(username);
                            }
                        }
                    }
                    s.close();
                }
            } catch(Exception e) {
                log("Error: " + e.getMessage());
            }
        }
    }
    
    public static void main(String[] args) {
        log("=== K2J JAVA DDoS DETECTOR STARTED ===");
        log("Monitoring for attack patterns...");
        
        new CPPListener().start();
        
        while(true) {
            try { Thread.sleep(60000); } catch(Exception e) {}
            log("Heartbeat - Active bans: " + bannedIPs.size());
        }
    }
}