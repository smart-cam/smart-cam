import cv2
import os
import numpy as np
import sys
import boto
from boto.dynamodb2.table import Table

from util.config import Config
from util import misc

# use ~/videos as temporary directory for downloaded videos
OUTPUT_DIR = os.path.expanduser('~') + '/videos'

class FaceRec(object):

    def __init__(self):
        cfg = Config()
        # set up face detection models
        opencv_home = cfg.get("face_detection", "opencv_home")
        haarcascade = cfg.get("face_detection", "haarcascade")
        cascadePath = "/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml"
        self.faceCascade = cv2.CascadeClassifier('{0}/{1}'.format(opencv_home, haarcascade))

        self.recognizer = cv2.face.createLBPHFaceRecognizer()
        #self.recognizer = cv2.face.createEigenFaceRecognizer()
        #self.recognizer = cv2.face.createFisherFaceRecognizer()

        # the faces and Raspberry Pi locations we'll use
        self.names = ["james", "juanjo", "sayantan", "vineet"]
        self.rasp_names = ["FrontDoor", "Entrance", "Garage"]
        access = cfg.get("aws", "access_key_id")
        secret = cfg.get("aws", "secret_access_key")

        # connect to dynamo
        self.conn = boto.dynamodb2.connect_to_region('us-west-1', aws_access_key_id=access, aws_secret_access_key=secret)
        self.sc = Table('SMARTCAM', connection=self.conn)


    # read in training set and train the model
    def trainModel(self, path):
        image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('jpg')]
        images = []
        labels = []

        # extract coordinates of face in each training photo
        for image_path in image_paths:
            try:
                image = cv2.imread(image_path, 0)
                faces = self.faceCascade.detectMultiScale(image, 1.3, 4)
            except Exception, e:
                print "trouble with " + image_path
                print e
                
            # get lables and set up training set
            label = self.names.index(os.path.split(image_path)[-1].split('_')[0])
            for (x, y, w, h) in faces:
                images.append(image[y: y + h, x: x + w])
                labels.append(label)
                print "adding " + image_path + " " + str(self.names[label])
                #cv2.imshow("Adding faces to traning set...", image[y: y + h, x: x + w])
                #cv2.waitKey(0)

        # train the model
        self.recognizer.train(images, np.array(labels))


    # give predictions for all videos in a directory
    # this is mainly for testing a model
    def predictFaces(self, path):
        #cv2.destroyAllWindows()

        image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('jpg')]

        for image_path in image_paths:
            # load image and identify coordinates of each face
            pred_image = cv2.imread(image_path, 0)
            faces = self.faceCascade.detectMultiScale(pred_image, 1.3, 4)

            # for each face, predict the match
            for (x, y, w, h) in faces:
                pred, conf = self.recognizer.predict(pred_image[y: y + h, x: x + w])
                actual = self.names.index(os.path.split(image_path)[-1].split('_')[0])

                # report result and show the face
                if pred == actual:
                    print "%d is correctly recognized with confidence %f" %(actual, conf)
                else:
                    print "%d is incorrectly recognized as %d" %(actual, pred)

                cv2.imshow("Recognizing Face", pred_image[y: y + h, x: x + w])
                cv2.waitKey(0)


    # give predictions from a single frame
    # frame is the grayscale image
    # faces contains the coordinates for each detected face
    def predictSingle(self, frame, faces):
        for (x, y, w, h) in faces:
            pred, conf = self.recognizer.predict(frame[y: y + h, x: x + w])
            print "recognized face as %s, conf %f" %(self.names[pred], conf)
            #cv2.imshow("Recognized Face", frame[y: y + h, x: x + w    ])
            #cv2.waitKey(0)

            # only return a match if confidence (distance) is under 151
            if conf < 151.0:
                return self.names[pred]
            else:
                return None

    # run facial recognition on single video
    def process(self, video_file):
        cap = cv2.VideoCapture(video_file)

        frame_id = 0
        rec_faces = []

        # open the video and read each frame
        while cap.isOpened():
            try:
                ret, frame = cap.read()

                if not ret:
                    break

                # convert frame to grayscale and detect faces
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.faceCascade.detectMultiScale(gray, 1.3, 5)

                # run facial recognition on the detected faces
                pred = self.predictSingle(gray, faces)
                #cv2.destroyAllWindows()
                
                if pred and pred not in rec_faces: 
                    rec_faces.append(pred)

            except ValueError, e:
                print e
                break

        # print out the faces detected
        print rec_faces
        return rec_faces


    # query dynamo to get a video and process it
    def queryDB(self):
        # run through each of the cameras
        for rasp in self.rasp_names:
            print "processing " + rasp
            ret = self.sc.query_2(RASP_NAME__eq=rasp)

            # only process videos that have not been looked at AND have
            # non-zero face count
            for item in ret:
                print "processing " + item['S3_KEY'][7:]
                if ('FACE_COMPLETE' not in item or item['FACE_COMPLETE'] != 1) and item['FACE_COUNT'] > 0:

                    # download video to local directory
                    ret_status, local_file = misc.download_from_s3(item['S3_BUCKET'], item['S3_KEY'], OUTPUT_DIR)
                    if ret_status:

                        # run facial recognition
                        faces = self.process(local_file)
                        os.remove(local_file)

                        # if there are matches, write back to dynamo
                        if faces:
                            item['FACES'] = ','.join(faces)
                            item['FACE_COMPLETE'] = 1
                            print item['FACES'], item['FACE_COMPLETE']
                            item.save()


if __name__ == '__main__':
    path = "rec2"           # training set directory
    target = "test_videos"  # test set directory
    fr = FaceRec()

    fr.trainModel(path)
    #fr.predictFaces(path)
    
    # take one pass throough the database for facial recognition
    # we can loop this to have it poll instead
    fr.queryDB()
