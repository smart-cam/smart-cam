__author__ = 'ssatpati'

from random import randint
import pprint
import time
import json
import multiprocessing
import log

import boto
from boto.dynamodb2.table import Table

from config import Config

logger = log.getLogger(__name__)

class DynamoDBUtils(object):

    # <TEST ONLY> Mapping of Customer & Pie/Cam
    cust_pie_dict = {
        "cid1" : ["cam1","cam2"],
        "cid2" : ["cam1","cam2"]
    }

    FACES = {
                 'videos/video_100_frames_1.mp4': {
                     'face_count': 59,
                     'face_count_dtl': ['0', '1', '8', '12', '12', '11', '10', '4', '1', '0'],
                     'face_count_uniq': 3,
                     'face_count_uniq_dtl': ['0', '1', '0', '0', '0', '1', '0', '0', '1', '0'],
                     'frame_count': 100,
                     'time_taken': '0:00:04.731971'
                 },
                 'videos/video_100_frames_2.mp4': {'face_count': 62,
                     'face_count_dtl': ['10', '10', '0', '0', '0', '9', '5', '8', '10', '10'],
                     'face_count_uniq': 2,
                     'face_count_uniq_dtl': ['1', '0', '0', '0', '0', '1', '0', '0', '0', '0'],
                     'frame_count': 100,
                     'time_taken': '0:00:04.955812'
                 }
            }

    rasp_names = ["kitchen", "garage"]

    cols = ['START_TIME','LEN','PROCESSED','S3_BUCKET','S3_KEY','VERSION']

    S3_BUCKET = 'smart-cam'

    def __init__(self):
        cfg = Config()
        aws_access_key_id = cfg.get("aws", "access_key_id")
        aws_secret_access_key = cfg.get("aws", "secret_access_key")
        self.conn = boto.dynamodb2.connect_to_region('us-west-1',
                                        aws_access_key_id=aws_access_key_id,
                                        aws_secret_access_key=aws_secret_access_key)
        self.sc = Table('SMARTCAM', connection=self.conn)
        logger.info(self.conn.list_tables())
        pprint.pprint(self.conn.describe_table('SMARTCAM'))

    # <TEST ONLY> Creates one item in table
    def create_items(self, num_items=2):
        cnt = 0
        for rasp_name in DynamoDBUtils.rasp_names:
            for i in xrange(num_items):
                cnt += 1
                self.__create_item(rasp_name, cnt)
                time.sleep(num_items)

    # <TEST ONLY> Creates one item in table
    def __create_item(self, rasp_name, num):
        data = dict()

        data['RASP_NAME'] = rasp_name
        data['START_TIME'] = time.time()
        data['S3_BUCKET'] = DynamoDBUtils.S3_BUCKET
        data['S3_KEY'] = 'videos/video_{0}.avi'.format(num)
        data['PROCESSED'] = 0
        data['CLASSIFIED'] = 0
        data['VERSION'] = 0

        logger.info("# Uploading Data for {0}: {1}".format(rasp_name, num))
        self.sc.put_item(data)

    # <TEST ONLY> Creates multiple full items in table
    def create_full_items(self, num_items=10, start_time=1459555200):
        cnt = 0
        with self.sc.batch_write() as batch:
            for rasp_name in DynamoDBUtils.rasp_names:
                st = start_time
                for i in xrange(num_items):
                    cnt += 1
                    if cnt % 2 == 0:
                        batch.put_item(self.__create_full_item(rasp_name, st, 'videos/video_100_frames_1.mp4'))
                    else:
                        batch.put_item(self.__create_full_item(rasp_name, st, 'videos/video_100_frames_2.mp4'))
                    st += 11.25  # 10 + 1.25 secs between 2 video files

    # <TEST ONLY> Creates multiple full items in table
    # All Hard code values for purpose of testing the Backend/UI Integration
    def __create_full_item(self, rasp_name, start_time, s3_key):
        data = dict()

        data['RASP_NAME'] = rasp_name
        data['START_TIME'] = start_time
        data['UPDATE_TIME'] = start_time + 5
        data['S3_BUCKET'] = DynamoDBUtils.S3_BUCKET
        data['S3_KEY'] = s3_key

        data['FRAME_COUNT'] = DynamoDBUtils.FACES[s3_key]['frame_count']
        data['FACE_COUNT'] = DynamoDBUtils.FACES[s3_key]['face_count']
        data['FACE_COUNT_UNIQ'] = DynamoDBUtils.FACES[s3_key]['face_count_uniq']

        # Face Counts / Detail
        d = {}
        #d['data'] = ['5','5','5','5','5','5','5','5','5','6']
        data['FACE_COUNT_DTL'] = DynamoDBUtils.FACES[s3_key]['face_count_dtl']

        d = {}
        #d['data'] = ['0','0','0','0','0','0','0','0','0','1']
        data['FACE_COUN_UNIQ_DTL'] = DynamoDBUtils.FACES[s3_key]['face_count_uniq_dtl']

        d = {}
        d['data'] = ['0.1','0.1','0.1','0.05','0.05','0.15','0.001','0.05','0.01','0.01']
        data['FOREGROUND'] = d

        data['PROCESSED'] = 1
        data['VERSION'] = 1

        logger.info("# Uploading Data for {0}: {1}".format(rasp_name, start_time))

        # Converted to a Batch Write
        #self.sc.put_item(data)

        return data

    # Creates one item in table
    def create_item(self, rasp_name, s3_bucket, s3_key, s_time):
        data = dict()

        data['RASP_NAME'] = rasp_name
        data['START_TIME'] = s_time
        data['S3_BUCKET'] = s3_bucket
        data['S3_KEY'] = s3_key
        data['PROCESSED'] = 0
        data['CLASSIFIED'] = 0
        data['VERSION'] = 0
        data['LEN'] = randint(5, 60)

        logger.info("# Uploading Data for {0}: {1}:{2}".format(rasp_name, s3_bucket, s3_key))
        self.sc.put_item(data)

    # Fetch items
    def display_items(self):
        rows = self.sc.query_2(index='PROCESSED-index',PROCESSED__eq=0)
        cnt = 0
        for row in rows:
            logger.info('{0},{1},{2}'.format(row['RASP_NAME'],row['START_TIME'],row['PROCESSED']))
            cnt += 1
        logger.info('# Total unprocessed items: {0}'.format(cnt))
        return rows

    def purge_table(self):
        cnt = 0
        for row in self.sc.scan():
            cnt += 1
            row.delete()
            logger.info('Deleted Row: {0}'.format(cnt))

    def delete_by_id(self,id):
        cnt = 0
        for row in self.get_items_by_id(id):
            cnt += 1
            row.delete()
            logger.info('Deleted Row: {0}'.format(cnt))

    def reset_processed(self):
        cnt = 0
        for row in self.sc.scan():
            cnt += 1
            row['PROCESSED'] = 0
            self.update(row)
            logger.info('Update Row: {0}'.format(cnt))

    def reset_classified(self):
        cnt = 0
        for row in self.sc.scan():
            cnt += 1
            row['CLASSIFIED'] = 0
            self.update(row)
            logger.info('Update Row: {0}'.format(cnt))

    def add_classified(self):
        cnt = 0
        for row in self.sc.scan():
            cnt += 1
            row['CLASSIFIED'] = 0
            self.update(row)
            logger.info('Update Row: {0}'.format(cnt))

    def get_unprocessed_items(self):
        return self.sc.query_2(index='PROCESSED-index',PROCESSED__eq=0)

    def get_unclassified_items(self):
        return self.sc.query_2(index='CLASSIFIED-index',CLASSIFIED__eq=0)

    def get_items_by_id(self, id):
        return self.sc.query_2(RASP_NAME__eq=id)

    def get_items_by_id_range(self, id, start, end):
        return self.sc.query_2(RASP_NAME__eq=id, START_TIME__between=(start, end))

    def update(self, row):
        try:
            row.save(overwrite=True)
        except Exception as e:
            logger.error(e)
            logger.info('[FAILED] Processing: ', row['RASP_NAME'],row['START_TIME'],row['PROCESSED'])

    def stats(self,lst):
        quotient, remainder = divmod(len(lst), 2)
        if remainder:
            return sorted(lst)[quotient]
        return sum(lst) / len(lst), sum(sorted(lst)[quotient - 1:quotient + 1]) / 2

    def close(self):
        self.conn.close()

# repeatedly upload items to simpleDB until program is forced to exit
if __name__ == "__main__":
    db = DynamoDBUtils()
    db.display_items()
    logger.info('### Query By ID: ')
    for row in db.get_items_by_id('kitchen'):
        logger.info(row['RASP_NAME'])
    logger.info('### Query By Range Key: ')
    for row in db.get_items_by_id_range('cid1_cam1', 1459621230, 1459621270):
        logger.info('{0},{1},{2}'.format(row['RASP_NAME'],row['START_TIME'],row['PROCESSED']))
    db.close()