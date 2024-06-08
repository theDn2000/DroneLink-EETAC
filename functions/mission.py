import pymavlink.dialects.v20.all as dialect
from pymavlink import mavutil
import pymavlink.mavutil as utility
import threading
import json



def uploadFlightPlan(self, waypoints_json):
    # Upload a flight plan to the vehicle
    '''
    A mission is a set of waypoints that the vehicle will follow, from taking off to landing. 
    This function uploads a mission to the vehicle. 

    The waypoints_json parameter is a JSON string with the following format:
    {
    "coordinates": [
        {"lat": 47.6205, "lon": -122.3493, "alt": 100},  // Coordinate 1
        {"lat": 47.6153, "lon": -122.3448, "alt": 150},  // Coordinate 2
        {"lat": 47.6102, "lon": -122.3425, "alt": 200}   // Coordinate 3
    ]
    }
    '''
    waypoint_loader = []

    # Load the JSON file
    waypoints_json = json.loads(waypoints_json)

    # Count the number of waypoints
    n = len(waypoints_json['coordinates'])

    # The first waypoint is the home location, we can obtain it from the vehicle and add it to the mission
    self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component, mavutil.mavlink.MAV_CMD_GET_HOME_POSITION, 0, 0, 0, 0, 0, 0, 0, 0)
    
    msg = self.vehicle.recv_match(type='HOME_POSITION', blocking=True)
    msg = msg.to_dict()
    latitude_home = msg['latitude']
    longitude_home = msg['longitude']
    altitude_home = 0 # The drone will take off from the ground
    print (f'- Mission Controller: Home position: {latitude_home}, {longitude_home}, {altitude_home}')

    # Add the home waypoint to the mission
    waypoint_loader.append(utility.mavlink.MAVLink_mission_item_int_message(self.vehicle.target_system,                           # Target system
                                       self.vehicle.target_component,                                                                # Target component
                                       0,                                                                # Sequence number (0 is the home waypoint)
                                       0,                                                                # Frame
                                       16,                                                               # Command
                                       0,                                                                # Current
                                       0,                                                                # Autocontinue
                                       0,                                                                # Param 1
                                       0,                                                                # Param 2
                                       0,                                                                # Param 3
                                       0,                                                                # Param 4
                                       latitude_home,                                                    # Param 5 (Latitude)
                                       longitude_home,                                                   # Param 6 (Longitude)
                                       altitude_home))                                                   # Param 7 (Altitude)
    print("- Mission Controller: Home waypoint added to the waypoint loader")

    # Add the takeoff waypoint to the mission
    waypoint_loader.append(utility.mavlink.MAVLink_mission_item_int_message(self.vehicle.target_system,   # Target system
                                        self.vehicle.target_component,                                    # Target component
                                        1,                                                                # Sequence number (1 is the takeoff waypoint)
                                        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,                    # Frame
                                        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,                              # Command
                                        0,                                                                # Current
                                        True,                                                             # Autocontinue
                                        0,                                                                # Param 1
                                        0,                                                                # Param 2
                                        0,                                                                # Param 3
                                        0,                                                                # Param 4
                                        latitude_home,                                                    # Param 5 (Latitude)
                                        longitude_home,                                                   # Param 6 (Longitude)
                                        waypoints_json['coordinates'][0]['alt']))                        # Param 7 (Altitude)
    print("- Mission Controller: Takeoff waypoint added to the waypoint loader")

    # Add the route waypoints to the mission
    sequence = 2
    for waypoint in waypoints_json['coordinates']:
        latitude = int(waypoint['lat']*10**7)
        longitude = int(waypoint['lon']*10**7)
        altitude = float(waypoint['alt'])

        # Add the waypoint
        waypoint_loader.append(utility.mavlink.MAVLink_mission_item_int_message(self.vehicle.target_system,  # Target system
                                           self.vehicle.target_component,                                    # Target component
                                           sequence,                                                         # Sequence number
                                           mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,                    # Frame
                                           mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,                             # Command
                                           0,                                                                # Current
                                           True,                                                             # Autocontinue
                                           0,                                                                # Param 1
                                           0,                                                                # Param 2
                                           0,                                                                # Param 3
                                           0,                                                                # Param 4
                                           latitude,                                                         # Param 5 (Latitude)
                                           longitude,                                                        # Param 6 (Longitude)
                                           altitude))                                                        # Param 7 (Altitude)
        sequence += 1

    # Add a RTL command to the mission to end the mission
    waypoint_loader.append(utility.mavlink.MAVLink_mission_item_int_message(self.vehicle.target_system,   # Target system
                                        self.vehicle.target_component,                                    # Target component
                                        sequence,                                                         # Sequence number
                                        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,                    # Frame
                                        mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,                     # Command
                                        0,                                                                # Current
                                        True,                                                             # Autocontinue
                                        0,                                                                # Param 1
                                        0,                                                                # Param 2
                                        0,                                                                # Param 3
                                        0,                                                                # Param 4
                                        0,                                                                # Param 5 (Latitude)
                                        0,                                                                # Param 6 (Longitude)
                                        0))                                                               # Param 7 (Altitude)
    print ("- Mission Controller: RTL command added to the waypoint loader")

    # Delete all previous missions and waypoints
    #self.vehicle.mav.mission_clear_all_send(self.vehicle.target_system, self.vehicle.target_component)
    self.vehicle.waypoint_count_send(0)
    
    # Recieve the ACK
    ack = self.vehicle.recv_match(type='MISSION_ACK', blocking=True)
    print("- Mission Controller: Previous mission cleared")

    # Send the number of waypoints
    self.vehicle.waypoint_count_send(len(waypoint_loader))

    # Send all the items
    for i in range(0, len(waypoint_loader)):
        # Wait for the ACK [MISSION_REQUEST_INT]
        ack = self.vehicle.recv_match(type=['MISSION_REQUEST_INT', 'MISSION_REQUEST'], blocking=True)
        print ("- Mission Controller: Requesting waypoint" + str(ack.seq)) 
        try:
            print(f'- Mission Controller: Sending waypoint {ack.seq}/{len(waypoint_loader) - 1}: {waypoint_loader[ack.seq]}')
            self.vehicle.mav.send(waypoint_loader[ack.seq])
        except Exception as e: 
            print("- Mission Controller: Error sending waypoint")
        # Wait 2 seconds before sending the next waypoint
        #time.sleep(2)



        # Break the loop if the last waypoint was sent´
        if ack.seq == len(waypoint_loader) - 1:
            break
                                        
    # Wait for the ACK [MISSION_ACK]
    ack = self.vehicle.recv_match(type='MISSION_ACK', blocking=True)

    # Send feedback to the user
    print('- Mission Controller: Flight plan uploaded!')
    
