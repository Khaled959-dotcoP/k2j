// K2J C++ INTEGRATOR - Connects Python, C, Java together
// Compile: g++ -o k2j_integrator k2j_integrator.cpp -lpthread

#include <iostream>
#include <thread>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <fstream>
#include <ctime>
#include <jsoncpp/json/json.h>  // sudo apt-get install libjsoncpp-dev

using namespace std;

int c_socket = -1;
int java_socket = -1;
ofstream logfile;

void log_to_file(const char* msg) {
    time_t now = time(NULL);
    logfile << ctime(&now) << " [C++] " << msg << endl;
    logfile.flush();
}

// Listen for Python messages
void python_listener() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8081);
    addr.sin_addr.s_addr = INADDR_ANY;
    
    bind(server_fd, (sockaddr*)&addr, sizeof(addr));
    listen(server_fd, 10);
    log_to_file("Listening for Python on port 8081");
    
    while(true) {
        int client = accept(server_fd, nullptr, nullptr);
        char buffer[1024] = {0};
        read(client, buffer, sizeof(buffer)-1);
        
        log_to_file(buffer);
        
        // Forward to C module
        if(c_socket > 0) {
            send(c_socket, buffer, strlen(buffer), 0);
        }
        
        // Forward to Java
        if(java_socket > 0) {
            send(java_socket, buffer, strlen(buffer), 0);
        }
        
        close(client);
    }
}

// Connect to C module
void connect_to_c() {
    c_socket = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8083);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
    
    while(connect(c_socket, (sockaddr*)&addr, sizeof(addr)) < 0) {
        log_to_file("Waiting for C module...");
        sleep(2);
    }
    log_to_file("Connected to C module on port 8083");
}

// Connect to Java
void connect_to_java() {
    java_socket = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(8082);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
    
    while(connect(java_socket, (sockaddr*)&addr, sizeof(addr)) < 0) {
        log_to_file("Waiting for Java module...");
        sleep(2);
    }
    log_to_file("Connected to Java on port 8082");
}

int main() {
    logfile.open("k2j_cpp.log", ios::app);
    log_to_file("=== K2J C++ INTEGRATOR STARTED ===");
    
    connect_to_c();
    connect_to_java();
    
    thread py_thread(python_listener);
    py_thread.detach();
    
    log_to_file("All connections established. System running.");
    
    while(true) {
        sleep(60);
        log_to_file("Heartbeat - Integration active");
    }
    
    return 0;
}