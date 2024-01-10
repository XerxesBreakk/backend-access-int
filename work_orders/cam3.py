import cv2 as cv2
import cv2 as cv
import numpy as np
import os
from datetime import datetime, timedelta

FILE_OUTPUT = '/Users/saulmestanza/Desktop/keyboard/output.avi'

# Checks and deletes the output file
# You cant have a existing file or it will through an error
if os.path.isfile(FILE_OUTPUT):
    os.remove(FILE_OUTPUT)

# Playing video from file:
# cap = cv2.VideoCapture('vtest.avi')
# Capturing video from webcam:
ip_addr = '192.168.0.101'
stream_url = 'http://' + ip_addr + ':81/stream'  
cap = cv2.VideoCapture(stream_url)

currentFrame = 0


width = cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
height  = cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)


# Get current width of frame
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
# Get current height of frame
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float
# Define the codec and create VideoWriter object
# fourcc = cv2.CV_FOURCC(*'X264')
fourcc = cv2.VideoWriter_fourcc(*'X264')
out = cv2.VideoWriter(FILE_OUTPUT,fourcc, 20.0, (int(width),int(height)))

now = datetime.today()
future = now + timedelta(seconds=15)
# while(True):
while(cap.isOpened() and not now > future):
    now = datetime.today()
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret == True:
        # Handles the mirroring of the current frame
        frame = cv2.flip(frame,1)
        # Saves for video
        out.write(frame)
        print("write!")
        # Display the resulting frame
        cv2.imshow('frame',frame)
    else:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # To stop duplicate images
    currentFrame += 1

# When everything done, release the capture
cap.release()
out.release()
cv2.destroyAllWindows()