def uploadFlightPlan_trigger(self, waypoints_json, blocking=False):
    # Upload flight plan trigger function (blocking or non-blocking)
    if blocking:
        uploadFlightPlan(self, waypoints_json)
    else:
        w = threading.Thread(target=uploadFlightPlan, args=[self, waypoints_json])
        w.start()

def executeFlightPlan(self):
    # Execute a flight plan previously uploaded to the vehicle

    # Set the vehicle to guided mode
    mode = 'GUIDED'

    mode_id = self.vehicle.mode_mapping()[mode]
    self.vehicle.mav.set_mode_send(
        self.vehicle.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id)
    arm_msg = self.vehicle.recv_match(type='COMMAND_ACK', blocking=True)

    # Arm the vehicle
    self.arm_trigger(True)

    # Set the state to "onMission"
    self.state = "onMission"

    # Start the mission
    self.vehicle.mav.command_long_send(self.vehicle.target_system, self.vehicle.target_component, mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0, 0, 0, 0)
    print('- Mission Controller: Mission started')

def executeFlightPlan_trigger(self, blocking=False):
    # Execute flight plan trigger function (blocking or non-blocking)
    if blocking:
        executeFlightPlan(self)
    else:
        w = threading.Thread(target=executeFlightPlan, args=[self])
        w.start()