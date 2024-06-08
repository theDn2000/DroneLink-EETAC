import threading
import time
from pymavlink import mavutil



def land(self):
    # Land the vehicle
    self.going = True
    self.direction = "Land"
    # Create a message to send to the vehicle
    msg = self.vehicle.mav.command_long_encode(
        0, 0,  # target system, target component
        mavutil.mavlink.MAV_CMD_NAV_LAND,  # command
        0,  # confirmation
        0, 0, 0, 0,  # params 1-4
        0, 0, 0)  # params 5-7
    # Send command to vehicle
    self.vehicle.mav.send(msg)
    self.state = "landing"
    # Wait for the vehicle to land
    while self.alt > 0.1:
        time.sleep(0.1)

    # Set the vehicle to stabilize mode
    mode = 'STABILIZE'
    # Check if mode is available
    if mode not in self.vehicle.mode_mapping():
        print('- DroneLink: Unknown mode : {}'.format(mode))
        print('- DroneLink: Try:', list(self.vehicle.mode_mapping().keys()))

    # Get mode ID
    mode_id = self.vehicle.mode_mapping()[mode]
    self.vehicle.mav.set_mode_send(
        self.vehicle.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id)
    arm_msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=False, timeout=3)
    print('- DroneLink: Mode changed to STABILIZE')

    self.vehicle.motors_disarmed_wait()
    self.going = False
    self.state = 'connected'
    self.reaching_waypoint = False
    self.direction = "init"

def land_trigger(self, blocking=False):
    # Trigger the land function (blocking or non-blocking)
    if blocking:
        self.land()
    else:
        w = threading.Thread(target=self.land)
        w.start()
    