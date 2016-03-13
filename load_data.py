# this code uploads sample data to simpleDB for use with process_data.py

import boto
from random import randint
import time

# set up connection to simpleDB
aws_access_key_id = ""
aws_secret_access_key = ""
conn = boto.connect_sdb(aws_access_key_id, aws_secret_access_key)
domain = conn.create_domain("test1")

# upload an item to simpleDB
def upload_data(num):
    d = dict()
    name = "video"+str(i)
    d['name'] = name
    d['src'] = "Pi1"
    d['url'] = "http://something"
    d['len'] = randint(5, 60)
    d['timestamp'] = time.time()
    d['lock'] = False
    d['lock_id'] = 0
    d['processed'] = False
    d['lockstamp'] = 0.0
    print "uploading data for " + name
    domain.put_attributes(name, d)

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
