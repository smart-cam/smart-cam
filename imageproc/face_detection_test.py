__author__ = 'ssatpati'
from face_detection import FaceDetection
from util.db import DynamoDBUtils
from util import misc
import random
import shutil
import pprint
import os

OUTPUT_DIR = '../videos'

if __name__ == '__main__':
    BUCKET_NAME = 'smart-cam'

    '''
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    ret, local_file = misc.download_from_s3(BUCKET_NAME, 'videos/video_1.avi', OUTPUT_DIR)

    print ret, local_file
    '''

    #local_file = '../videos/video_100_frames_2.mp4'
    local_file = '../videos/Office_1460080165.688278.mp4'

    fd = FaceDetection()
    report = fd.process(local_file, show_frame=False)
    pprint.pprint(report)