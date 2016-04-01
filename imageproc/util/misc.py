__author__ = 'ssatpati'
import boto
from config import Config
import os

def download_from_s3(bucket_name, key_name, local_out_dir='~/tmp'):
    cfg = Config()
    aws_access_key_id = cfg.get("aws", "access_key_id")
    aws_secret_access_key = cfg.get("aws", "secret_access_key")

    # connect to the bucket
    conn = boto.connect_s3(aws_access_key_id,
                    aws_secret_access_key)

    ret_val = (False, None)

    try:
        print("# S3: Fetching Bucket: {0} / Key: {1}".format(bucket_name, key_name))
        bucket = conn.get_bucket(bucket_name)
        key = bucket.get_key(key_name)
        if key:
            local_file = os.path.join(local_out_dir, os.path.basename(key_name))
            print '# S3: Saving contents to Local File - {0}'.format(local_file)
            key.get_contents_to_filename(local_file)
            ret_val = (True, os.path.abspath(local_file))
    except boto.exception.S3ResponseError as err:
        print(err)

    return ret_val


if __name__ == '__main__':
    print download_from_s3('w210-smartcam', 'videos/video_20.avi', '.')
    print download_from_s3('w210-smartcam', 'videos/video_6.avi', '.')