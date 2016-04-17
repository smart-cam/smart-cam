__author__ = 'ssatpati'

import json
import datetime
import cv2
import pprint
import numpy as np

from util.config import Config
from util import log

logger = log.getLogger(__name__)


class FaceDetectionV1(object):

    #Enter the number of frames to be skipped if no face is found
    SKIP = 2

    def __init__(self):
        cfg = Config()
        opencv_home = cfg.get("face_detection", "opencv_home")
        haarcascade = cfg.get("face_detection", "haarcascade")

        self.haarcascade = cv2.CascadeClassifier('{0}/{1}'.format(opencv_home,
                                                                  haarcascade))
        #self.eye_cascade = cv2.CascadeClassifier('{0}/haarcascade_eye.xml'.format(opencv_home))

    def __detect_faces(self,frame_id, frame):
        """Detect Faces"""

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_rects = self.haarcascade.detectMultiScale(gray, 1.3, 5)

        logger.info("[{0}] Faces Detected: {1}\n{2}\n".format(frame_id, np.shape(faces_rects)[0], faces_rects))

        for (x, y, w, h) in faces_rects:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

        return faces_rects


    def __get_roi(self, faces_rects, frame):
        faces_roi = []
        for (x, y, w, h) in faces_rects:
            roi = frame[y:y+h, x:x+w]
            faces_roi.append(roi)
        return faces_roi

     # Assuming video snippets won't contain more than a few face ROI(s)
    def __get_uniq_faces_curr_frame_template_match(self, frame_id, frame_prev, faces_roi):
        logger.info("[{0}] Face Similarity: # of faces in current frame - {1}".format(frame_id,
                                                                                len(faces_roi)))
        # First Time
        if frame_prev.size == 0:
            return len(faces_roi)

        uniq_faces_curr_frame = 0

        for template_roi in faces_roi:
            # Apply template Matching
            res = cv2.matchTemplate(frame_prev,
                                    template_roi,
                                    cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            logger.info("[{0}] {1},{2},{3},{4}".format(frame_id, min_val, max_val, min_loc, max_loc))



        logger.info("[{0}] Total Unique Faces in Current Frame: {1}".format(frame_id, uniq_faces_curr_frame))
        return uniq_faces_curr_frame


    def __get_range(self, l, increment=10):
        # Default
        beg = 0
        end = 0
        while end < l:
            beg = end
            if beg + increment < l:
                end = beg + increment
            else:
                end = l
            yield (beg, end)


    def __generate_report(self, faces, time_taken):
        report = {}

        report['face_count'] = sum([i[1] for i in faces])
        report['face_count_uniq'] = sum([i[2] for i in faces])
        report['frame_count'] = len(faces)
        report['time_taken'] = time_taken

        face_count_dtl = []
        face_count_uniq_dtl = []

        for beg, end in self.__get_range(len(faces)):
            face_count_dtl.append(str(sum([i[1] for i in faces[beg:end]])))
            face_count_uniq_dtl.append(str(sum([i[2] for i in faces[beg:end]])))

        report['face_count_dtl'] = face_count_dtl
        report['face_count_uniq_dtl'] = face_count_uniq_dtl

        return report

    def process(self, video_file,show_frame=False):
        '''Main Point of Entry to Program'''
        start = datetime.datetime.now()

        faces = []
        total_est_uniq_faces = 0

        # Handle to Video
        cap = cv2.VideoCapture(video_file)

        # Prev Frame
        frame_prev = np.array([])

        frame_id = 0
        # For each Frame
        while cap.isOpened():
            try:
                ret, frame = cap.read()

                if not ret:
                    break

                frame_id += 1

                # Get the Face ROI from Viola Jones
                faces_rects = self.__detect_faces(frame_id, frame)

                # Increment Total Face Count
                face_count = np.shape(faces_rects)[0]

                # If Faces Detected
                if np.shape(faces_rects)[0] > 0:
                    # Get the the ROI(s) for detected faces
                    faces_roi = self.__get_roi(faces_rects, frame)

                    # Detect Similar Faces
                    face_count_uniq = self.__get_uniq_faces_curr_frame_template_match(frame_id, frame_prev, faces_roi)
                    total_est_uniq_faces += face_count_uniq
                else:
                    face_count_uniq = 0

                # Set Previous
                frame_prev = frame

                # Show the Frame
                if show_frame:
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                # Add the individual counts to list
                faces.append((frame_id,face_count,face_count_uniq))

                # Count
                logger.info("[{0}] Total Estimated Unique Faces so far: {1}\n".format(frame_id, total_est_uniq_faces))

                # For Debugging Purposes
                #if frame_id > 300:
                #    break
            except Exception as e:
                logger.error(e)
                break

        cap.release()
        cv2.destroyAllWindows()

        report = self.__generate_report(faces, str(datetime.datetime.now() - start))

        return report


if __name__ == '__main__':
    fd = FaceDetection()
    #report = fd.process('/Users/ssatpati/0-DATASCIENCE/DEV/github/smart-cam/resources/video.avi')
    report = fd.process('/Users/ssatpati/0-DATASCIENCE/DEV/github/smart-cam/videos/video_3.avi')
    pprint.pprint(report)