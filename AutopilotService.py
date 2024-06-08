import paho.mqtt.client as mqtt
from paho.mqtt.client import ssl
import json
import os
import sys

sys.path.append(os.path.abspath('../../..'))

from Drone import Drone as Dron

'''
These are the different values for the state of the autopilot:
    'connected' (only when connected the telemetry_info packet will be sent every 250 miliseconds)
    'armed'
    'takingOff'
    'changingAltitude'
    'flying'
    'returningHome'
    'landing'
    'onMission'

The autopilot can also be 'disconnected' but this state will never appear in the telemetry_info packet 
when disconnected the service will not send any packet
'''


def process_message(message, client):
    global vehicle
    global direction
    global go
    global sending_telemetry_info
    global sending_topic
    global op_mode
    global sending_topic
    global state
    global dron

    splited = message.topic.split("/")
    origin = splited[0]
    command = splited[2]
    drone_id = int(splited[3])
    sending_topic = "AutopilotService/" + origin

    if command == "connect":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # The connection ports are the following [10 possible drones]:
            ports = [5763, 5773, 5783, 5793, 5803, 5813, 5823, 5833, 5843, 5853]
            # Create the drone object
            dron = Dron(drone_id)
            # depending on the drone_id and operation mode, the port will be different
            print('Drone ID: ', drone_id)
            if operation_mode == 'simulation':
                connection_string = "tcp:127.0.0.1:" + str(ports[int(drone_id) - 1])
            elif operation_mode == 'production':
                connection_string = "/dev/ttyS0" # The program is being executed in a Raspberry Pi
            else:
                print('Operation mode not recognized')
            # Connect the drone
            dron.connect_trigger(connection_string, True)

            # If connect is OK, initialize the telemetry data
            if dron.state == 'connected':
                print('- Autopilot Service: Starting to send telemetry info')
                print ('- Autopilot Service: Vehicle connected' + origin)
                dron.send_telemetry_info_trigger(process_output, False)

                # Disable geofence by default
                dron.disable_geofence()

                # Check if the vehicle is armed
                dron.check_armed()
                # Check if the vehicle is flying (only if it is not connected nor disarmed)
                if dron.state != "connected" and dron.state != "disconnected":
                    dron.check_flying_trigger(False)

    if command == "disconnect":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Disconnect the drone
            if dron.state != 'disconnected':
                dron.disconnect()
            else:
                print('- Autopilot Service: Vehicle is already disconnected')

    if command == "armDrone":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Arm the drone
            if dron.state == 'connected':
                dron.arm_trigger(False)
                print("- Autopilot Service: Vehicle armed")
            else:
                print('- Autopilot Service: The vehicle is not armable as it is not connected')

        # the vehicle will disarm automatically is takeOff does not come soon, the arm function does this automatically

    if command == "takeOff":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            if dron.state == 'armed':
                atargetAltitude = int(message.payload.decode("utf-8"))
                print("- Autopilot Service: Vehicle taking off")
                dron.take_off_trigger(atargetAltitude, False)
                print("- Autopilot Service: Vehicle reached target altitude")
            else:
                print('- Autopilot Service: Vehicle not armed')

        if dron.state == 'flying':
            # Enable flying trigger if the vehicle is flying
            dron.flying_trigger()

    if command == "changeAltitude":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Change the altitude
            if dron.state == 'flying':
                dron.change_altitude_trigger(int(message.payload.decode("utf-8")), False)
                print('- AutopilotService: Altitude changing to ' + message.payload.decode("utf-8") + ' meters')
            else:
                print('- Autopilot Service: Vehicle not flying')

    if command == "returnToLaunch":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            if dron.state == 'flying':
                # Return to launch
                dron.return_to_launch_trigger(False)
            else:
                print('- AutopilotService: Vehicle not flying')

    if command == "getParameter":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Get the parameter value
            if dron.state != 'disconnected':
                parameter_value = dron.get_parameter_trigger(message.payload.decode("utf-8"), True)
                # Publish the parameter value to return it to the client
                client.publish(sending_topic + '/getParameterResponse/' + str(drone_id), parameter_value)
                print('- Autopilot Service: Message sent')
            else:
                print('- Autopilot Service: Vehicle not connected')

    if command == "setParameter":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Set the parameter value
            if dron.state != 'disconnected':
                message_splited = message.payload.decode("utf-8").split("/")
                parameter_id = message_splited[0]
                try:
                    parameter_value = float(message_splited[1])
                    dron.modify_parameter_trigger(parameter_id, parameter_value, True)
                    print("- Autopilot Service: Parameter " + parameter_id + " set to " + str(parameter_value))
                except ValueError:
                    print("- Autopilot Service: The parameter value must be a number")

            else:
                print('- Autopilot Service: Vehicle not connected')
    
    if command == "goto":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            if dron.state == 'flying':
                message_splited = message.payload.decode("utf-8").split("/")
                coords = [float(message_splited[0]), float(message_splited[1])]
                dron.goto_trigger(coords[0], coords[1], dron.alt, False)
                print('- AutopilotService: Going to the waypoint')
            else:
                print('- Autopilot Service: Vehicle not flying')

    if command == "land":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            if dron.state == 'flying':
                # Land the drone
                dron.land_trigger(False)

            else:
                print('- AutopilotService: Vehicle not flying')

    if command == "go":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Go to the specified direction
            if dron.state == 'flying':
                dron.go_order(message.payload.decode("utf-8"))
            else:
                print('-AutopilotService: Vehicle is not flying')

    if command == "uploadFlightPlan":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Upload the flight plan
            if dron.state == 'connected':
                # message is a json string, convert it to a dictionary
                message = str(message.payload.decode("utf-8"))
                dron.uploadFlightPlan((message))
            else:
                print('- AutopilotService: Vehicle should be connected and disarmed to upload a flight plan')

    if command == "executeFlightPlan":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Execute the flight plan
            if dron.state == 'connected':
                dron.executeFlightPlan_trigger(False)
            else:
                print('- AutopilotService: Vehicle should be connected and disarmed to execute a flight plan')

    if command == "disableGeofence":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Disable the geofence
            if dron.state != 'disconnected':
                dron.disable_geofence()
                print('- AutopilotService: Geofence disabled')
            else:
                print('- Autopilot Service: Vehicle not connected')

    if command == "enableGeofence":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Enable the geofence
            if dron.state != 'disconnected':
                dron.enable_geofence()
                print('- AutopilotService: Geofence enabled')
            else:
                print('- Autopilot Service: Vehicle not connected')

    if command == "uploadGeofence":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Upload the geofence
            if dron.state != 'disconnected':
                # message is a json string, convert it to a dictionary

                message = json.loads(message.payload.decode("utf-8"))

                dron.set_fence_geofence(message)
                print('- AutopilotService: Geofence uploaded')
            else:
                print('- Autopilot Service: Vehicle not connected')

    if command == "actionGeofence":
        # Check if the drone is the requested one
        drone_id = int(splited[3])
        if service_id == drone_id:
            print('- Autopilot Service: Received "' + command +'".')
            # Action the geofence
            if dron.state != 'disconnected':
                dron.action_geofence(int(message.payload.decode("utf-8")))
                print('- AutopilotService: Geofence action changed to ' + message.payload.decode("utf-8"))
            else:
                print('- Autopilot Service: Vehicle not connected')


