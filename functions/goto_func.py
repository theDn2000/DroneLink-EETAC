import math
import threading
import time
from pymavlink import mavutil



def goto_trigger(self, lat, lon, alt, blocking=False):
    # Go to a waypoint trigger function (blocking or non-blocking)
    print('- DroneLink: Going to the waypoint')
    if blocking:
        goto(self, lat, lon, alt)
    else:
        w = threading.Thread(target=self.goto, args=[lat, lon, alt])
        w.start()

def goto(self, lat, lon, alt):
    # Go to a waypoint main function
    self.reaching_waypoint = True
    self.vehicle.mav.send(
        mavutil.mavlink.MAVLink_set_position_target_global_int_message(10, self.vehicle.target_system,
                                                                       self.vehicle.target_component,
                                                                       mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                                                       int(0b110111111000), int(lat * 10 ** 7),
                                                                       int(lon * 10 ** 7), alt, 0, 0, 0, 0, 0, 0, 0,
                                                                       0))
    
    # Wait until the drone is close to the waypoint
    dist = self.distanceInMeters(self.lat, self.lon, lat ,lon)
    distanceThreshold = 0.5
    while dist > distanceThreshold:
        time.sleep(0.25)
        dist = self.distanceInMeters(self.lat, self.lon, lat ,lon)
    print('- DroneLink: Waypoint reached')
    self.reaching_waypoint = False
    
def distanceInMeters(self, lat1, lon1, lat2, lon2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = lat2 - lat1
    dlong = lon2 - lon1
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5
