import cv2 as cv # OpenCV 

class Camera(object):
    def __init__(self, ID):
        self.ID = ID # ID of the camera
        self.cap = cv.VideoCapture(0) # video capture source camera (Here webcam of lap>
        self.sending_video_stream = False # Flag to send video stream 


    '''
    Here the methods of the Camera class are imported, which are organized into files.
    This way, future students who need to incorporate new services for their applications could organize their contributions.
    They would create a file with their new methods and import it here.
    '''

    from functions_camera.take_picture_func import take_picture
    from functions_camera.video_stream_func import send_video_stream, start_video_stream, stop_video_stream

