from util.db import DynamoDBUtils
from util import misc
from util import log

import multiprocessing
import subprocess
import cv2
import pprint
import glob
import time
import shutil
import os
import sys

logger = log.getLogger(__name__)


#Path to Default Video File
VIDEO_FILE = '../resources/video.avi'

PARALLEL_PROCS = 1
OUTPUT_DIR = os.path.expanduser('~') + '/videos1'

# Create all Classes
db = DynamoDBUtils()


def update_record(row, report):
    # Metadata

    # Update
    db.update(row)


def process_item(row):
    d = {}
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
            local_file_basename = os.path.basename(local_file)
            logger.info('[{0}]'.format(local_file_basename))

            local_dir = local_file + ".D"

            # Create a dir
            os.makedirs(local_dir)

            # Dump the frames
            cap = cv2.VideoCapture(local_file)
            cnt = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if cnt % 5 == 0:
                    image_file = '{0}/frame_{1}.png'.format(local_dir, cnt)
                    cv2.imwrite(image_file,frame)
                    logger.info('[{0}] Image File Written: {1}'.format(local_file_basename, image_file))
                cnt +=1

            output_file = local_dir + '/tf.class.out'

            # Run Image Classification
            for f in glob.glob(local_dir + '/*'):
                logger.info('[{0}] Image Classification: {1}'.format(local_file_basename, f))
                frame_id = os.path.basename(f).split(".")[0].split("_")[1]
                rc = subprocess.call(['./util/tf_classify.sh',f,output_file])
                with open(output_file, 'r') as f:
                    classification = {}
                    for l in f.readlines():
                        t = l.split(":")
                        classification[t[0].strip()] = t[1].strip()
                        break # Just first line
                    d[str(frame_id)] = classification

            print d


            # Update Fields in DB
            #update_record(row, report)

            #Delete the file/folder
            #os.remove(local_file)
            #shutil.rmtree(local_dir)
            print '### Sleeping for 100 secs ###'
            time.sleep(100)
        else:
            logger.info('[{0}][{1}] FAILED Downloading File: {2}/{3}'.format(row['RASP_NAME'],row['START_TIME'],row['S3_BUCKET'],row['S3_KEY']))
    except Exception as e:
        logger.error(e)
        logger.info('[{0}][{1}] FAILED Classifying Video: {2}/{3}'.format(row['RASP_NAME'],row['START_TIME'],row['S3_BUCKET'],row['S3_KEY']))
        #Delete the file
        os.remove(local_file)
        sys.exit(1)


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
        rows = db.get_unclassified_items()

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