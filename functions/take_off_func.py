import threading
import time
from pymavlink import mavutil



def take_off(self, aTargetAltitude):
    # Take off the vehicle to a target altitude
        
    mode = 'GUIDED'

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
    arm_msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    print('- DroneLink: Mode changed to GUIDED')
    
    
    self.state = 'takingOff'
    self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component,
                                         mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, aTargetAltitude)

    while True:
        if self.alt >= aTargetAltitude * 0.95:
            break
        time.sleep(1)
    self.state = "flying"

    # Enable flying trigger
    self.flying_trigger()
    print("- DroneLink: Vehicle flying")

def take_off_trigger(self,aTargetAltitude, blocking):
    # Take off trigger function (for blocking and non-blocking)
    if blocking:
        take_off(self, aTargetAltitude, True)
    else:
        t = threading.Thread(target=self.take_off, args=[aTargetAltitude])
        t.start()






 