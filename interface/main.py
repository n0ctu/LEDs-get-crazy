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

    # Load config from YAML file
    config = Config('../config.yaml')

    # Start the interface
    interface = Interface(config)
    interface.udp_listener()

