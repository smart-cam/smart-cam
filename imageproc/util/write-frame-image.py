__author__ = 'ssatpati'

import cv2
import os
import shutil

OUTPUT_DIR = '/Users/ssatpati/tmp/face_detection/frames'
video_file = '/Users/ssatpati/Downloads/Entrance_1460869203.882519.mp4'

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

cap = cv2.VideoCapture(video_file)
cnt = 1

while cap.isOpened():
    try:
        ret, frame = cap.read()

        if not ret:
            break

        cv2.imwrite('{0}/frame_{1}.png'.format(OUTPUT_DIR, cnt),frame)

        cnt += 1

    except Exception as e:
        print e
        break

cap.release()
cv2.destroyAllWindows()
