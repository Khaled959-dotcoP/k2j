#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <time.h>

#define PORT 9092
#define MAX_BUFFER 4096

FILE* logfile;

void log_msg(const char* msg) {
    time_t now = time(NULL);
    fprintf(logfile, "%s [C] %s\n", ctime(&now), msg);
    fflush(logfile);
}

void* listen_from_cpp(void* arg) {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;
    
    bind(server_fd, (struct sockaddr*)&addr, sizeof(addr));
    listen(server_fd, 10);
    log_msg("[C] Listening on port 9092");
    
    while(1) {
        int client = accept(server_fd, NULL, NULL);
        char buffer[MAX_BUFFER] = {0};
        read(client, buffer, sizeof(buffer)-1);
        log_msg(("[C] Packet inspected: " + string(buffer).substr(0,50)).c_str());
        close(client);
    }
    return NULL;
}

int main() {
    logfile = fopen("k2j_c.log", "a");
    log_msg("[C] K2J C Filter Started");
    
    pthread_t thread;
    pthread_create(&thread, NULL, listen_from_cpp, NULL);
    
    while(1) {
        sleep(30);
        log_msg("[C] Heartbeat");
    }
    
    fclose(logfile);
    return 0;
}
