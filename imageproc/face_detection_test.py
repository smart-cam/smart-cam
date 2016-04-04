__author__ = 'ssatpati'
from face_detection import FaceDetection
from util.db import DynamoDBUtils
import pprint
from util import misc
import os


if __name__ == '__main__':
    BUCKET_NAME = 'smart-cam'

    try:
        os.remove('../videos/video_1.avi')
    except Exception as e:
        print e

    ret, local_file = misc.download_from_s3(BUCKET_NAME, 'videos/video_1.avi', '../videos')

    print ret, local_file

    fd = FaceDetection()
    report = fd.process(local_file)
    pprint.pprint(report)