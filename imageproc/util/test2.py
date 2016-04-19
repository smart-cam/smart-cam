__author__ = 'ssatpati'

import time
import sys
import subprocess
import os

OUTPUT_DIR = os.path.expanduser('~') + '/videos1'

rc = subprocess.call(['./tf_classify.sh','frame_1.png',OUTPUT_DIR])