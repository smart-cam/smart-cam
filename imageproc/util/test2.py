__author__ = 'ssatpati'

import time
import sys
import subprocess
import os

OUTPUT_FILE = os.path.expanduser('~') + '/videos1/tf.class.out'

rc = subprocess.call(['./tf_classify.sh','frame_1.png',OUTPUT_FILE])
print rc

d  = {}
with open(OUTPUT_FILE, 'r') as f:
    for l in f.readlines():
        t = l.split(":")
        d[t[0].strip()] = t[1].strip()

print d