def on_internal_message(client, userdata, message):
    global internal_client
    process_message(message, internal_client)

def on_external_message(client, userdata, message):
    global external_client
    process_message(message, external_client)

def on_connect(external_client, userdata, flags, rc):
    if rc == 0:
        print("- Autopilot Service: Connection OK")
    else:
        print("- Autopilot Service: Bad connection")

def process_output(telemetry_info, drone_id):
    # Callback function to send the telemetry_info packet
    external_client.publish(sending_topic + '/telemetryInfo/' + str(drone_id), json.dumps(telemetry_info))

def AutopilotService(connection_mode, operation_mode, external_broker, username, password, internal_client, external_client):
    global op_mode
    global state

    print('- Autopilot Service: Connection mode: ', connection_mode)
    print('- Autopilot Service: Operation mode: ', operation_mode)
    op_mode = operation_mode

    if connection_mode == "global":
        if external_broker == "hivemq":
            external_client.connect("broker.hivemq.com", 8000)
            print('- Autopilot Service: Connected to broker.hivemq.com:8000')

        elif external_broker == "hivemq_cert":
            external_client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
            external_client.connect("broker.hivemq.com", 8884)
            print('- Autopilot Service: Connected to broker.hivemq.com:8884')

        elif external_broker == "classpip_cred":
            external_client.username_pw_set(
                username, password
            )
            external_client.connect("classpip.upc.edu", 8000)
            print('- Autopilot Service: Connected to classpip.upc.edu:8000')

        elif external_broker == "classpip_cert":
            external_client.username_pw_set(
                username, password
            )
            external_client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
                                    tls_version=ssl.PROTOCOL_TLS, ciphers=None)
            external_client.connect("classpip.upc.edu", 8883)
            print('- Autopilot Service: Connected to classpip.upc.edu:8883')
        elif external_broker == "localhost":
            external_client.connect("localhost", 8000)
            print('- Autopilot Service: Connected to localhost:8000')
        elif external_broker == "localhost_cert":
            print('- Autopilot Service: Not implemented yet')

    elif connection_mode == "local":
        if operation_mode == "simulation":
            external_client.connect("localhost", 8000)
            print('- Autopilot Service: Connected to localhost:8000')
        else:
            external_client.connect("10.10.10.1", 8000)
            print('- Autopilot Service: Connected to 10.10.10.1:8000')

    print("- Autopilot Service: Waiting....")
    external_client.subscribe("+/AutopilotService/#", 2)
    external_client.subscribe("cameraService/+/#", 2)
    internal_client.subscribe("+/AutopilotService/#")
    internal_client.loop_start()
    if operation_mode == 'simulation':
        external_client.loop_forever()
    else:
        # external_client.loop_start() #when executed on board use loop_start instead of loop_forever
        external_client.loop_forever()



if __name__ == '__main__':
    import sys

    # Inicialize the drone object (defined in the connect function)
    dron = None

    # Initialization variables
    service_id = int(sys.argv[1]) # ID of the drone in which the service is running
    connection_mode = sys.argv[2]  # global or local
    operation_mode = sys.argv[3]  # simulation or production
    

    username = None
    password = None
    if connection_mode == 'global':
        external_broker = sys.argv[4]
        if external_broker == 'classpip_cred' or external_broker == 'classpip_cert':
            username = sys.argv[5]
            password = sys.argv[6]
    else:
        external_broker = None

    # Broker interno:
    internal_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Autopilot_internal")
    internal_client.on_message = on_internal_message
    # internal_client.connect("192.168.208.2", 1884)
    internal_client.connect("localhost", 1884)

    # Broker externo:
    external_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Autopilot_external", transport="websockets")
    external_client.on_message = on_external_message
    external_client.on_connect = on_connect

    AutopilotService(connection_mode, operation_mode, external_broker, username, password, internal_client,
                     external_client)
