import time
from pymavlink import mavutil
import threading



def arm(self):
    # Arm main function
    self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                         mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
    self.vehicle.motors_armed_wait()
    self.state = "armed"

    time.sleep(3)
    # Create a cyclic thread to check if the vehicle is armed, if not, change the state to disarmed
    t = threading.Thread(target=self.check_armed_on_loop)
    t.start()

def arm_trigger(self, blocking):
    # Arm trigger function (blocking and non-blocking)
    if blocking:
        arm(self)
    else:
        t = threading.Thread(target=arm, args=(self,))
        t.start()

def check_armed(self):
    # Check if the vehicle is armed using a hearthbeat message
    if self.vehicle.motors_armed():
        # Update the state to armed if the vehicle is connected
        if self.state == 'connected':
            self.state = 'armed'
        return True
    else:
        return False

def check_armed_on_loop(self):
    # Check if the vehicle is armed in a loop
    while True:
        if not self.check_armed():
            self.state = 'connected'

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
            break
        time.sleep(1)

