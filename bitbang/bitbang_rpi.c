#include <stdio.h>
#include <stdlib.h>
#include <string.h>
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

// Define peripheral addresses and offsets
#define BCM_PERI_BASE        bcm_host_get_peripheral_address()

#define GPIO_OFFSET          0x00200000

#define SYS_TIMER_OFFSET     0x00003000
#define SYS_TIMER_SIZE       0x1C
#define SYS_TIMER_CLO        0x04

#define ARM_TIMER_OFFSET     0x0000B000
#define ARM_TIMER_SIZE       0x424
#define ARM_TIMER_COUNTER    0x420
#define ARM_TIMER_CONTROL    0x408
#define ARM_TIMER_COUNTER_EN 0x00000280

#define ARM_TIMER_FREQ       250000000   // ARM timer frequency
#define ARM_TIMER_FREQ_PI4   500000000   // ARM timer frequency Pi 4

#define ONE_SEC_IN_US        1000000

int mem_fd;
void *gpio_map;

// I/O access
volatile unsigned *gpio;
volatile uint32_t* sys_timer;
volatile uint32_t* arm_timer;

// GPIO setup macros. Always use INP_GPIO(x) before using OUT_GPIO(x). According to https://elinux.org/RPi_GPIO_Code_Samples#Direct_register_access
#define INP_GPIO(g) *(gpio+((g)/10)) &= ~(7<<(((g)%10)*3))
#define OUT_GPIO(g) *(gpio+((g)/10)) |=  (1<<(((g)%10)*3))
#define GPIO_SET *(gpio+7)   // sets   bits which are 1, ignores bits which are 0
#define GPIO_CLR *(gpio+10)  // clears bits which are 1, ignores bits which are 0

// Set up a memory regions to access GPIO
void setup_io() {
    unsigned gpio_base = BCM_PERI_BASE + GPIO_OFFSET;

    // Open /dev/mem
    if ((mem_fd = open("/dev/mem", O_RDWR|O_SYNC) ) < 0) {
        printf("can't open /dev/mem \n");
        exit(-1);
    }

    // Map GPIO
    gpio_map = mmap(
        NULL,                 // Any adddress in our space will do
        BLOCK_SIZE,           // Map length
        PROT_READ|PROT_WRITE, // Enable reading & writing to mapped memory
        MAP_SHARED,           // Shared with other processes
        mem_fd,               // File to map
        gpio_base             // Offset to GPIO peripheral
    );

    close(mem_fd); // No need to keep mem_fd open after mmap

    if (gpio_map == MAP_FAILED) {
        printf("mmap error %ld\n", (uintptr_t)gpio_map);
        exit(-1);
    }

    // Always use volatile pointer!
    gpio = (volatile unsigned *)gpio_map;
    printf("GPIO mapped to 0x%lX\n", (uintptr_t)gpio);
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

// Function to convert nanoseconds to timer ticks
unsigned long ns_to_ticks(long nanoseconds, long osc_freq) {
    // System timer frequency on Raspberry Pi is typically 1MHz, ARM timer 250 or 500MHz
    return (nanoseconds * osc_freq) / 1000000000L;
}

// Function to set up and enable the ARM Timer
void setup_arm_timer() {
    // Open /dev/mem to access physical memory
    int mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (mem_fd == -1) {
        perror("Unable to open /dev/mem");
        exit(1);
    }

    // Map the ARM Timer's registers into memory
    arm_timer = (volatile uint32_t*)mmap(NULL, 
                                         ARM_TIMER_SIZE, 
                                         PROT_READ | PROT_WRITE, 
                                         MAP_SHARED, 
                                         mem_fd, 
                                         BCM_PERI_BASE + ARM_TIMER_OFFSET);
    if (arm_timer == MAP_FAILED) {
        perror("mmap for ARM Timer failed");
        close(mem_fd);
        exit(2);
    }

    // Calculate the indices for the control and counter registers
    int ctl_i = ARM_TIMER_CONTROL / 4;  // Divide by 4 to convert byte offset to uint32_t index
    int cnt_i = ARM_TIMER_COUNTER / 4;

    // Enable ARM Timer counter if not already enabled
    if (!(arm_timer[ctl_i] & ARM_TIMER_COUNTER_EN)) {
        arm_timer[ctl_i] = ARM_TIMER_COUNTER_EN;
    }

    // Optionally, print a debug message to verify the timer is enabled
    printf("ARM Timer enabled, control register: 0x%x\n", arm_timer[ctl_i]);

    // No need to keep mem_fd open after mmap
    close(mem_fd);
}

// Function to wait for a specific number of ARM timer ticks
void wait_timer_ticks(unsigned long ticks) {
    unsigned long start = arm_timer[ARM_TIMER_COUNTER / 4]; // Divide by 4 to get the register index
    while ((arm_timer[ARM_TIMER_COUNTER / 4] - start) < ticks);
}

// Function to send bytestream with specific timings
void send_bits(int gpio_pin, long t0h_t1l_ns, long t1h_t0l_ns, const uint8_t* bytes, int length) {
    bcm_host_init();
    setup_io();
    setup_arm_timer();
    gpio_output(gpio_pin); // Set GPIO pin to output

    // Calculate the number of ticks for each timing
    unsigned long t0h_ticks = ns_to_ticks(t0h_t1l_ns, ARM_TIMER_FREQ_PI4);
    unsigned long t1h_ticks = ns_to_ticks(t1h_t0l_ns, ARM_TIMER_FREQ_PI4);
    unsigned long t0l_ticks = t1h_ticks;
    unsigned long t1l_ticks = t0h_ticks;

    for (int i = 0; i < length; ++i) {
        for (int bit = 0; bit < 8; ++bit) {
            // Determine if the current bit is 0 or 1
            int value = (bytes[i] >> (7 - bit)) & 1;

            gpio_write(gpio_pin, 1); // Set pin high
            // printf("Sending: %d", value);

            // Apply high time for 0 or 1
            wait_timer_ticks(value ? t1h_ticks : t0h_ticks);
            // printf(" (high for %ld ticks)", value ? t1h_ticks : t0h_ticks);

            gpio_write(gpio_pin, 0); // Set pin low

            // Apply low time for 0 or 1
            wait_timer_ticks(value ? t0l_ticks : t1l_ticks);
            // printf(" (low for %ld ticks)\n", value ? t0l_ticks : t1l_ticks);
        }
    }

    // Ensure the pin is low after transmission
    gpio_write(gpio_pin, 0);
    bcm_host_deinit();
}

// main function for testing
int main(void) {
    printf("Sending WS2815 test data to pin 18...\n");
    // Test data for WS2815 (GRB): 4 pixels red, green, blue, white
    uint8_t data[] = {0x00, 0xFF, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF};
    // send_bits(gpio_pin, T0H/T1L timing in nanoseconds, T1H/T0L timing in nanoseconds, data, length)
    send_bits(18, 300, 1090, data, sizeof(data));
    return 0;
}