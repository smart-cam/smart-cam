# this code uploads sample data to simpleDB for use with process.data.py

from boto import dynamodb2
from boto.dynamodb2.table import Table
from random import randint
import time

# set up connection to dynamo
access_key = ""
secret_key = ""
TABLE_NAME = "test_data"
REGION = "us-west-1"

# connect to dynamo
conn = dynamodb2.connect_to_region(REGION, 
        aws_access_key_id=access_key, aws_secret_access_key=secret_key)

# this connects to an already existing table. does not create a new one!
table = Table(TABLE_NAME, connection=conn)

# upload an item to simpleDB
def upload_data(num):
    d = dict()
    name = "video"+str(i)
    d['customer'] = "customer1"
    d['src'] = "Pi1"
    d['filename'] = name
    d['bucket'] = "w210-video-repo"
    d['len'] = randint(5, 60)
    d['timestamp'] = time.time()
    d['lock'] = ""
    d['lock_id'] = 0
    d['processed'] = 0
    d['lockstamp'] = 0.0
    print "uploading data for " + name
    table.put_item(d)

# repeatedly upload items to simpleDB until program is forced to exit
if __name__ == "__main__":
    i = 0
    while(True):
        # quickly upload 50 items
        if i < 10:
            upload_data(i)
            i += 1

        # after 50 items in DB, sleep for 1s then upload 3 more items
        else:
            time.sleep(5)
            upload_data(i)
            i += 1
            upload_data(i)
            i += 1
            upload_data(i)
            i += 1
