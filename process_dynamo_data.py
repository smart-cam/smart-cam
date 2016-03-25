# this code implements locks when processing data in simpleDB
# so that each simpleDB item does not get processed more than once
# it uses simpleDB's consistent reads and conditional puts 
# try running multiple instances of this script at once to see its effects

from boto import dynamodb2
from boto.dynamodb2.table import Table
import time
import uuid
import sys

# configure connection parameters
access_key = ""
secret_key = ""
TABLE_NAME = "test_data"
REGION = "us-west-1"

# set up connection to AWS and DynamoDB
conn = dynamodb2.connect_to_region(REGION,
        aws_access_key_id=access_key, aws_secret_access_key=secret_key)
table = Table(TABLE_NAME, connection=conn)

# settings for lock functionality
LOCK_TIMEOUT = 15 # lock will timeout after 15 seconds
ACQ_TIMEOUT = 3 # try to acquire lock for no more than 3 seconds


# acquire lock for a DynamoDB item
# lock acquisition is conditional that the item 1) is unlocked, and
# 2) the item is unprocessed
#
# boto's high-level interface provides no capability for conditional write
# operations, so we have to use a more manual process
# otherwise we could call save() on the DynamoDB item object
#
# db_item: DynamoDB item that we're trying to lock
def lock_item(db_item):
    time_limit = time.time() + ACQ_TIMEOUT

    # try to acquire lock until ACQ_TIMEOUT seconds have elapsed
    while time.time() < time_limit:
        timeout = time.time() + LOCK_TIMEOUT
        lockID = str(uuid.uuid4()) # create unique ID for lock

        # set lock on item if it is currently unlocked and unprocessed
        try:
            db_item['lock_id'] = lockID
            db_item['lockstamp'] = timeout

            # have to use conn.put_item to do a conditional write
            # prepare_full converts the item to the structure we need
            # then specify the conditions and convert to needed structure
            item_out = db_item.prepare_full()
            condition = {'lock_id':0, 'processed':0}
            exp = create_expected(condition)
            conn.put_item(TABLE_NAME, item_out, expected=exp)
            return lockID

        # if because conditional check failed, continue execution
        except dynamodb2.exceptions.ConditionalCheckFailedException, e:
            print db_item['filename'] + " is already locked or processed"

        # if we can't get lock, check if lock expired or item is processed
        updated_item = table.get_item(filename=db_item['filename'], consistent=True) # do a consistent read to get most updated version of item
        if updated_item['processed'] == 1:
            break
        elif updated_item['lockstamp'] < time.time():
            print "force releasing lock for %s, time %f < %f" %(db_item['filename'], float(updated_item['lockstamp']), time.time())
            # release stale lock
            new_lock = str(updated_item['lock_id'])
            if not release_item(updated_item, new_lock, processed=0):
                print "error releasing lock"
                break

    # if we can't get lock, give up
    print "could not get lock for item " + db_item['filename']
    return None

# this function creates a specially-formatted dict containing the
# conditions for a conditional write operation
# 
# conditions: dict in the format {'attr_1':val_1 ... 'attr_n':val_n} 
# that specifies the required value for each attribute
def create_expected(conditions):
    exp = dict()

    # jump through each input attribute and create the output dict
    for k in conditions.iterkeys():
        exp[k] = dict()
        exp[k]['Value'] = dict()

        # check if the value is number or string. Dynamo requires
        # an 'N' or 'S' to denote the value type
        if isinstance(conditions[k],int) or isinstance(conditions[k],float):
            exp[k]['Value']['N'] = str(conditions[k])
        elif isinstance(conditions[k], str):
            exp[k]['Value']['S'] = str(conditions[k])
        exp[k]['Exists'] = True

    return exp


# release the lock for an item in the database
#
# db_item: DynamoDB item
# lockID: string containing the target lockID
# processed: int specifying what the processed attribute should be set to
def release_item(db_item, lockID, processed=1):
    # release lock by resetting attributes
    db_item['lockstamp'] = 0.0
    db_item['lock_id'] = 0
    db_item['processed'] = processed

    try:
        # as before, prepare data structures for conditional write
        item_out = db_item.prepare_full()
        condition = {'lock_id':lockID, 'processed':0}
        exp = create_expected(condition)
        conn.put_item(TABLE_NAME, item_out, expected=exp)

    except dynamodb2.exceptions.ConditionalCheckFailedException, e:
        print "could not release lock for " + db_item['filename']
        return False

    return True

# query the DB every 5 seconds to get the unprocessed items
# try to acquire the lock on each item, then process and unlock it
if __name__ == "__main__":
    while(True):
        # get all items that are unprocesssed
        rs = table.query_2(processed__eq=0, index='processed-index')
        for item in rs:
            lock = lock_item(item) # try to acquire lock
            if lock:
                # if we get lock, process the item and release it
                print "processing data from " + item['filename']
                time.sleep(1) # simulate processing the data
                release_item(item, lock)
                print "processed data from " + item['filename']

        # wait before issuing next query
        time.sleep(5)
