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

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    ret, local_file = misc.download_from_s3(BUCKET_NAME, 'videos/video_1.avi', OUTPUT_DIR)

    print ret, local_file

    fd = FaceDetection()
    report = fd.process(local_file)
    pprint.pprint(report)
    d = {}
    d['data'] = report['face_count_dtl']
    #pprint.pprint(d)
    d= {}
    d['data'] = report['face_count_uniq_dtl']
    #pprint.pprint(d)
    for i in xrange(len(report['face_count_dtl'])):
        print i, round(random.uniform(0, 1.0), 10)