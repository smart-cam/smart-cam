__author__ = 'ssatpati'
import boto
from boto.s3.key import Key
from config import Config
import os


def upload_to_s3(bucket_name, key_name, video_file):
    cfg = Config()
    # connect to the bucket
    conn = boto.connect_s3(cfg.get("aws", "access_key_id"),
                            cfg.get("aws", "secret_access_key"))

    ret_val = False

    try:
        print("# S3: Uploading to Bucket: {0} / Video|Key: {1}".format(bucket_name, video_file))
        bucket = conn.get_bucket(bucket_name)
        k = Key(bucket)
        if key_name:
            k.key = key_name
        else:
            k.key = os.path.basename(video_file)
        k.set_contents_from_filename(video_file)
        ret_val = True
    except boto.exception.S3ResponseError as err:
        print(err)

    return ret_val


def download_from_s3(bucket_name, key_name, local_out_dir='/tmp'):
    cfg = Config()
    # connect to the bucket
    conn = boto.connect_s3(cfg.get("aws", "access_key_id"),
                            cfg.get("aws", "secret_access_key"))

    ret_val = (False, None)

    try:
        print("# S3: Fetching Bucket: {0} / Key: {1}".format(bucket_name, key_name))
        bucket = conn.get_bucket(bucket_name)
        key = bucket.get_key(key_name)
        if key:
            local_file = os.path.join(local_out_dir, os.path.basename(key_name))
            print '# S3: Saving contents to Local File - {0}'.format(local_file)
            key.get_contents_to_filename(local_file, response_headers={
                                                'response-content-type': 'video/avi'
                                            })
            ret_val = (True, os.path.abspath(local_file))
    except boto.exception.S3ResponseError as err:
        print(err)

    return ret_val


def delete_keys(bucket_name, key_pattern):
    cfg = Config()
    # connect to the bucket
    conn = boto.connect_s3(cfg.get("aws", "access_key_id"),
                            cfg.get("aws", "secret_access_key"))

    ret_val = True

    try:
        print("# S3: Fetching Keys from Bucket: {0}".format(bucket_name))
        bucket = conn.get_bucket(bucket_name)

        for key in bucket.get_all_keys():
            print key
            if os.path.basename(key.name).startswith(key_pattern):
                key.delete()
                print 'Deleted {0}'.format(key.name)
    except boto.exception.S3ResponseError as err:
        print(err)
        ret_val = False

    return ret_val


def create_bucket(bucket_name):
    '''Create Bucket: CAUTION ### It deletes the bucket'''
    cfg = Config()
    # connect to the bucket
    conn = boto.connect_s3(cfg.get("aws", "access_key_id"),
                            cfg.get("aws", "secret_access_key"))

    ret_val = False

    try:
        print("# S3: Deleting/Creating Bucket: {0}".format(bucket_name))
        bucket = conn.get_bucket(bucket_name)
        # Delete Files
        print("Deleting Files in S3 Bucket - {0}".format(bucket_name))
        for key in bucket.list():
            key.delete()
        print("Deleting S3 Bucket - {0}".format(bucket_name))
        # Delete Bucket
        conn.delete_bucket(bucket_name)
    except boto.exception.S3ResponseError as err:
        print(err)

    try:
        bucket = conn.create_bucket(bucket_name)
        ret_val = True
    except boto.exception.S3ResponseError as err:
        print(err)

    return ret_val




if __name__ == '__main__':
    BUCKET_NAME = 'smart-cam'
    N = 6

    '''
    print create_bucket(BUCKET_NAME)

    for i in xrange(1, N+1):
        print upload_to_s3(BUCKET_NAME,
                           'videos/video_{0}.avi'.format(i),
                           '/Users/ssatpati/0-DATASCIENCE/DEV/github/smart-cam/resources/video.avi')
    '''

    delete_keys(BUCKET_NAME, 'Entrance_')
