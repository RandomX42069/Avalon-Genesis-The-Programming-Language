#include <stdio.h>

int function(char* string) {
    int index = 0;
    while (string[index] != '\0') {
        index++;
    }
    return index;
}

int main() {
    function("hello world!");
    return 0;
}