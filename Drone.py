import threading
import pymavlink
from pymavlink.mavutil import default_native
import pymavlink.dialects.v20.all as dialect


class Drone(object):
    def __init__(self, ID):
        self.ID = ID # ID of the drone
        self.vehicle = None # MAVLink connection to the drone
        self.lock = threading.Lock()  # Locking to avoid conflicts between threads
        self.direction = "init" # Initial direction of the drone
        self.state = "disconnected" # Initial state of the drone
        ''' other possible states are:
            connected
            armed
            takingOff
            changingAltitude
            flying
            returningHome
            landing
            onMission
        '''
        self.lat = 0 # Latitude of the drone
        self.lon = 0 # Longitude of the drone
        self.alt = 0 # Altitude of the drone

        
        self.sending_telemetry_info = False # Flag to send telemetry information
        self.going = False  # Flag to indicate that the drone is going to a direction (North, South, East, West, Up, Down)
        self.reaching_waypoint = False # Flag to indicate that the drone is reaching a waypoint (Mission and Goto)


    '''
    Here the methods of the Dron class are imported, which are organized into files.
    This way, future students who need to incorporate new services for their applications could organize their contributions.
    They would create a file with their new methods and import it here.
    '''

    from functions.connect_func import connect, connect_trigger, disconnect
    from functions.telemetry_info_func import send_telemetry_info, send_telemetry_info_trigger, get_telemetry_info, get_position
    from functions.arm_func import arm, arm_trigger, check_armed, check_armed_on_loop
    from functions.take_off_func import take_off, take_off_trigger
    from functions.altitude_func import change_altitude, change_altitude_trigger
    from functions.land_func import land, land_trigger
    from functions.return_to_launch_func import return_to_launch, return_to_launch_trigger
    from functions.flying_func import flying, flying_trigger, prepare_command, go_order, check_flying_trigger, check_flying
    from functions.goto_func import goto, goto_trigger, distanceInMeters
    from functions.geofence import clear_Mission, enable_geofence, disable_geofence, set_fence_geofence, action_geofence
    from functions.modify_parameters import modify_parameter, modify_parameter_trigger, get_parameter, get_parameter_trigger, get_all_parameters, get_all_parameters_trigger
    from functions.mission import uploadFlightPlan, uploadFlightPlan_trigger, executeFlightPlan, executeFlightPlan_trigger