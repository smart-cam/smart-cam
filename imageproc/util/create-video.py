__author__ = 'ssatpati'

import glob
import cv2

img1 = cv2.imread('/Users/ssatpati/tmp/face_detection/P1E_S1_C1/00000000.jpg')
height , width , layers =  img1.shape
print img1.shape
#cv2.imshow('Input', img1)


'''
https://www.codementor.io/tips/4192438272/writing-a-video-file-using-h-264-compression-in-opencv
'''
#fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') # note the lower case

#fourcc = cv2.VideoWriter_fourcc('H','2','6','4') # note the lower case
#fourcc = cv2.VideoWriter_fourcc('X','2','6','4') # note the lower case


fourcc = cv2.VideoWriter_fourcc('a','v','c','1') # note the lower case


#video = cv2.VideoWriter('../../videos/video_100_frames_1.mp4',fourcc, 20.0, (width,height))
video = cv2.VideoWriter('../../videos/video_100_frames_1_1.mp4',fourcc, 20.0, (width,height))

'''
cnt = 1
for f in glob.glob("/Users/ssatpati/tmp/face_detection/P1E_S1_C1/*.jpg"):
    print f
    if cnt % 500 == 0:
        video.release()
        video = cv2.VideoWriter('video_{0}.avi'.format(cnt),fourcc, 20.0, (width,height))
    video.write(cv2.imread(f))
    cnt += 1
    print "Num of Frames Added: {0}".format(cnt)

'''

for f in glob.glob("/Users/ssatpati/tmp/face_detection/100_FRAMES/1/*.jpg"):
    print f
    video.write(cv2.imread(f))


cv2.destroyAllWindows()
video.release()

