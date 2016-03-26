import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import cv2
import threading


FRAMES_DICT = list()

RASPBERRY_PI_NAME = "Raspberry_PI_1"

# Creating MOG object
##OLD CODE## fgbg = cv2.BackgroundSubtractorMOG()
fgbg = cv2.createBackgroundSubtractorMOG2()
# Setting up Raspberry Pi camera
camera = PiCamera()
camera.resolution = (360, 240)
camera.framerate = 15
rawCapture = PiRGBArray(camera, size=(360, 240))

# Giving time to camera to warm-up
time.sleep(0.1)

def getMotionFromFrame(frame, threshold):
    # This function returns True if mass of truth is greater than threshold
    frameCopy = frame.copy()
    totalMass = frameCopy.size

    frameCopy[frameCopy > 0] = 1        # Converting all non-zero pixels to 1
    frameCopyMass = frameCopy.sum()
    fraction = frameCopyMass/totalMass
    
    if fraction > threshold:
        response = True
    else:
        response = False

    return response, round(fraction, 4)

# Function to write SmartCam and timestamp into a frame
def writeToFrame(frameDict):
    frameCopy = frameDict['frame'].copy()
    # Writing SmartCam
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frameCopy, 'Capstone project: SmartCam', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1, 8)
    # Writing timestamp
    timestamp = frameDict['timestamp']
    cv2.putText(frameCopy, timestamp, (50,70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1, 8)
    return frameCopy

##OLD CODE## fourcc = cv2.cv.CV_FOURCC(*'XVID')
fourcc = cv2.VideoWriter_fourcc(*'XVID')
clipWriter = cv2.VideoWriter("tt.avi", fourcc, 15, (360, 240))

def frameWriter():
    while True:
        if len(FRAMES_DICT) > 0:
            frameDict = FRAMES_DICT.pop(0)
            frame = writeToFrame(frameDict)
            clipWriter.write(frame)

writerThread = threading.Thread(name='Writer', target=frameWriter)
writerThread.start()

##ADDITIONAL CODE##
num_frames = 0
start = time.time()
##end of ADDITIONAL CODE##

t1 = time.time()
f = open("PerFrameTimeTaken.txt", "w")
for frame_data in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    ##ADDITIONAL CODE##
    num_frames += 1
    ##end of ADDITIONAL CODE##
    frame = frame_data.array
    timestamp = time.asctime() + ' ' + time.tzname[0]
    frameDict = dict()
    frameDict['timestamp'] = timestamp
    frameDict['frame'] = frame
    FRAMES_DICT.append(frameDict)
    
    ##ADDITIONAL CODE##
    end = time.time()
    seconds = end - start
    fps  = num_frames / seconds;
    print "Estimated frames per second : {0}".format(fps);
    ##end of ADDITIONAL CODE##

    # Processing image
    #blurred = cv2.medianBlur(frame, 9)
    #fgmask = fgbg.apply(blurred)

    #isMotion, fraction = getMotionFromFrame(fgmask, 0.001)

    # Writing SmartCam and timestamp
    #frame = writeToFrame(frameDict)

    #clipWriter.write(frame)
    rawCapture.truncate(0)
    t2 = time.time()
    f.write(str(t2-t1) + "\n")
    t1=t2


