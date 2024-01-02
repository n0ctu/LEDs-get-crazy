import sys, signal
from config import Config
from interface import Interface
from text import Text

if __name__ == "__main__":

    # Handle SIGTERM when running as a service
    def handle_sigterm(signum, frame):
        #status(canvas, "INFO: Service stopped.", "sigterm x_x", "red")
        sys.exit(0)
    signal.signal(signal.SIGTERM, handle_sigterm)

    try:

        # Check if the current platform is supported
        try:
            import board
            import neopixel
        except:
            print("WARNING: The UDP interface requires a Raspberry Pi or similar device with GPIO pins. Development/Preview mode only (no board/no neopixel).")

        # Load config from YAML file
        config = Config('../config.yaml')

        # Start the interface
        interface = Interface(config)
        interface.udp_listener()

    except KeyboardInterrupt:
        #status("INFO: Aborted by user interaction.", "aborted by user x_x", "red")
        sys.exit(0)