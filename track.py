#!/usr/bin/env/python3
'''
    Author: Yuan PJ <yuan0925pj@gmail.com>
'''

#Import the OpenCV and dlib libraries
import cv2
import dlib
import time
import RPi.GPIO as GPIO
from imutils.video import VideoStream

#Initialize a face cascade using the frontal face haar cascade provided with
#the OpenCV library
faceCascade = cv2.CascadeClassifier('/home/pi/code/face-recognition/haarcascades/haarcascade_frontalface_default.xml')

#The deisred output width and height
OUTPUT_SIZE_WIDTH = 775
OUTPUT_SIZE_HEIGHT = 600

#Setup GPIO
GPIO.setmode(GPIO.BCM)
LEFT = 20
RIGHT = 21
UP = 23
DOWN = 24
LED = 26
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(LEFT, GPIO.OUT) #Yellow
GPIO.setup(RIGHT, GPIO.OUT) #Green
GPIO.setup(UP, GPIO.OUT) #Red
GPIO.setup(DOWN, GPIO.OUT) #Orange
#GPIO.output(LEFT, GPIO.LOW)
#GPIO.output(RIGHT, GPIO.LOW)
#GPIO.output(UP, GPIO.LOW)
#GPIO.output(DOWN, GPIO.LOW)

def detectAndTrackLargestFace():
    #Open the first webcame device
    #capture = cv2.VideoCapture(0)
    capture = VideoStream(src=0).start()
    time.sleep(3)

    #Create two opencv named windows
    #cv2.namedWindow("base-image", cv2.WINDOW_AUTOSIZE)
    #cv2.namedWindow("result-image", cv2.WINDOW_AUTOSIZE)

    #Position the windows next to eachother
    #cv2.moveWindow("base-image",0,100)
    #cv2.moveWindow("result-image",400,100)

    #Start the window thread for the two windows we are using
    #cv2.startWindowThread()

    #Create the tracker we will use
    tracker = dlib.correlation_tracker()

    #The variable we use to keep track of the fact whether we are
    #currently using the dlib tracker
    trackingFace = 0

    #The color of the rectangle we draw around the face
    rectangleColor = (0,165,255)

    #Set threshold border
    left_x  = 100
    right_x = 230
    top_y = 50
    bottom_y = 140

    try:
        while True:
            #Retrieve the latest image from the webcam
            #rc, fullSizeBaseImage = capture.read()
            fullSizeBaseImage = capture.read()
            if fullSizeBaseImage is None:
                time.sleep(0.1)
                continue

            #Resize the image to 320x240
            baseImage = cv2.resize( fullSizeBaseImage, ( 320, 240))


            #Check if a key was pressed and if it was Q, then destroy all
            #opencv windows and exit the application
            pressedKey = cv2.waitKey(2)
            if pressedKey == ord('Q'):
                cv2.destroyAllWindows()
                GPIO.cleanup()
                exit(0)



            #Result image is the image we will show the user, which is a
            #combination of the original image from the webcam and the
            #overlayed rectangle for the largest face
            #resultImage = baseImage.copy()






            #If we are not tracking a face, then try to detect one
            if not trackingFace:
                GPIO.output(LED, GPIO.LOW)

                GPIO.output(LEFT, GPIO.LOW)
                GPIO.output(RIGHT, GPIO.LOW)
                GPIO.output(UP, GPIO.LOW)
                GPIO.output(DOWN, GPIO.LOW)
                
                #For the face detection, we need to make use of a gray
                #colored image so we will convert the baseImage to a
                #gray-based image
                gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)
                #Now use the haar cascade detector to find all faces
                #in the image
                faces = faceCascade.detectMultiScale(gray, 1.3, 5)

                #In the console we can show that only now we are
                #using the detector for a face
                #print("Using the cascade detector to detect face")


                #For now, we are only interested in the 'largest'
                #face, and we determine this based on the largest
                #area of the found rectangle. First initialize the
                #required variables to 0
                maxArea = 0
                x = 0
                y = 0
                w = 0
                h = 0


                #Loop over all faces and check if the area for this
                #face is the largest so far
                #We need to convert it to int here because of the
                #requirement of the dlib tracker. If we omit the cast to
                #int here, you will get cast errors since the detector
                #returns numpy.int32 and the tracker requires an int
                for (_x,_y,_w,_h) in faces:
                    if  _w*_h > maxArea:
                        x = int(_x)
                        y = int(_y)
                        w = int(_w)
                        h = int(_h)
                        maxArea = w*h

                #If one or more faces are found, initialize the tracker
                #on the largest face in the picture
                if maxArea > 0 :

                    #Initialize the tracker
                    tracker.start_track(baseImage,
                                        dlib.rectangle( x-10,
                                                        y-20,
                                                        x+w+10,
                                                        y+h+20))

                    #Set the indicator variable such that we know the
                    #tracker is tracking a region in the image
                    trackingFace = 1

            #Check if the tracker is actively tracking a region in the image
            if trackingFace:

                #Update the tracker and request information about the
                #quality of the tracking update
                trackingQuality = tracker.update( baseImage )



                #If the tracking quality is good enough, determine the
                #updated position of the tracked region and draw the
                #rectangle
                if trackingQuality >= 7:
                    tracked_position =  tracker.get_position()

                    t_x = int(tracked_position.left())
                    t_y = int(tracked_position.top())
                    t_w = int(tracked_position.width())
                    t_h = int(tracked_position.height())
                    #cv2.rectangle(resultImage, (t_x, t_y),
                    #                            (t_x + t_w , t_y + t_h),
                    #                            rectangleColor ,2)
                    pos_x = t_x + t_w/2
                    pos_y = t_y + t_h/2
                    print(pos_x, pos_y)
                    #print(left_x, pos_x, right_x)
                    #print(bottom_y, pos_y, top_y)
                    GPIO.output(LED, GPIO.HIGH)
                    if pos_x > right_x:
                        GPIO.output(RIGHT, GPIO.HIGH)
                        GPIO.output(LEFT, GPIO.LOW)
                    elif pos_x < left_x:
                        GPIO.output(LEFT, GPIO.HIGH)
                        GPIO.output(RIGHT, GPIO.LOW)
                    else:
                        GPIO.output(RIGHT, GPIO.LOW)
                        GPIO.output(LEFT, GPIO.LOW)
                    if pos_y < top_y:
                        GPIO.output(DOWN, GPIO.HIGH)
                        GPIO.output(UP, GPIO.LOW)
                    elif pos_y > bottom_y:
                        GPIO.output(UP, GPIO.HIGH)
                        GPIO.output(DOWN, GPIO.LOW)
                    else:
                        GPIO.output(UP, GPIO.LOW)
                        GPIO.output(DOWN, GPIO.LOW)


                else:
                    #If the quality of the tracking update is not
                    #sufficient (e.g. the tracked region moved out of the
                    #screen) we stop the tracking of the face and in the
                    #next loop we will find the largest face in the image
                    #again
                    trackingFace = 0





            #Since we want to show something larger on the screen than the
            #original 320x240, we resize the image again
            #
            #Note that it would also be possible to keep the large version
            #of the baseimage and make the result image a copy of this large
            #base image and use the scaling factor to draw the rectangle
            #at the right coordinates.
            #largeResult = cv2.resize(resultImage,
            #                         (OUTPUT_SIZE_WIDTH,OUTPUT_SIZE_HEIGHT))

            #Finally, we want to show the images on the screen
            #cv2.imshow("base-image", baseImage)
            #cv2.imshow("result-image", largeResult)




    #To ensure we can also deal with the user pressing Ctrl-C in the console
    #we have to check for the KeyboardInterrupt exception and destroy
    #all opencv windows and exit the application
    except KeyboardInterrupt as e:
        cv2.destroyAllWindows()
        GPIO.cleanup()
        exit(0)


if __name__ == '__main__':
    detectAndTrackLargestFace()
