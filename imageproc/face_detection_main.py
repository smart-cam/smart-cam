from face_detection import FaceDetection
from util.db import DynamoDBUtils
from util import misc
from util import log

import multiprocessing
import pprint
import time
import shutil
import os

logger = log.getLogger(__name__)


#Path to Default Video File
VIDEO_FILE = '../resources/video.avi'

PARALLEL_PROCS = 10
OUTPUT_DIR = os.path.expanduser('~') + '/videos'

# Create all Classes
db = DynamoDBUtils()
fd = FaceDetection()


def update_record(row, report):
    # Metadata
    row['UPDATE_TIME'] = time.time()
    row['VERSION'] += 1
    row['PROCESSED'] = 1

    # Face Counts / Summary
    row['FRAME_COUNT'] = report['frame_count']
    row['FACE_COUNT'] = report['face_count']
    row['FACE_COUNT_UNIQ'] = report['face_count_uniq']

    # Face Counts / Detail
    d = {}
    d['data'] = report['face_count_dtl']
    row['FACE_COUNT_DTL'] = d
    d= {}
    d['data'] = report['face_count_uniq_dtl']
    row['FACE_COUN_UNIQ_DTL'] = d

    # Update
    db.update(row)


def process_item(row):
    '''Face Counting needs to be integrated here'''
    try:
        logger.info('Processing: <{0}> <{1}> <{2}> <{3}> <{4}>'.format(row['RASP_NAME'],
                                                                 row['START_TIME'],
                                                                 row['PROCESSED'],
                                                                 row['S3_BUCKET'],
                                                                 row['S3_KEY']))
        # Download File from S3
        ret_status, local_file = misc.download_from_s3(row['S3_BUCKET'], row['S3_KEY'], OUTPUT_DIR)
        if ret_status:
            logger.info('[{0}][{1}] Video File: {2}'.format(row['RASP_NAME'],row['START_TIME'],local_file))
            #time.sleep(10)

            # Run Face Count
            report = fd.process(local_file)
            pprint.pprint(report)

            # Update Fields in DB
            update_record(row, report)

            #Delete the file
            os.remove(local_file)
        else:
            logger.info('[{0}][{1}] FAILED Downloading File: {2}/{3}'.format(row['RASP_NAME'],row['START_TIME'],row['S3_BUCKET'],row['S3_KEY']))
    except Exception as e:
        logger.error(e)
        logger.info('[{0}][{1}] FAILED Processing Video: {2}/{3}'.format(row['RASP_NAME'],row['START_TIME'],row['S3_BUCKET'],row['S3_KEY']))
        #Delete the file
        os.remove(local_file)


if __name__ == '__main__':
    '''Main Entry Point to the Program'''

    sleep_secs = 10

    # Test Code Only
    #db.purge_table()
    #time.sleep(5)

    # Test Code Only
    #db.create_items()
    #time.sleep()

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

        logger.info('# Processing Done for this Batch, sleeping for {0} secs'.format(sleep_secs))
        time.sleep(sleep_secs)


    #report = fd.process(VIDEO_FILE)
    #print "\n################### REPORT ###################\n"
    #pprint.pprint(report)
    #print "\n################### ###### ###################\n"