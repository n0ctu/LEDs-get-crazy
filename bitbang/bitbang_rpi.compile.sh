# Download required packages which contain the header files for the Raspberry Pi
#sudo apt-get install libraspberrypi-dev raspberrypi-kernel-headers build-essential

# Compile the C code into a shared object file
# gcc -shared -o bitbang_rpi.so bitbang_rpi.c -fPIC -lbcm_host
gcc -g -o bitbang_rpi bitbang_rpi.c -fPIC -lbcm_host