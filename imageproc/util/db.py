__author__ = 'ssatpati'

from random import randint
import pprint
import time
import json
import multiprocessing

import boto
from boto.dynamodb2.table import Table

from config import Config


class DynamoDBUtils(object):

    # <TEST ONLY> Mapping of Customer & Pie/Cam
    cust_pie_dict = {
        "cid1" : ["cam1","cam1"],
        "cid2" : ["cam1","cam2"]
    }

    cols = ['CREATE_TIME','LEN','PROCESSED','S3_BUCKET','S3_KEY','VERSION']

    def __init__(self):
        cfg = Config()
        aws_access_key_id = cfg.get("aws", "access_key_id")
        aws_secret_access_key = cfg.get("aws", "secret_access_key")
        self.conn = boto.dynamodb2.connect_to_region('us-west-1',
                                        aws_access_key_id=aws_access_key_id,
                                        aws_secret_access_key=aws_secret_access_key)
        self.sc = Table('SMARTCAM', connection=self.conn)
        print self.conn.list_tables()
        pprint.pprint(self.conn.describe_table('SMARTCAM'))

    # <TEST ONLY> Creates Sample Records: 10 records per cust/cam
    def create_items(self):
        cnt = 0
        for cust,cams in DynamoDBUtils.cust_pie_dict.iteritems():
            for cam in cams:
                for i in xrange(2):
                    cnt += 1
                    self.__create_item(cust, cam, cnt)

    # <TEST ONLY> Creates one item in table
    def __create_item(self, c_id, cam_id, num):
        data = dict()

        data['CUSTID_PIEID'] = c_id + '_' + cam_id
        data['CREATE_TIME'] = time.time()
        data['S3_BUCKET'] = 'w210-smartcam'
        data['S3_KEY'] = 'videos/video_{0}.avi'.format(num)
        data['PROCESSED'] = 0
        data['VERSION'] = 0
        data['LEN'] = randint(5, 60)

        print "# Uploading Data for {0},{1}: {2}".format(c_id,cam_id,num)
        self.sc.put_item(data)

    # Creates one item in table
    def create_item(self, c_id, cam_id, s3_bucket, s3_key):
        data = dict()

        data['CUSTID_PIEID'] = c_id + '_' + cam_id
        data['CREATE_TIME'] = time.time()
        data['S3_BUCKET'] = s3_bucket
        data['S3_KEY'] = s3_key
        data['PROCESSED'] = 0
        data['VERSION'] = 0
        data['LEN'] = randint(5, 60)

        print "# Uploading Data for {0},{1}: {2}".format(c_id,cam_id,s3_url)
        self.sc.put_item(data)

    # Fetch items
    def display_items(self):
        rows = self.sc.query_2(index='PROCESSED-index',PROCESSED__eq=0)
        cnt = 0
        for row in rows:
            print row['CUSTID_PIEID'],row['TIMESTAMP'],row['PROCESSED']
            cnt += 1
        print '# Total unprocessed items: {0}'.format(cnt)
        return rows

    def purge_table(self):
        cnt = 0
        for row in self.sc.scan():
            cnt += 1
            row.delete()
            print 'Deleted Row: {0}'.format(cnt)

    def get_unprocessed_items(self):
        return self.sc.query_2(index='PROCESSED-index',PROCESSED__eq=0)

    def get_items_by_id(self, id):
        return self.sc.query_2(CUSTID_PIEID__eq=id)

    # Process Item
    def process_item(self,row):
        '''Face Counting needs to be integrated here'''
        print 'Processing: ', row['CUSTID_PIEID'],row['CREATE_TIME'],row['PROCESSED']

        try:
            #Create Dict - Assumption: 30 secs video / 20fps
            d = {}
            fc_t = []
            fc_u = []
            for i in xrange(30):
                d[i] = {}
                fc = randint(1, 50)
                fc_t.append(fc)
                d[i]['fc_t'] = fc
                fc = randint(1, 25)
                fc_u.append(fc)
                d[i]['fc_u'] = fc

            row['UPDATE_TIME'] = time.time()
            row['VERSION'] += 1
            row['PROCESSED'] = 1
            row['FACES'] = json.dumps(d)
            #print json.dumps(d)

            # Aggregated Counts per file
            fc_t_mean, fc_t_median = stats(fc_t)
            fc_u_mean, fc_u_median = stats(fc_u)

            row['FACE_COUNT_TOT_MEAN'] = fc_t_mean
            row['FACE_COUNT_TOT_MEDIAN'] = fc_t_median

            row['FACE_COUNT_UNIQ_MEAN'] = fc_u_mean
            row['FACE_COUNT_UNIQ_MEDIAN'] = fc_u_median

            #row.partial_save()
            row.save(overwrite=True)
        except Exception as e:
            print e
            print '[FAILED] Processing: ', row['CUSTID_PIEID'],row['CREATE_TIME'],row['PROCESSED']


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
    print '###'
    for row in db.get_items_by_id('cid1_cam1'):
        print row['CUSTID_PIEID']
    db.close()