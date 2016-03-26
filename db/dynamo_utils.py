__author__ = 'ssatpati'

import boto
from boto.dynamodb2.table import Table
from random import randint
import pprint
import time
import multiprocessing

PARALLEL_PROCS = 10

# set up connection to simpleDB
aws_access_key_id = "AKIAIR6PPMENHJVJHGFQ"
aws_secret_access_key = "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"

conn = boto.dynamodb2.connect_to_region('us-west-1',
                                        aws_access_key_id=aws_access_key_id,
                                        aws_secret_access_key=aws_secret_access_key)



sc = Table('SMARTCAM', connection=conn)

# Mapping of Customer & Pie/Cam
cust_pie_dict = {
    "cid1" : ["cam1","cam1"],
    "cid2" : ["cam1","cam2"]
}


# Creates Sample Records: 10 records per cust/cam
def create_items():
    for cust,cams in cust_pie_dict.iteritems():
        for cam in cams:
            for i in xrange(10):
                create_item(cust, cam, i)

# Creates one item in table
def create_item(c_id, cam_id, num):
    data = dict()

    data['CUSTID_PIEID'] = c_id + '_' + cam_id
    data['TIMESTAMP'] = time.time()
    data['S3_URL'] = 's3://smartcam/{0}/{1}/video_{2}'.format(c_id,cam_id,num)
    data['PROCESSED'] = 0
    data['VERSION'] = 0
    data['LEN'] = randint(5, 60)

    print "# Uploading Data for {0},{1}: {2}".format(c_id,cam_id,num)
    sc.put_item(data)

# Fetch items
def display_items():
    rows = sc.query_2(index='PROCESSED-index',PROCESSED__eq=0)
    cnt = 0
    for row in rows:
        print row['CUSTID_PIEID'],row['TIMESTAMP'],row['PROCESSED']
        cnt += 1
    print '# Total unprocessed items: {0}'.format(cnt)
    return rows

def fetch_items():
    return sc.query_2(index='PROCESSED-index',PROCESSED__eq=0)

def delete_item(rows):
    cnt = 0
    for row in rows:
        cnt += 1
        row.delete()
        print 'Deleted Row: {0}'.format(cnt)

# Process Item
def process_item(row):
    '''Face Counting needs to be integrated here'''
    row['PROCESSED'] = 1
    row['FACE_COUNT_TOTAL'] = randint(1, 200)
    row['FACE_COUNT_UNIQUE'] = randint(1, 50)
    row.partial_save()


# repeatedly upload items to simpleDB until program is forced to exit
if __name__ == "__main__":
    print conn.list_tables()
    pprint.pprint(conn.describe_table('SMARTCAM'))

    # Delete existing items
    rows = fetch_items()
    delete_item(rows)

    # Create items
    create_items()

    while(True):
        display_items()
        rows = fetch_items()
        time.sleep(2)

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
            # Remaining Records
            for job in jobs:
                job.start()
            for job in jobs:
                job.join()
            del jobs[:]  # Re-Init
        else:
            print '# No unprocessed record found in DB, sleeping for 5 secs'
            time.sleep(5)