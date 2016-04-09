__author__ = 'ssatpati'

import time
import sys

print sys.argv

cnt = 50

while cnt > 0:
    print cnt, sys.argv
    cnt -= 1
    time.sleep(1)
