import pymavlink.dialects.v20.all as dialect



def clear_Mission(self):
    # Clear all missions and waypoints
    self.vehicle.mav.mission_clear_all_send(self.vehicle.target_system, self.vehicle.target_component)
    print("- Geofence Controller: Previous missions and waypoints cleared successfully")

def enable_geofence(self):
    # Enable the geofence
    if self.get_parameter_trigger("FENCE_ENABLE", True) != 1:
        while True:
            # Modify the parameter value
            self.modify_parameter_trigger("FENCE_ENABLE", 1, True)
            # Get the parameter value
            if self.get_parameter_trigger("FENCE_ENABLE", True) == 1:
                print("- Geofence Controller: Geofence enabled successfully")
                # Break the loop
                break

            else:
                print("- Geofence Controller: Failed to enable GEOFENCE, trying again")

    else:
        # Geofence was already enabled
        print("- Geofence Controller: GEOFENCE is already enabled")

def disable_geofence(self):
    # Disable the geofence
    if self.get_parameter_trigger("FENCE_ENABLE", True) != 0:
        while True:
            # Modify the parameter value
            self.modify_parameter_trigger("FENCE_ENABLE", 0, True)
            # Get the parameter value
            if self.get_parameter_trigger("FENCE_ENABLE", True) == 0:
                print("- Geofence Controller: Geofence disabled successfully")
                # Break the loop
                break

            else:
                print("- Geofence Controller: Failed to disable GEOFENCE, trying again")

    else:
        # Geofence was already enabled
        print("- Geofence Controller: GEOFENCE is already disabled")

    print("- Geofence Controller: Completed!")

def set_fence_geofence(self, fence_list):
    # Set the geofence
    '''
    The fence_list must start and end with the same point to close the geofence, and the first point of the list must be the reference point.
    An example of a geofence list:
    fence_list = [(reference_lat, reference_lon), (lat1, lon1), (lat2, lon2), (lat3, lon3), (lat1, lon1)]
    '''
    # SET FENCE_TOTAL PARAMETER TO LENGTH OF FENCE LIST
    while True:

        # Modify the parameter value
        self.modify_parameter_trigger("FENCE_TOTAL", len(fence_list), True)
        # Get the parameter value
        if self.get_parameter_trigger("FENCE_TOTAL", True) == len(fence_list):
            print("- Geofence Controller FENCE_TOTAL set to {0} successfully".format(len(fence_list)))

            # Break the loop
            break

        else :
            print("- Geofence Controller: Failed to set FENCE_TOTAL to {0}, trying again".format(len(fence_list)))

    # SET THE FENCE BY SENDING FENCE_POINT MESSAGES
    # Initialize fence item index counter
    idx = 0

    # Run until all the fence items uploaded successfully
    while idx < len(fence_list):

        # Create FENCE_POINT message
        message = dialect.MAVLink_fence_point_message(target_system=self.vehicle.target_system,
                                                    target_component=self.vehicle.target_component,
                                                    idx=idx,
                                                    count=len(fence_list),
                                                    lat=fence_list[idx][0],
                                                    lng=fence_list[idx][1])

        # Send this message to vehicle
        self.vehicle.mav.send(message)

        # Create FENCE_FETCH_POINT message (this message is used to check if the fence point is uploaded successfully)
        message = dialect.MAVLink_fence_fetch_point_message(target_system=self.vehicle.target_system,
                                                            target_component=self.vehicle.target_component,
                                                            idx=idx)

        # Send this message to vehicle
        self.vehicle.mav.send(message)

        # Wait until receive FENCE_POINT message
        message = self.vehicle.recv_match(type=dialect.MAVLink_fence_point_message.msgname,
                                    blocking=True)

        # Convert the message to dictionary
        message = message.to_dict()

        # get the latitude and longitude from the fence item
        latitude = message["lat"]
        longitude = message["lng"]

        # Check the fence point is uploaded successfully
        if latitude != 0.0 and longitude != 0:
            # Print that the fence item uploaded successfully converting to string
            print("- Geofence Controller: Fence waypoint" + str(latitude) + " " + str(longitude) + " uploaded successfully")
            # Increase the index of the fence item
            idx += 1

    print("- Geofence Controller: All the fence items uploaded successfully")

def action_geofence(self, action):
    # Set the geofence action (0: Report, 1: RTL or Land, 2: Always Land, 3: Smart RTL or RTL or Land, 4: Brake or Land, 5: Smart RTL or Land)
    while True:
        # Modify the parameter value
        self.modify_parameter_trigger("FENCE_ACTION", int(action), True)
        # Get the parameter value
        if self.get_parameter_trigger("FENCE_ACTION", True) == int(action):
            print("- Geofence Controller: FENCE_ACTION set to value " + str(int(action)) + " successfully")
            # Break the loop
            break

        else :
            print("- Geofence Controller: Failed to set FENCE_ACTION to value " + str(int(action)) + ", trying again")
    
    print("- Geofence Controller: Completed!")












