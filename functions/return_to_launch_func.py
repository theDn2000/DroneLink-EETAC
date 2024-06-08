import threading
import time
from pymavlink import mavutil



def return_to_launch(self):
    # Return to launch main function
    mode = 'RTL'
    self.state = 'returningHome'
    self.going = True
    self.direction = "RTL"
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
    print('- DroneLink: Returning to launch')
    # Check if the vehicle is disarmed, if it is, set the state to connected
    while self.check_armed():
        time.sleep(1)

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

def return_to_launch_trigger(self, blocking=False):
    # Return to launch trigger function (blocking and non-blocking)
    if blocking:
        return_to_launch(self)
    else:
        t = threading.Thread(target=self.return_to_launch)
        t.start()