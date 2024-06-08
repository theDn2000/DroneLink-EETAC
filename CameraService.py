import ssl
import cv2 as cv # OpenCV 
from Camera import Camera
import paho.mqtt.client as mqtt
import threading
import websockets
import asyncio
import queue
import socket


def process_message(message,   client):

    global sending_video_stream
    global sending_video_for_calibration
    global finding_colors
    global origin
    global cap

    splited = message.topic.split("/")
    origin = splited[0]
    command = splited[2]
    camera_id = splited[3]

    if command == "takePicture":
        # Check if the camera is the requested one
        if service_id == camera_id:
            print('- Camera Service: Received "' + command +'".')
            # Take a picture
            jpg_as_text = camera.take_picture()
            # Publish the image to the broker
            client.publish("CameraService/" + origin + "/picture/" + str(camera_id), jpg_as_text)

    if command == "startVideoStream":
        # Check if the camera is the requested one
        if service_id == camera_id:
            print('- Camera Service: Received "' + command +'".')
            # Start the video stream
            camera.start_video_stream(callback_broker)

    if command == "stopVideoStream":
        # Check if the camera is the requested one
        if service_id == camera_id:
            print('- Camera Service: Received "' + command +'".')
            # Stop the video stream
            camera.stop_video_stream()

    if command == "getCameraIP":
        # Check if the camera is the requested one
        if service_id == camera_id:
            print('- Camera Service: Received "' + command +'".')
            # Get the IP of the camera
            ip = get_ip()
            print("- Camera Service: IP: ", ip)
            # Publish the IP to the broker
            client.publish("CameraService/" + origin + "/getCameraIP/" + str(camera_id), str(ip))




def callback_broker(jpg_as_text):
    # Publish the image to the broker (for video streaming)
    external_client.publish("CameraService/" + origin + "/picture/" + str(service_id), jpg_as_text)

def on_internal_message(client, userdata, message):
    print("- Camera Service: Received internal ", message.topic)
    global internal_client
    process_message(message, internal_client)

def on_external_message(client, userdata, message):
    print("- Camera Service: Received external ", message.topic)

    global external_client
    process_message(message, external_client)

def on_connect(external_client, userdata, flags, rc):
    if rc == 0:
        print("- Camera Service: Connection OK")
    else:
        print("- Camera Service: Bad connection")

def CameraService(connection_mode, operation_mode, external_broker, username, password):
    global op_mode
    global external_client
    global internal_client
    global cap
    global colorDetector

    cap = cv.VideoCapture(0)  # video capture source camera (Here webcam of lap>

    print("- Camera Service: Camera ready")

    print("- Camera Service: Connection mode: ", connection_mode)
    print("- Camera Service: Operation mode: ", operation_mode)
    op_mode = operation_mode

    print("- Camera Service: Connection mode: ", connection_mode)
    print("- Camera Service: Operation mode: ", operation_mode)
    op_mode = operation_mode



    if connection_mode == "global":
        if external_broker == "hivemq":
            external_client.connect("broker.hivemq.com", 8000)
            print("- Camera Service: Connected to broker.hivemq.com:8000")

        elif external_broker == "hivemq_cert":
            external_client.tls_set(
                ca_certs=None,
                certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
                ciphers=None,
            )
            external_client.connect("broker.hivemq.com", 8884)
            print("- Camera Service: Connected to broker.hivemq.com:8884")

        elif external_broker == "classpip_cred":
            external_client.username_pw_set(username, password)
            external_client.connect("classpip.upc.edu", 8000)
            print("- Camera Service: Connected to classpip.upc.edu:8000")

        elif external_broker == "classpip_cert":
            external_client.username_pw_set(username, password)
            external_client.tls_set(
                ca_certs=None,
                certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
                ciphers=None,
            )
            external_client.connect("classpip.upc.edu", 8883)
            print("- Camera Service: Connected to classpip.upc.edu:8883")
        elif external_broker == "localhost":
            external_client.connect("localhost", 8000)
            print("- Camera Service: Connected to localhost:8000")
        elif external_broker == "localhost_cert":
            print("- Camera Service: Not implemented yet")

    elif connection_mode == "local":
        if operation_mode == "simulation":
            external_client.connect("localhost", 8000)
            print("- Camera Service: Connected to localhost:8000")
        else:
            external_client.connect("10.10.10.1", 8000)
            print("- Camera Service: Connected to 10.10.10.1:8000")

    print("- Camera Service: Waiting....")
    external_client.subscribe("+/CameraService/#", 2)
    internal_client.subscribe("+/CameraService/#")
    internal_client.loop_start()
    external_client.loop_forever()



# WEB SOCKETS
async def send_video_stream(websocket, path):
    # Callback function that sends the video stream to the client
    frames_queue = queue.Queue()
    
    def callback_websocket(jpg_as_text):
        frames_queue.put(jpg_as_text)
    
    # Function that recieves the client message and processes it to start or stop sending video stream
    print("- Camera Service: Starting video stream via Websocket")
    async for message in websocket:
        # Split the message
        splited = message.split("/")
        origin = splited[0]
        command = splited[2]
        camera_id = splited[3]

        # Check if the ID of the camera is the same as the requested one
        if service_id == camera_id:
            if command == "startVideoStream":
                # Start the video stream
                camera.start_video_stream(callback_websocket)
                # Once the video stream is started, send the frames to the client
                while camera.sending_video_stream == True:
                    jpg_as_text = frames_queue.get()
                    if jpg_as_text is None:
                        print("- Camera Service: No frame to send")
                        #await asyncio.sleep(0.03333333333333333)  # 30 frames per second
                        await asyncio.sleep(0.01666666666666667)  # 60 frames per second
                    else:
                        try:
                            await websocket.send(jpg_as_text)
                            #await asyncio.sleep(0.03333333333333333)  # 30 frames per second
                            await asyncio.sleep(0.01666666666666667)  # 60 frames per second
                        except Exception as e:
                            print("- Camera Service: Error sending frame: ", e)


                
            elif command == "stopVideoStream":
                # Stop the video stream
                print("- Camera Service: Stopping video stream via Websocket")
                camera.stop_video_stream()

async def start_websocket_server():
    # Start the websocket server
    port = 8765
    print("- CameraService: Websocket server listening on port:", port)
    websocket = websockets.serve(send_video_stream, "0.0.0.0", port)
    await websocket

def start_websocket_server_in_thread():
    # Function to call when starting the thread
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(start_websocket_server())
    asyncio.get_event_loop().run_forever()

def get_ip():
    # Get the IP of the device
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    return IPAddr
    

import cv2 as cv

if __name__ == "__main__":
    import sys

    # Inicialize variables
    service_id = sys.argv[1]
    connection_mode = sys.argv[2]  # global or local
    operation_mode = sys.argv[3]  # simulation or production
    username = None
    password = None

    if connection_mode == "global":
        external_broker = sys.argv[4]
        if external_broker == "classpip_cred" or external_broker == "classpip_cert":
            username = sys.argv[5]
            password = sys.argv[6]
    else:
        external_broker = None
    
    internal_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Camera_internal")
    internal_client.on_message = on_internal_message
    internal_client.connect("localhost", 1884)

    external_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Camera_external", transport="websockets")
    external_client.on_message = on_external_message
    external_client.on_connect = on_connect

    # Create object Camera
    camera = Camera(service_id)

    # WebSockets parameters
    loop = asyncio.new_event_loop()

    # Thread to inicialize web socket
    wst = threading.Thread(target=start_websocket_server_in_thread)
    wst.start()

    CameraService(connection_mode, operation_mode, external_broker, username, password)
