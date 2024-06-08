import base64
import cv2 as cv  # OpenCV
import threading
import time



def send_video_stream(self, callback):
    # Send video stream main function

    while self.sending_video_stream:
        # Read Frame
        ret, frame = self.cap.read()
        if ret:
            _, image_buffer = cv.imencode(".jpg", frame)
            jpg_as_text = base64.b64encode(image_buffer)
            callback(jpg_as_text)
            time.sleep(0.1)  # 60 fps

def start_video_stream(self, callback):
    # Start video stream main function
    print("- CameraLink: Starting video stream")
    self.sending_video_stream = True
    # Create a thread to send the video stream (always non-blocking)
    w = threading.Thread(target=self.send_video_stream, args=[callback])
    w.start()

def stop_video_stream(self):
    # Stop video stream main function
    print("- CameraLink: Stopping video stream")
    self.sending_video_stream = False
    