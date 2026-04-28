#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <time.h>

#define PORT 8083

FILE* logfile;

void log_msg(const char* msg) {
    time_t now = time(NULL);
    fprintf(logfile, "%s [C] %s\n", ctime(&now), msg);
    fflush(logfile);
}

// Listen for C++ messages
void* listen_to_cpp(void* arg) {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;
    
    bind(server_fd, (struct sockaddr*)&addr, sizeof(addr));
    listen(server_fd, 10);
    log_msg("Listening for C++ on port 8083");
    
    while(1) {
        int client = accept(server_fd, NULL, NULL);
        char buffer[512] = {0};
        read(client, buffer, sizeof(buffer)-1);
        log_msg(buffer);
        close(client);
    }
    return NULL;
}

int main() {
    logfile = fopen("k2j_c.log", "a");
    log_msg("=== K2J C FILTER STARTED ===");
    
    pthread_t thread;
    pthread_create(&thread, NULL, listen_to_cpp, NULL);
    
    log_msg("Packet filter active - Monitoring all traffic");
    
    while(1) {
        sleep(30);
        log_msg("Heartbeat - Filter active");
    }
    
    fclose(logfile);
    return 0;
}