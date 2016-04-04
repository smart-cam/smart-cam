__author__ = 'ssatpati'
from face_detection import FaceDetection
from util.db import DynamoDBUtils
from util import misc
import shutil
import pprint
import os

OUTPUT_DIR = '../videos'

if __name__ == '__main__':
    BUCKET_NAME = 'smart-cam'

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    ret, local_file = misc.download_from_s3(BUCKET_NAME, 'videos/video_1.avi', OUTPUT_DIR)

    print ret, local_file

    fd = FaceDetection()
    report = fd.process(local_file)
    pprint.pprint(report)