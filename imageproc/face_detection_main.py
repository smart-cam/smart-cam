from face_detection import FaceDetection
from util.db import DynamoDBUtils
from util import misc

import multiprocessing
import pprint
import time
import shutil
import os

#Path to Default Video File
VIDEO_FILE = '../resources/video.avi'

PARALLEL_PROCS = 10
OUTPUT_DIR = '../videos'

# Create all Classes
db = DynamoDBUtils()
fd = FaceDetection()

def process_item(row):
    '''Face Counting needs to be integrated here'''
    print 'Processing: <{0}> <{1}> <{2}> <{3}> <{4}>'.format(row['RASP_NAME'],
                                                             row['START_TIME'],
                                                             row['PROCESSED'],
                                                             row['S3_BUCKET'],
                                                             row['S3_KEY'])

    ret_status, local_file = misc.download_from_s3(row['S3_BUCKET'], row['S3_KEY'], OUTPUT_DIR)
    if ret_status:
        print '[{0}][{1}] Video File: {2}'.format(row['RASP_NAME'],row['START_TIME'],local_file)
        time.sleep(10)
        report = fd.process(local_file)
        pprint.pprint(report)
    else:
       print '[{0}][{1}] FAILED Downloading File: {2}/{3}'.format(row['RASP_NAME'],row['START_TIME'],row['S3_BUCKET'],row['S3_KEY'])

if __name__ == '__main__':
    '''Main Entry Point to the Program'''

    # Test Code Only
    #db.purge_table()
    #time.sleep(5)

    # Test Code Only
    #db.create_items()
    #time.sleep(5)

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    while True:
        db.display_items()
        rows = db.get_unprocessed_items()

        # Process Items
        if rows != None:
            jobs = []
            cnt = 0
            for row in rows:
                cnt += 1
                p = multiprocessing.Process(target=process_item, args=(row,))
                jobs.append(p)
                # Start processes
                if cnt % PARALLEL_PROCS == 0:
                    for job in jobs:
                        job.start()
                    for job in jobs:
                        job.join()
                    del jobs[:]  # Re-Init

            if len(jobs) > 0:
                # Remaining Records or Less than Batch Size
                for job in jobs:
                    job.start()
                for job in jobs:
                    job.join()
                del jobs[:]  # Re-Init

        print '# Processing Done for this Batch, sleeping for 5 secs'
        time.sleep(10)


    #report = fd.process(VIDEO_FILE)
    #print "\n################### REPORT ###################\n"
    #pprint.pprint(report)
    #print "\n################### ###### ###################\n"