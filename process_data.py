# this code implements locks when processing data in simpleDB
# so that each simpleDB item does not get processed more than once
# it uses simpleDB's consistent reads and conditional puts 
# try running multiple instances of this script at once to see its effects

import boto
import time
import uuid
import sys

# set up connection to simpleDB
aws_access_key_id = ""
aws_secret_access_key = ""
conn = boto.connect_sdb(aws_access_key_id, aws_secret_access_key)
domain = conn.get_domain(sys.argv[1])

# lock will timeout after 15 seconds
LOCK_TIMEOUT = 15
# try to acquire lock for no more than 2 seconds
ACQ_TIMEOUT = 2


# release the lock for an item in the database
# this operation marks the item as processed
def release_item(db_item, lockID):
    print "releasing lock for item " + db_item
    # release lock, ensure that the lock ID is what we expect
    domain.put_attributes(db_item, {'lockstamp':0.0, 'lock':False,
        'lock_id':0, 'processed':True}, 
        expected_value=['lock_id', str(lockID)])


# attempt to acquire lock for item
# lock acquisition is conditional on the item 1) being unlocked, and
# 2) the item being unprocessed
#
# simpleDB's conditional put can check state of only one attribute
# so after the conditional put, we have to call get_attributes to check
# that the item is still in the unprocessed state
def lock_item(db_item):
    time_limit = time.time() + ACQ_TIMEOUT

    # try to acquire lock for ACQ_TIMEOUT seconds
    while time.time() < time_limit:
        timeout = time.time() + LOCK_TIMEOUT
        lockID = uuid.uuid4() # create unique ID for lock

        # attempt to set lock on item, but only if it is currently unlocked
        try:
            if domain.put_attributes(db_item, {'lockstamp':timeout,
                'lock':True, 'lock_id':lockID}, 
                expected_value=['lock', 'False']):

                # make sure item hasn't been processed since initial query
                item = domain.get_attributes(db_item, 
                        'processed', consistent_read = True)
                if item['processed'] == 'True':
                    release_item(db_item, lockID)
                    return None

                return lockID
        # if exception is because item is locked, continue with exection
        except boto.exception.SDBResponseError, e:
            if e.status != 404 and e.status != 409:
                sys.stderr.write(str(e))
                return None

        # if we can't get lock, check if lock has expired
        item = domain.get_attributes(db_item, consistent_read = True)
        if float(item['lockstamp']) < time.time() and item['processed'] != 'True':
            print "force releasing lock for %s, time %f < %f" %(db_item,
                    float(item['lockstamp']), time.time())
            release_item(db_item, item['lock_id']) # release expired lock

    # if we can't get lock, give up
    print "could not get lock for item " + db_item
    return None


# query the DB every 5 seconds to get the unprocessed items
# try to acquire the lock on each item, then process and unlock it
if __name__ == "__main__":
    query = "select name from "+sys.argv[1]+ " where processed='False'"
    while(True):
        rs = domain.select(query)
        for item in rs:
            lock = lock_item(item['name'])
            time.sleep(0.1) # simulate processing the data
            if lock:
                release_item(item['name'], lock)
                print item['name']

        # wait before issuing next query
        time.sleep(5)
