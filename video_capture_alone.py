import numpy as np
import cv2
import time

cap = cv2.VideoCapture(0)
fps = cap.get(cv2.CAP_PROP_FPS)
print "Fps using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)
out = cv2.VideoWriter_fourcc(*'XVID')
out2 = cv2.VideoWriter('kk.avi',out,20.0,(640,480))
num_frames = 0
start = time.time()
while(num_frames < 100):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    out2.write(frame)
    num_frames += 1
    # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture

end = time.time()
seconds = end - start
fps  = num_frames / seconds;
print "Estimated frames per second : {0}".format(fps);

cap.release()
out2.release()
cv2.destroyAllWindows()