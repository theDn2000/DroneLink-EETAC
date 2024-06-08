import pymavlink.dialects.v20.all as dialect
from pymavlink import mavutil
import threading



def modify_parameter_trigger(self, param_name, param_value, blocking=False):
    # Trigger the modification of a parameter (blocking or non-blocking)
    if blocking:
        modify_parameter(self, param_name, param_value)
    else:
        w = threading.Thread(target=modify_parameter, args=[self, param_name, param_value])
        w.start()

def modify_parameter(self, param_name, param_value):
    # Change the parameter value
    try:
        # If the parameter value cannot be converted to a float, return an error
        param_value = float(param_value)
        msg = self.vehicle.mav.param_set_encode(
        self.vehicle.target_system, self.vehicle.target_component,
        param_name.encode(encoding="utf-8"), param_value, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
    except ValueError:
        print('- DroneLink: The parameter value must be a number')

    
    self.vehicle.mav.send(msg)

def get_parameter_trigger(self, param_name, blocking=False):
    # Trigger the get of a parameter (blocking or non-blocking)
    if blocking:
        return get_parameter(self, param_name)
    else:
        w = threading.Thread(target=get_parameter, args=[self, param_name])
        w.start()

def get_parameter(self, param_name):
    # Get the value of a parameter
    msg = self.vehicle.mav.param_request_read_encode(
        self.vehicle.target_system, self.vehicle.target_component,
        param_name.encode(encoding="utf-8"), -1)
    
    self.vehicle.mav.send(msg)

    # Wait for a response (blocking)
    response = self.vehicle.recv_match(type='PARAM_VALUE', blocking=True)
    # Return the value of the parameter
    return response.param_value
    
def  get_all_parameters_trigger(self, blocking=False):
    # Trigger the get of all parameters (blocking or non-blocking)
    if blocking:
        return get_all_parameters(self)
    else:
        w = threading.Thread(target=get_all_parameters, args=[self])
        w.start()

def get_all_parameters(self):
    # Get all the parameters
    msg = self.vehicle.mav.param_request_list_encode(
        self.vehicle.target_system, mavutil.mavlink.MAV_COMP_ID_ALL)
    
    self.vehicle.mav.send(msg)

    # Create a list with all the parameters
    parameters_id = []
    parameters_value = []
    while True:
        response = self.vehicle.recv_match(type='PARAM_VALUE', blocking=True)
        if response.param_count == response.param_index + 1:

            break
        parameters_id.append(response.param_id)
        parameters_value.append(response.param_value)
    return parameters_id, parameters_value


