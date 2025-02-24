#include <stdio.h>
#include <stdint.h>

int main() {
    // Define two large signed 64-bit integers
    int64_t a = 4000000000000000000;  // First number
    int64_t b = 6000000000000000000;  // Second number

    // Perform the addition
    int64_t sum = a + b;

    // Print the result
    printf("Sum: %lld\n", sum);

    return 0;
}

