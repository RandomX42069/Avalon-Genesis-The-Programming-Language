#define NULL (void*)0

char* allocateMem(const int size) {
    if (!size) {return NULL;}
    char* buffer = malloc(size);
    return buffer;
}