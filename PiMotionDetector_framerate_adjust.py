import numpy as np
import cv2
from scipy import ndimage
from scipy.spatial import distance
import time
import math
from picamera import PiCamera
from picamera.array import PiRGBArray

import re

RASPBERRY_PI_NAME = "RPi_1"
CAMERA_INDEX = 0        # Usually 0 for webcam, not needed for Pi camera

# Motion Detection class
class MotionDetector:
    def __init__(self):
        # Initializing variables
        self.previous_center_of_mass = (0, 0)
        self.previous_sum_of_edges = 0

    ### NOTE: do we need to pass frame to this function? it is unused
    def isMotion(self, frame, edges):
        # Converting edges from 255 to 1
        edges_to_1 = edges/255
        
        # Calculating distance between center of mass between 2 consecutive frames
        current_center_of_mass = ndimage.measurements.center_of_mass(edges_to_1)
        distance_of_centers = distance.euclidean(current_center_of_mass, self.previous_center_of_mass)

        # Calculating change in sum of edges
        current_sum_of_edges = int(edges_to_1.sum())
        change_in_sum_of_edges = abs(current_sum_of_edges - self.previous_sum_of_edges)

        # Assign current values to previous values
        self.previous_center_of_mass = current_center_of_mass
        self.previous_sum_of_edges = current_sum_of_edges

        if change_in_sum_of_edges > 0.05*self.previous_sum_of_edges or distance_of_centers > 7:
            # Motion detected
            return True
        else:
            return False

# Function to write SmartCam and timestamp into a frame
# and add a white dot to edges to depict center of mass
def writeToFrame(frame, edges):
    # Writing SmartCam
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, 'Capstone project: SmartCam', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 1, 8)
    # Writing timestamp
    timestamp = time.asctime() + ' ' + time.tzname[0]
    cv2.putText(frame, timestamp, (50,70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1, 8)

    # Drawing a circle for center of mass
    center = ndimage.measurements.center_of_mass(edges/255)
    if math.isnan(center[0]) == False:
        c = tuple(int(x) for x in center)   # Converting center of mass into integer
        cv2.circle(edges, c, 15, 255, thickness=-1, lineType=8, shift=0)
    
    return frame, edges

# Video Clip Writer class
class VideoClipWriter:
    def __init__(self):
        # NOTE: which of the next two lines you need to use depends on your cv2 version
        #self.fourcc = cv2.cv.CV_FOURCC(*'XVID')
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.filename_prefix = RASPBERRY_PI_NAME
        self.filename_timestamp = 0
        self.motion_detection_timestamp = 0
        self.clipWriter = None
        self.videoLength = 60        # in seconds
        self.record_after_motion_detection = 15        # in seconds

    def motionTrigger(self, ifMotion):
        if ifMotion == False:
            return
        elif ifMotion == True:
            curr_time = time.time()
            if self.clipWriter == None:
                self.createVideoWriterObject(curr_time)
                self.filename_timestamp = curr_time
                self.motion_detection_timestamp = curr_time
            elif self.clipWriter.isOpened() == True:
                self.motion_detection_timestamp = curr_time
    
    def frameTrigger(self, frame):
        curr_time = time.time()
        print (1000*round(curr_time - self.filename_timestamp, 3)) % 50.0
        #if self.clipWriter == None or not (1000*round(curr_time - self.filename_timestamp, 3)) % 50.0:
        if self.clipWriter == None:
            return
        if self.clipWriter.isOpened() == True and curr_time - self.filename_timestamp < self.videoLength and curr_time - self.motion_detection_timestamp < self.record_after_motion_detection:
            self.clipWriter.write(frame)
        elif self.clipWriter.isOpened() == True and curr_time - self.filename_timestamp > self.videoLength and curr_time - self.motion_detection_timestamp < self.record_after_motion_detection:
            self.clipWriter.release()
            self.clipWriter = None
            self.createVideoWriterObject(curr_time)
            self.filename_timestamp = curr_time
        elif self.clipWriter.isOpened() == True and curr_time - self.filename_timestamp < self.videoLength and curr_time - self.motion_detection_timestamp > self.record_after_motion_detection:
            self.clipWriter.release()
            self.clipWriter = None
        return

    def createVideoWriterObject(self, curr_time):
        # filename = self.filename_prefix + '_' + str(curr_time) + '.avi'
        filename = self.filename_prefix + '_' + \
            time.strftime("%Y%m%d_%H%M%S", time.gmtime(curr_time)) + '_' + \
            str(round(curr_time % 1, 3))[2:5] + '.avi'
        self.clipWriter = cv2.VideoWriter(filename, self.fourcc, 3.0, (640,480))

def main():
    # Creating video capture object
    #camera = cv2.VideoCapture(CAMERA_INDEX)

    # set up the Pi's camera
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 20
    rawCapture = PiRGBArray(camera, size=(640, 480))

    # Creating motion detector object
    motionDetectorObject = MotionDetector()
    # Creating video writer object
    clipWriterObject = VideoClipWriter()

    num_frames = 0
    start = time.time()

    # Capture frames
    for frame_data in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        #ret, frame = camera.read()
        # Getting edges



        frame = frame_data.array
        edges = cv2.Canny(frame, 160, 200)

        num_frames += 1

        isMotion = motionDetectorObject.isMotion(frame, edges)
        print isMotion
        
        # Writing to frame and edges
        frame, edges = writeToFrame(frame, edges)
        clipWriterObject.motionTrigger(isMotion)
        clipWriterObject.frameTrigger(frame)
        
        cv2.imshow("Frame", frame)
        cv2.imshow("Edges", edges)
        key = cv2.waitKey(1) & 0xFF

        # clear stream for next frame capture
        rawCapture.truncate(0)

        end = time.time()
        seconds = end - start
        fps  = num_frames / seconds;
        print "Estimated frames per second : {0}".format(fps);

        # end capture if q key is pressed
        if key == ord('q'):
            break

    #camera.release()

if __name__ == '__main__':
    main()
