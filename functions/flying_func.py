import threading
import time
from pymavlink import mavutil



def flying_trigger(self):
    # Enable flying trigger function in a new thread (only non-blocking)
    w = threading.Thread(target=self.flying)
    w.start()

def flying(self):
    # Main flying function
    speed = 1
    end = False
    cmd = self.prepare_command(0, 0, 0)  # stop
    while not end:
        self.going = False
        while not self.going:
            if not self.reaching_waypoint:
                self.vehicle.mav.send(cmd)
                time.sleep(1)
        # a new go command has been received. Check direction
        print('- DroneLink: Going ', self.direction)
        if self.direction == "North":
            cmd = self.prepare_command(speed, 0, 0)  # NORTH
        if self.direction == "South":
            cmd = self.prepare_command(-speed, 0, 0)  # SOUTH
        if self.direction == "East":
            cmd = self.prepare_command(0, speed, 0)  # EAST
        if self.direction == "West":
            cmd = self.prepare_command(0, -speed, 0)  # WEST
        if self.direction == "NorthWest":
            cmd = self.prepare_command(speed, -speed, 0)  # NORTHWEST
        if self.direction == "NorthEast":
            cmd = self.prepare_command(speed, speed, 0)  # NORTHEST
        if self.direction == "SouthWest":
            cmd = self.prepare_command(-speed, -speed, 0)  # SOUTHWEST
        if self.direction == "SouthEast":
            cmd = self.prepare_command(-speed, speed, 0)  # SOUTHEST
        if self.direction == "Stop":
            cmd = self.prepare_command(0, 0, 0)  # STOP
        if self.direction == "RTL" or self.direction == "Land" or self.direction == "changingAltitude":
            end = True

def prepare_command(self, velocity_x, velocity_y, velocity_z):
    # Move vehicle in direction based on specified velocity vectors.
    msg = mavutil.mavlink.MAVLink_set_position_target_global_int_message(
        0,  # time_boot_ms (not used)
        self.vehicle.target_system,
        self.vehicle.target_component,  # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
        0b0000111111000111,  # type_mask (only speeds enabled)
        0,
        0,
        0,  # x, y, z positions (not used)
        velocity_x,
        velocity_y,
        velocity_z,  # x, y, z velocity in m/s
        0,
        0,
        0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0,
        0,
    )  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    return msg

def go_order(self, direction):
    # Set the direction of the vehicle
    self.direction = direction
    self.going = True

def check_flying_trigger(self, blocking=False):
    # Enable the check_flying function in a new thread
    if blocking:
        self.check_flying()
    else:
        w = threading.Thread(target=self.check_flying)
        w.start()

def check_flying(self):
    # Check if the vehicle is flying
    time.sleep(1) # Wait for telemetry info
    if self.alt > 2: # May be necessary to change if the drone takes off from a high ground
        current_alt = self.alt
        while True:
            # Then, check if the vehicle is not taking off
            if self.alt > current_alt + 0.0125*current_alt:
                # The vehicle is taking off
                if self.state == 'armed' or self.state == 'connected':
                    self.state = 'takingOff'
            else:
                # The vehicle is flying
                if self.state == 'armed' or self.state == 'connected':
                    self.state = 'flying'
                    self.flying_trigger()
                break
        # Change the mode to GUIDED
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
        arm_msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=False, timeout=3)
        print('- DroneLink: Mode changed to GUIDED')
        return True
    else:
        return False