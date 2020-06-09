import sys
import time

import cv2 as cv

from file_utils import get_all_files, get_frame_GREY

tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'CSRT']
tracker_type = tracker_types[2]

if tracker_type == 'BOOSTING':
    tracker = cv.TrackerBoosting_create()
if tracker_type == 'MIL':
    tracker = cv.TrackerMIL_create()
if tracker_type == 'KCF':
    tracker = cv.TrackerKCF_create()
if tracker_type == 'TLD':
    tracker = cv.TrackerTLD_create()
if tracker_type == 'MEDIANFLOW':
    tracker = cv.TrackerMedianFlow_create()
if tracker_type == 'GOTURN':
    tracker = cv.TrackerGOTURN_create()
if tracker_type == "CSRT":
    tracker = cv.TrackerCSRT_create()


data_path = "testpics"
files = get_all_files(data_path)
frame = cv.imread(files[0])
print('shape={}'.format(frame.shape))
gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
blurred_img = cv.medianBlur(frame,5)
_, gray = cv.threshold(blurred_img,127,255,cv.THRESH_BINARY)

# Define an initial bounding box
bbox = (258, 60, 108, 80)

# Uncomment the line below to select a different bounding box
# bbox = cv.selectROI(frame, False)
print(bbox)

# Initialize tracker with first frame and bounding box
ok = tracker.init(gray, bbox)
counter = 0
while counter < len(files):
    # Start timer
    timer = cv.getTickCount()
    frame = cv.imread(files[counter])
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    blurred_img = cv.medianBlur(frame,5)
    _, gray = cv.threshold(blurred_img,127,255,cv.THRESH_BINARY)

    # Update tracker
    ok, bbox = tracker.update(gray)

    # Calculate Frames per second (FPS)
    fps = cv.getTickFrequency() / (cv.getTickCount() - timer)

    # Draw bounding box
    if ok:
        # Tracking success
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv.rectangle(frame, p1, p2, (255,0,0), 2, 1)
    else :
        # Tracking failure
        cv.putText(frame, "Tracking failure detected", (100,80), cv.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

    # Display tracker type on frame
    cv.putText(frame, tracker_type + " Tracker", (100,20), cv.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)

    # Display FPS on frame
    cv.putText(frame, "FPS : " + str(int(fps)), (100,50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2)


    # Display result
    cv.imshow("Tracking", frame)
    counter += 1

    # Exit if ESC pressed
    k = cv.waitKey(1) & 0xff
    if k == 27 : break
