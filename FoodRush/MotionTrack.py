import cv2
import numpy as np

# lower_green = np.array([29, 86, 6])
# upper_green = np.array([64, 255, 255])

lower_yellow = np.array([5, 100, 100])
upper_yellow = np.array([30, 255, 255])

def motionTrack(cap, heroSprite):
    retBool, frame = cap.read()
    window_name = "MotionTrack"
    desired_size = 640.0

    if frame is not None:
        # Get the size of the image, which is a numpy array
        size = frame.shape
        # resize the image to fit in our window, while
        # maintaining an aspect ratio
        fx = desired_size / size[0]
        fy = desired_size / size[1]

        resized = cv2.resize(frame, (0, 0), fx=fy, fy=fx) # Resize the window to be a square.

        # Draw four boxes to indicate the right area for player to move to.
        cv2.rectangle(resized, (165, 5), (475, 165), (0, 0, 0), 5)
        cv2.rectangle(resized, (165, 475), (475, 635), (0, 0, 0), 5)
        cv2.rectangle(resized, (5, 165), (165, 475), (0, 0, 0), 5)
        cv2.rectangle(resized, (475, 165), (635, 475), (0, 0, 0), 5)

        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
        # Threshold the HSV image to get only orange color
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        # get rid of background noise.
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[0]
        center = None

        # only proceed if at least one contour was found
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 10:
                cv2.circle(resized, center, 20, (0, 0, 255), -1)

        if (center != None):
            if ((165 < center[0] < 475) and (5 < center[1] < 165)):
                cv2.rectangle(resized, (165, 5), (475, 165), (0, 255, 255), 5)
                heroSprite.deltaY = -0.1
                heroSprite.heroMoved = True
            elif ((165 < center[0] < 475) and (475 < center[1] < 635)):
                cv2.rectangle(resized, (165, 475), (475, 635), (0, 255, 255), 5)
                heroSprite.deltaY = 0.1
                heroSprite.heroMoved = True
            elif ((5 < center[0] < 165) and (165 < center[1] < 475)):
                cv2.rectangle(resized, (5, 165), (165, 475), (0, 255, 255), 5)
                heroSprite.deltaX = 0.1
                heroSprite.heroMoved = True
            elif ((475 < center[0] < 635) and (165 < center[1] < 475)):
                cv2.rectangle(resized, (475, 165), (635, 475), (0, 255, 255), 5)
                heroSprite.deltaX = -0.1
                heroSprite.heroMoved = True

        # Flip our frame horizontally for better game experience.
        flipped = cv2.flip(resized, 1)

        # Display flipped frame in a window with window_name
        cv2.imshow(window_name, flipped)
