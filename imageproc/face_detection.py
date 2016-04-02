__author__ = 'ssatpati'

import json
import datetime
import cv2
import pprint
import numpy as np

from util.config import Config


class FaceDetection(object):

    #Enter the number of frames to be skipped if no face is found
    SKIP = 2

    def __init__(self):
        cfg = Config()
        opencv_home = cfg.get("face_detection", "opencv_home")
        self.face_cascade = cv2.CascadeClassifier('{0}/haarcascade_frontalface_default.xml'.format(opencv_home))
        self.eye_cascade = cv2.CascadeClassifier('{0}/haarcascade_eye.xml'.format(opencv_home))

    def __detect_faces(self,frame_id, frame):
        """Detect Faces"""

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_rects = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        print "\n### [{0}] Faces Detected: {1}\n{2}\n".format(frame_id, np.shape(faces_rects)[0], faces_rects)

        for (x, y, w, h) in faces_rects:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

        return faces_rects

    # Assuming video snippets won't contain more than a few face ROI(s)
    def __get_uniq_faces_curr_frame(self, frame_id, faces_roi_hists_prev, faces_roi_hists):
        print "\n### [{0}] Face Similarity: Prev: {1}, Curr: {2}".format(frame_id,
                                                                         len(faces_roi_hists_prev),
                                                                         len(faces_roi_hists))
        # First Time
        if len(faces_roi_hists_prev) == 0:
            return len(faces_roi_hists)

        uniq_faces_curr_frame = 0

        # Perform Image Histogram Similarity
        # For each histogram in current frame
        for rh1 in faces_roi_hists:
            match_found = False
            # For each histogram in previous frame
            for rh2 in faces_roi_hists_prev:
                #print "\nrh1 {0}: {1}".format(type(rh1),np.shape(rh1))
                #print "\nrh2 {0}: {1}".format(type(rh2),np.shape(rh2))
                corr = cv2.compareHist(rh1, rh2, cv2.HISTCMP_CORREL)
                print "### [{0}] Similarity Metrics: {1}".format(frame_id, corr)
                if corr >= 0.35:
                    # Match Found, can break the loop for this histogram in current frame
                    match_found = True
                    break;
            # Add to unique face count, if no match found for this histogram in current frame
            if not match_found:
                uniq_faces_curr_frame += 1

        print "### [{0}] Total Unique Faces in Current Frame: {1}\n".format(frame_id, uniq_faces_curr_frame)
        return uniq_faces_curr_frame


    def __get_roi_hist(self, faces_rects, frame):
        faces_roi_hists = []
        for (x, y, w, h) in faces_rects:
            roi = frame[y:y+h, x:x+w]
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
            roi_hist = cv2.calcHist([hsv_roi],[0], mask, [180], [0,180])
            roi_hist = cv2.normalize(roi_hist,roi_hist, 0, 255, cv2.NORM_MINMAX)
            faces_roi_hists.append(roi_hist)
        return faces_roi_hists


    def __get_range(self, l, increment=20):
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

        report['details'] = []
        for beg, end in self.__get_range(len(faces)):
            d = {}
            d['beg'] = beg
            d['end'] = end
            d['face_count'] = sum([i[1] for i in faces[beg:end]])
            d['face_count_uniq'] = sum([i[2] for i in faces[beg:end]])
            report['details'].append(d)

        return json.dumps(report)

    def process(self, video_file,show_frame=False):
        '''Main Point of Entry to Program'''
        start = datetime.datetime.now()

        faces = []
        total_est_uniq_faces = 0

        # Handle to Video
        cap = cv2.VideoCapture(video_file)

        # Hists from Prev Frames
        faces_roi_hists_prev = []

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
                    # Get the Histograms for the ROI(s) detected
                    faces_roi_hists = self.__get_roi_hist(faces_rects, frame)

                    # Detect Similar Faces
                    face_count_uniq = self.__get_uniq_faces_curr_frame(frame_id, faces_roi_hists_prev, faces_roi_hists)
                    total_est_uniq_faces += face_count_uniq

                    # Set Previous
                    faces_roi_hists_prev = faces_roi_hists
                else:
                    face_count_uniq = 0

                # Show the Frame
                if show_frame:
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                # Add the individual counts to list
                faces.append((frame_id,face_count,face_count_uniq))

                # Count
                print "\n### [{0}] Total Estimated Unique Faces so far: {1}".format(frame_id, total_est_uniq_faces)

                # For Debugging Purposes
                #if frame_id > 300:
                #    break
            except Exception as e:
                print e
                break

        cap.release()
        cv2.destroyAllWindows()

        report = self.__generate_report(faces, str(datetime.datetime.now() - start))

        return report


if __name__ == '__main__':
    fd = FaceDetection()
    report = fd.process('/Users/ssatpati/0-DATASCIENCE/DEV/github/W210_capstone/videos/video_1.avi')
    pprint.pprint(report)