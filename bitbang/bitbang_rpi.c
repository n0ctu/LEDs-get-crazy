#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdint.h>

// Include Raspberry Pi specific headers
#include <bcm_host.h>

// Define PAGE_SIZE and BLOCK_SIZE if not defined
#ifndef PAGE_SIZE
#define PAGE_SIZE (4*1024)
#endif
#ifndef BLOCK_SIZE
#define BLOCK_SIZE (4*1024)
#endif

int mem_fd;
void *gpio_map;

// I/O access
volatile unsigned *gpio;

// GPIO setup macros. Always use INP_GPIO(x) before using OUT_GPIO(x)
#define INP_GPIO(g) *(gpio+((g)/10)) &= ~(7<<(((g)%10)*3))
#define OUT_GPIO(g) *(gpio+((g)/10)) |=  (1<<(((g)%10)*3))
#define GPIO_SET *(gpio+7)  // sets   bits which are 1, ignores bits which are 0
#define GPIO_CLR *(gpio+10) // clears bits which are 1, ignores bits which are 0

unsigned get_gpio_base() {
    switch (bcm_host_get_processor_id()) {
        case BCM_HOST_PROCESSOR_BCM2835: return 0x20000000;
        case BCM_HOST_PROCESSOR_BCM2836: return 0x3F000000;
        case BCM_HOST_PROCESSOR_BCM2837: return 0x3F000000;
        case BCM_HOST_PROCESSOR_BCM2711: return 0xFE000000;
        default: 
            fprintf(stderr, "Unknown processor ID. Cannot determine GPIO base address.\n");
            exit(EXIT_FAILURE);
    }
}

// Set up a memory regions to access GPIO
void setup_io() {
    unsigned gpio_base = get_gpio_base();

    // Open /dev/mem
    if ((mem_fd = open("/dev/mem", O_RDWR|O_SYNC) ) < 0) {
        printf("can't open /dev/mem \n");
        exit(-1);
    }

    // Map GPIO
    gpio_map = mmap(
        NULL,             // Any adddress in our space will do
        BLOCK_SIZE,       // Map length
        PROT_READ|PROT_WRITE,// Enable reading & writing to mapped memory
        MAP_SHARED,       // Shared with other processes
        mem_fd,           // File to map
        gpio_base         // Offset to GPIO peripheral
    );

    close(mem_fd); // No need to keep mem_fd open after mmap

    if (gpio_map == MAP_FAILED) {
        printf("mmap error %ld\n", (uintptr_t)gpio_map);
        exit(-1);
    }

    // Always use volatile pointer!
    gpio = (volatile unsigned *)gpio_map;
}

// Set GPIO pin to output
void gpio_output(int pin) {
    INP_GPIO(pin); // must use INP_GPIO before we can use OUT_GPIO
    OUT_GPIO(pin);
}

// Set GPIO pin high or low
void gpio_write(int pin, int value) {
    if (value)
        GPIO_SET = 1 << pin;
    else
        GPIO_CLR = 1 << pin;
}

// Function to provide a precise delay in nanoseconds
void nsleep(long nanoseconds) {
    struct timespec req, rem;

    if (nanoseconds > 999999999L) {
        req.tv_sec = (int)(nanoseconds / 1000000000L);
        nanoseconds = nanoseconds % 1000000000L;
    } else {
        req.tv_sec = 0;
    }
    req.tv_nsec = nanoseconds;
    nanosleep(&req, &rem);
}

// Function to send bytestream with specific timings
void send_bits(int gpio_pin, long t0h_t1l_ns, long t1h_t0l_ns, const uint8_t* bytes, int length) {
    bcm_host_init();
    setup_io();
    gpio_output(gpio_pin); // Set GPIO pin to output

    for (int i = 0; i < length; ++i) {
        for (int bit = 0; bit < 8; ++bit) {
            // Determine if the current bit is 0 or 1
            int value = (bytes[i] >> (7 - bit)) & 1;
            gpio_write(gpio_pin, 1); // Set pin high

            // Apply high time for 0 or 1
            nsleep(value ? t1h_t0l_ns : t0h_t1l_ns);

            gpio_write(gpio_pin, 0); // Set pin low

            // Apply low time for 0 or 1
            nsleep(value ? t0h_t1l_ns : t1h_t0l_ns);
        }
    }

    // Ensure the pin is low after transmission
    gpio_write(gpio_pin, 0);
    bcm_host_deinit();
}

// main function for testing
int main() {
    printf("Sending WS2815 test data to pin 18...\n");
    // Test data for WS2815: 4 pixels red, green, blue, white
    uint8_t data[] = {0x00, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF};
    // send_bits(gpio_pin, T0H/T1L timing in nanoseconds, T1H/T0L timing in nanoseconds, data, length)
    send_bits(18, 300, 1090, data, sizeof(data));
    return 0;
}