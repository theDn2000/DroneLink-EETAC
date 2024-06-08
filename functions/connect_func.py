import threading
import time
from pymavlink import mavutil
import sys
import itertools



def connect(self, connection_string, baud=115200):
    # Connect main function, connects 
    if self.state == 'disconnected':
        print('- DroneLink: Connecting to the vehicle...')
        done = False
        # Animation while connecting
        def animate():
            for c in itertools.cycle(['|', '/', '-', '\\']):
                if done:
                    break
                sys.stdout.write('\rConnecting ' + c)
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write('\rConnected to flight controller     \n')

        t = threading.Thread(target=animate)
        t.start()

        self.vehicle = mavutil.mavlink_connection(connection_string, baud)
        self.vehicle.wait_heartbeat()

        time.sleep(1)
        done = True
        time.sleep(1)

        self.sending_telemetry_info = True
        self.state = 'connected'

    else:
        print('- DroneLink: Already connected to the vehicle')

def connect_trigger(self, connection_string, blocking, baud=115200):
    # Connect trigger function (blocking or non-blocking)
    if blocking:
        connect(self, connection_string)
    else:
        t = threading.Thread(target=connect, args=(self, connection_string, baud))
        t.start()

def disconnect(self):
    # Close the connection
    if self.state != 'disconnected':
        # Set the state to disconnected
        self.state = 'disconnected'
        self.sending_telemetry_info = False
        # Close the connection
        self.vehicle.close()
        