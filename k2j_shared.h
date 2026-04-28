#ifndef K2J_SHARED_H
#define K2J_SHARED_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define SHM_KEY 0x4B324A20
#define MSG_KEY 0x4B324A21
#define MAX_USERNAME 32
#define MAX_MSG 256

typedef struct {
    char username[MAX_USERNAME];
    char fingerprint[64];
    int is_banned;
    time_t ban_time;
} SecurityEntry;

typedef struct {
    long msg_type;
    char source[32];
    char target[32];
    char message[MAX_MSG];
    char username[MAX_USERNAME];
    char fingerprint[64];
} InterProcessMessage;

#endif