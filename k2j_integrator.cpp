#include <iostream>
#include <thread>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <fstream>
#include <ctime>
#include <jsoncpp/json/json.h>
#include <sqlite3.h>

using namespace std;

sqlite3* db = nullptr;
ofstream logfile;

void log_msg(const char* msg) {
    time_t now = time(NULL);
    logfile << ctime(&now) << " [C++] " << msg << endl;
    logfile.flush();
}

void init_sqlite() {
    sqlite3_open("k2j_armory.db", &db);
    log_msg("[SQLite] Connected from C++");
}

void forward_to_java(const Json::Value& data) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9091);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
    if(connect(sock, (sockaddr*)&addr, sizeof(addr)) == 0) {
        string msg = data.toStyledString();
        send(sock, msg.c_str(), msg.length(), 0);
    }
    close(sock);
}

void forward_to_c(const Json::Value& data) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9092);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
    if(connect(sock, (sockaddr*)&addr, sizeof(addr)) == 0) {
        string msg = data.toStyledString();
        send(sock, msg.c_str(), msg.length(), 0);
    }
    close(sock);
}

void listen_from_python() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9090);
    addr.sin_addr.s_addr = INADDR_ANY;
    
    bind(server_fd, (sockaddr*)&addr, sizeof(addr));
    listen(server_fd, 10);
    log_msg("[C++] Listening for Python on port 9090");
    
    while(true) {
        int client = accept(server_fd, nullptr, nullptr);
        char buffer[4096] = {0};
        read(client, buffer, sizeof(buffer)-1);
        
        Json::Value root;
        Json::Reader reader;
        if(reader.parse(buffer, root)) {
            log_msg(("Received from Python: " + root.toStyledString()).c_str());
            forward_to_java(root);
            forward_to_c(root);
        }
        close(client);
    }
}

int main() {
    logfile.open("k2j_cpp.log", ios::app);
    log_msg("[C++] K2J Integrator Started");
    init_sqlite();
    
    thread py_thread(listen_from_python);
    py_thread.detach();
    
    log_msg("[C++] All connections active - Python(9090) -> Java(9091) -> C(9092)");
    
    while(true) {
        sleep(60);
        log_msg("[C++] Heartbeat - Integration active");
    }
    
    sqlite3_close(db);
    return 0;
}
