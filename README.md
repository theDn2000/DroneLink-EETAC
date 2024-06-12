# DroneLink EETAC 

![logo](https://github.com/theDn2000/AutopilotServiceDEE_DCM/assets/109517814/18cc8967-327c-48f8-9cfc-2be24e8043ab)

## 📋 Content table
- [Introduction](#Introduction)
- [Installation](#Installation)
- [Contributions](#Contributions)
- [Use](#Use)
- [Examples](#Examples)

<a name="Introduction"></a>
## 📄 Introduction

**DroneLink EETAC** is a project designed to facilitate interaction with drones via the MAVLink protocol, providing robustness and scalability in controlling the autopilot and its cameras. This repository includes the main library **DroneLink EETAC**, an additional library for camera control called **CameraLink EETAC**, and three practical examples that demonstrate its versatility and application potential.

>[!NOTE]
>DroneLink EETAC is a complementary module of the Drone Engineering Ecosystem, a repository from the Castelldefels School of Telecommunications and Aerospace Engineering (EETAC).\
>\
> [![DroneEngineeringEcosystem Badge](https://img.shields.io/badge/DEE-MainRepo-brightgreen.svg)](https://github.com/dronsEETAC/DroneEngineeringEcosystemDEE)

In this file, you will find both installation instructions and a guide for using the libraries, as well as information on the operation and features of the examples.

<a name="Installation"></a>
## 📦 Installation and Requirements

>[!CAUTION]
>Before installing the project, make sure you have **Python 3.0 or higher**, which is essential for running the libraries. You can download it from [here](https://www.python.org/downloads/)

Clone the repository to your local machine using Git:

```
git clone https://github.com/theDn2000/DroneLink-EETAC.git
cd DroneLink-EETAC
```

Once you have the repository, download the dependencies from the *requirements.txt* file.

```
pip install -r requirements.txt
```

With this, you will be ready to use both the DroneLink EETAC library and the CameraLink EETAC library.

>[!WARNING]
>If you also want to use the examples included in this repository, you will need to have the latest version of the following tools:
>- **Mission Planner**: Essential for running the applications included in simulation mode. You can download it from [MissionPlanner](https://ardupilot.org/planner/docs/mission-planner-installation.html).
>- **Eclipse Mosquitto**: Broker required for the remote example in simulation mode. You can download it from [Mosquitto](https://mosquitto.org/download/)

<a name="Contributions"></a>
## 🤝 Contributions

This project is intended to grow from contributions both from the school and external sources. If you wish to contribute, follow the instructions below:

1. **Fork** the original repository:

   - Navigate to the [project's main page on GitHub](https://github.com/theDn2000/DroneLink-EETAC).
   - Click on the "Fork" button in the top right corner of the page.
   - This will create a copy of the repository in your GitHub account.
  
2. **Clone** your fork to your local machine:

   ```
   git clone https://github.com/your-username/repository-fork-name.git
   cd repository-fork-name
   ```

3. **Download** the dependencies from the *requirements.txt* file:
   ```
    pip install -r requirements.txt
    ```

4. Set up the original repository as an additional remote called **upstream**:

   ```
   git remote add upstream https://github.com/theDn2000/DroneLink-EETAC.git
   ```

5. Create a new **branch** to work on your version:

   ```
    git checkout -b your-branch-name
   ```

6. Before commiting, use the pre-commit tool for project verification:

   ```
    pre-commit run -a
   ```

Now you can make pull requests from your fork, and an administrator can merge your contributions into the main repository.
   
>[!NOTE]
>This video show an example of how you can contribute to the project\
>\
>[![DroneEngineeringEcosystem Badge](https://img.shields.io/badge/DEE-contributions-pink.svg)](https://www.youtube.com/watch?v=dv-k5MKjq8g)

>[!TIP]
>Installing [GitHub Desktop](https://desktop.github.com) is highly recommended to facilitate the previous steps.


<a name="Use"></a>
## 🚀 Use

### DroneLink EETAC

To make use of the DroneLink EETAC library, you must first import the Drone class into your project. The Drone class is defined in the file Drone.py.

```
from Drone import Drone
```

Once the library is imported, you can create a Drone object to use it. To do this, you should pass it the int ***id***, which is the identificator of that specific drone.

```
drone = Drone(id)
```

>[!TIP]
>The parameter drone.id allows you to differentiate drone-type objects, which leads you to interact with multiple vehicles at the same time. See [Dashboard Direct Multiple](#DDM) for more information.



With the Drone object created, you can call the functions of the Drone object as follows:

```
drone.function_name(parameter_1, parameter_2, etc)
```
Below is a table with all the functions available in DroneLink EETAC:

Function | Description | Parameter 1 | Parameter 2 | Parameter 3 | Response
--- | --- | --- | --- | --- | ---
*connect* | Stablishes the MAVLink connection with the autopilot of the drone | connection string [str] | baud rate (115200 by default) [int] | No | No
*get_position* | Get the position of the drone | No | No | No | latitude, longitude, altitude
*disconnect* | Closes the MAVLink connection with the autopilot of the drone | No | No | No | No
*send_telemetry_info* | Sends the telemetry info of the drone | callback (callback function to interpret the information) | No | No | No
*arm* | Arms the drone | No | No | No | No
*check_armed* | Checks if the vehicle is armed or not | No | No | No | True or False
*take_off* | Get the drone take off to reach the desired altitude | target altitude (in meters) [int] | No | No | No
*change_altitude* | Get the drone reach the desired altitude during flight | target altitude (in meters) [int] | No | No | No
*go_order* | Makes the drone go in a specific direction | direction ("North", "South", "East", "West", "NorthWest", "NorthEast", "SouthWest", "SouthEast", "Stop" [str]) | No | No | No
*check_flying* | Checks if the drone is flying | No | No | No | True or False
*goto* | Make the drone go to a specific waypoint | latitude [float] | longitude [float] | altitude [int] | No
*land* | Land the drone | No | No | No | No
*return_to_launch* | Go to the launch position and land | No | No | No | No
*uploadFlightPlan* | Upload a flight plan to the vehicle | waypoints_json (JSON string with the coordinates of the waypoints, check the function for more information about the format) | No | No | No
*executeFlightPlan* | Execute the flight plan previously uploaded | No | No | No | No
*set_fence_geofence* | Upload a geofence to the vehicle | fence_list (tuple list with the geofence points, check the function for more information about the format) | No | No | No
*enable_geofence* | Enable the geofence | No | No | No | No
*disable_geofence* | Disable the geofence | No | No | No | No
*action_geofence* | Set the action of the drone when trespassing the geofence | action (0: Report, 1: RTL or Land, 2: Always Land, 3: Smart RTL or RTL or Land, 4: Brake or Land, 5: Smart RTL or Land) [int]| No | No | No
*get_parameter* | Get the value of a parameter of the autopilot | param_name (name of the parameter) [str] | No | No | value of the parameter
*get_all_parameters* | Get all the parameters of the autopilot | No | No | No | list of parameters names, list of parameters values
*modify_parameter* | Modify a parameter of the autopilot | param_name (name of the parameter) [str] | param_value (value of the parameter) [float] | No | No

>[!NOTE]
>When send_telemetry_info is executed, the drone starts sending packets every 250 miliseconds. The service will stop sending telemetry_info packets as soon as the *disconnect* function is executed. This is an example of telemetry_info packet:
```
{
    'lat': 41.124567,
    'lon': 1.9889145,
    'heading': 270,
    'groundSpeed': 4.27,
    'altitude': 6.78,
    'battery': 80,
    'state': state
}
```

>[!IMPORTANT]
>In addition, the functions that allow it have an alternative version where we can choose whether we want them to be blocking or non-blocking:

Function | Description | Parameter 1 | Parameter 2 |  Parameter 3 | Parameter 4 | Response
--- | --- | --- | --- | --- | --- | ---
*connect_trigger* | Stablishes the MAVLink connection with the autopilot of the drone | connection string [str] | blocking (True or False) [bool] | baud rate (115200 by default) [int] | No | No
*send_telemetry_info_trigger* | Sends the telemetry info of the drone | callback (callback function to interpret the information) | blocking (True or False) [bool] | No | No | No
*arm_trigger* | Arms the drone | blocking (True or False) [bool] | No | No | No | No
*take_off_trigger* | Get the drone take off to reach the desired altitude | target altitude (in meters) [int] | blocking (True or False) [bool] | No | No | No
*change_altitude_trigger* | Get the drone reach the desired altitude during flight | target altitude (in meters) [int] | blocking (True or False) [bool] | No | No | No
*check_flying_trigger* | Checks if the drone is flying | blocking (True or False) [bool] | No | No | No | True or False
*goto_trigger* | Make the drone go to a specific waypoint | latitude [float] | longitude [float] | altitude [int] | blocking (True or False) [bool] | No
*land_trigger* | Land the drone | blocking (True or False) [bool] | No | No | No | No
*return_to_launch_trigger* | Go to the launch position and land | blocking (True or False) [bool] | No | No | No | No
*uploadFlightPlan_trigger* | Upload a flight plan to the vehicle | waypoints_json (JSON string with the coordinates of the waypoints, check the function for more information about the format) | blocking (True or False) [bool] | No | No | No
*executeFlightPlan_trigger* | Execute the flight plan previously uploaded | blocking (True or False) [bool] | No | No | No | No
*get_parameter_trigger* | Get the value of a parameter of the autopilot | param_name (name of the parameter) [str] | blocking (True or False) [bool] | No | No | value of the parameter
*get_all_parameters_trigger* | Get all the parameters of the autopilot | blocking (True or False) [bool] | No | No | No | list of parameters names, list of parameters values
*modify_parameter_trigger* | Modify a parameter of the autopilot | param_name (name of the parameter) [str] | param_value (value of the parameter) [float] | blocking (True or False) [bool] | No | No


The drone object has a parameter called **state**, which is modified depending on which functions are executed. The possible values of drone.state are the following:

- connected
- armed
- takingOff
- changingAltitude
- flying
- returningHome
- landing
- onMission

### CameraLink EETAC

To use the CameraLink EETAC library, you first need to import the Camera class into your project. The Camera class is defined in the file Camera.py.

```
from Camera import Camera
```

Once the library is imported, you can create a Camera object to use it. To do this, you should pass it the int ***id***, which is the identifier of that specific camera.

```
camera = Camera(id)
```

With the Camera object created, you can call the functions of the Camera object as follows:

```
camera.function_name(parameter_1, parameter_2, etc)
```
Below is a table with all the functions available in CameraLink EETAC:

Function | Description | Parameter 1 | Parameter 2 | Parameter 3 | Response
--- | --- | --- | --- | --- | ---
*take_picture* | Take a picture using the camera | No | No | No | jpg_as_text (image encoded in base64)
*start_video_stream* | Start video stream using the camera | callback (callback function to interpret every frame) | No | No | No
*stop_video_stream* | Stop video stream  | No | No | No | No

<a name="Examples"></a>
## 🛠️ Examples

### Dashboard Direct
![image](https://github.com/theDn2000/AutopilotServiceDEE_DCM/assets/109517814/60ae827a-ad67-4943-9d87-3bba951b0288)
![image](https://github.com/theDn2000/AutopilotServiceDEE_DCM/assets/109517814/15f7517a-1417-4039-bca9-9259f4c49416)

Dashboard Direct is a tool that allows you to interact with the autopilot directly. You can connect to the Mission Planner simulator or directly to the drone through three connection methods: Telemetry Radio, MAVProxy, or Raspberry Pi integrated into the vehicle.
>[!NOTE]
>Dashboard Direct creates a Drone object with the id that you select before connecting. This application combines the frontend for the user with the backend, calling directly the functions of DroneLink EETAC and CameraLink EETAC.

Dashboard Direct offer the following functionalities:
- **Basic drone controls**: Arm the drone, take off, change altitude, move, land and RTL.
- **Position and telemetry information**: Displayed drone position in map, altitude, heading, ground speed and battery.
- **Parameters tab**: Display the value of a parameter of the Autopilot, or modify it.
- **Mission tab**: Create waypoints by right-clicking on the map, upload the flight plan, execute the flight plan or clear the waypoints.
- **Geofence tab**: Create vertex points by right-clicking on the map to define a polygon, upload the polygon to the autopilot geofence, enable the geofence, disable the geofence, change the geofence action or clear the vertex points.
- **Camera display**: Take pictures or stream video using the local camera.

<a name="DDM"></a>
### Dashboard Direct Multiple
![image](https://github.com/theDn2000/AutopilotServiceDEE_DCM/assets/109517814/d1c607d3-5af2-4ff9-b4f1-36e5c6408193)
![image](https://github.com/theDn2000/AutopilotServiceDEE_DCM/assets/109517814/59034b5f-b7f8-4551-a110-de80d8b63ffe)

Dashboard Direct Multiple is a test tool that allows you to control several drones simultaneously (10 maximum). Before connecting, you have to select the swarm size and the connection type (simulation or real). 

Dashboard Direct Multiple creates multiple Drone objects and store them in a list. Then, uses the drone.id variables to execute orders to the selected drone.

Dashboard Direct Multiple offer the following functionalities:
- **Drone Selector**: A selection bar to determine the drone that you want to control when pressing every button.
- **Basic drone controls**: Arm the drone, take off, change altitude, move, land and RTL.
- **Multiple drone control**: Arm all the drones at the same time, take off all the drones at the same time.
- **Position and telemetry information**: Displayed drones position on map, altitude, heading, ground speed and battery.

### Dashboard Remote + Autopilot Service + Camera Service

![image](https://github.com/theDn2000/AutopilotServiceDEE_DCM/assets/109517814/e2756b0a-a054-4c13-8484-05266ea38d9c)


This set of files enables remote communication with the drone from any device that can run the Dashboard Remote application and has an internet connection. For this, the scripts *AutopilotService.py* and *CameraService.py* are executed on the onboard computer of the vehicle (in this case, the Raspberry Pi), while Dashboard Remote is run from an external device. All three files subscribe to an external broker chosen by the user once they are started, allowing the sending and receiving of messages from a distance.

>[!CAUTION]
>The device in which the services are being executed must have a mosquitto broker running on port 1884.
>1. Create a *mosquitto1884.conf* file with the following lines:
```
      listener 1884
      allow_anonymous true
```
>   2. Start the broker with the following command:
```
      mosquitto -v -c mosquitto1884.conf
```


To run any of the services on the drone’s Raspberry Pi, you should execute the following commands:

- **For AutopilotService**:

```
python3 AutopilotService.py id global/local simulation/production broker

# Where "id" is the identificator number of the drone and broker can be "hivemq", "hivemq_cert" (requires certificate) and "classpip_cred" (requires credentials) 
```

- **For CameraService**:

```
python3 CameraService.py id global/local simulation/production broker

# Where "id" is the identificator number of the camera and broker can be "hivemq", "hivemq_cert" (requires certificate) and "classpip_cred" (requires credentials) 
```

When a button is pressed in the Dashboard Remote application, a message is published to the broker in the following format:

- **Sending messages to AutopilotService**: 

```
message = "DashboardRemote/AutopilotService/command/drone_id"
self.client.publish(message, body)
# Where the body variable depends on the message (some messages don't use the body field)
```

Depending on the command sent to the service, it triggers the corresponding function of the DroneLink EETAC library. The possible commands are the following: 

![image](https://github.com/theDn2000/AutopilotServiceDEE_DCM/assets/109517814/7123fb35-b93d-4157-9283-8abef393a649)

>[!NOTE]
>For more information about this service, it is recommended to check the AutopilotService.py file.

- **Sending messages to CameraService**: 

```
message = "DashboardRemote/CameraService/command/camera_id"
self.client.publish(message, body)
# Where the body variable depends on the message (some messages don't use the body field)
```
Depending on the command sent to the service, it triggers the corresponding function of the CameraLink EETAC library. The possible commands are the following: 

![image](https://github.com/theDn2000/AutopilotServiceDEE_DCM/assets/109517814/883b3c35-aa68-47f1-8a9f-ee5f07b7f0f9)

>[!NOTE]
>For more information about this service, it is recommended to check the CameraService.py file.

The onboard services will also publish responses to the broker, but this time directed to the Dashboard Remote application, which will process the information and display it on the screen.

- **Sending messages to Dashboard Remote**: 

```
message = "origin/DashboardRemote/command/service_id"
self.client.publish(message, body)
# Where the body variable depends on the message (some messages don't use the body field)
```
Depending on the command sent to the dashboard, the visual updates of the application are different. The possible commands are the following:

![image](https://github.com/theDn2000/AutopilotServiceDEE_DCM/assets/109517814/44edef4b-276f-4cbd-bc13-cde5863c0b2e)

Dashboard Remote offer the following functionalities:
- **Basic drone controls**: Arm the drone, take off, change altitude, move, land and RTL.
- **Position and telemetry information**: Displayed drone position in map, altitude, heading, ground speed and battery.
- **Parameters tab**: Display the value of a parameter of the Autopilot, or modify it.
- **Mission tab**: Create waypoints by right-clicking on the map, upload the flight plan, execute the flight plan or clear the waypoints.
- **Geofence tab**: Create vertex points by right-clicking on the map to define a polygon, upload the polygon to the autopilot geofence, enable the geofence, disable the geofence, change the geofence action or clear the vertex points.
- **Camera display**: Take pictures or stream video using the camera of the drone and display it in the dashboard (via websockets or broker).

>[!IMPORTANT]
>The last update of the repository adds the posibility to send the video stream from the CameraService script to Dashboard Remote via **websockets** in addition to via broker. To make this connection possible, CameraService,py and DashboardRemote.py must run on devices **connected to the same network**.


