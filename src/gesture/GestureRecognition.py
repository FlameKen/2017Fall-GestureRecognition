import cv2
import numpy as np
import math
import time
import socket
from imutils.video import VideoStream

import sys

# Main part of gesture_hci
class App(object):
    def __init__(self, video_src):
        #self.cam = cv2.VideoCapture(video_src)
        self.cam = VideoStream(usePiCamera=True).start()
        #self.cam.start()
        self.frame = self.cam.read()
        
        # set channel range of skin detection 
        self.mask_lower_yrb = np.array([41, 142, 109])       # [54, 131, 110]
        self.mask_upper_yrb = np.array([250, 174, 147])     # [163, 157, 135]
        # create trackbar for skin calibration
        self.calib_switch = False

        # create background subtractor 
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=10)

        # define dynamic ROI area
        self.ROIx, self.ROIy = 0, 0;#self.frame.shape[1]/2, self.frame.shape[0]/2
        self.track_switch = True
        # record previous positions of the centroid of ROI
        self.preCX = None
        self.preCY = None

        # A queue to record last couple gesture command
        self.last_cmds = FixedQueue()
        
        # switch to turn on mouse input control
        self.cmd_switch = False
        
        # count loop (frame), for debugging
        self.n_frame = 0


# On-line Calibration for skin detection (bug, not stable)
    def skin_calib(self, raw_yrb):
        mask_skin = cv2.inRange(raw_yrb, self.mask_lower_yrb, self.mask_upper_yrb)
        cal_skin = cv2.bitwise_and(raw_yrb, raw_yrb, mask=mask_skin)

        ymin = cv2.getTrackbarPos('Ymin', 'YRB_calib')
        ymax = cv2.getTrackbarPos('Ymax', 'YRB_calib')
        rmin = cv2.getTrackbarPos('CRmin', 'YRB_calib')
        rmax = cv2.getTrackbarPos('CRmax', 'YRB_calib')
        bmin = cv2.getTrackbarPos('CBmin', 'YRB_calib')
        bmax = cv2.getTrackbarPos('CBmax', 'YRB_calib')
        self.mask_lower_yrb = np.array([ymin, rmin, bmin])
        self.mask_upper_yrb = np.array([ymax, rmax, bmax])


# Do skin detection with some filtering
    def skin_detect(self, raw_yrb, img_src):
        # use median blurring to remove signal noise in YCRCB domain
        raw_yrb = cv2.medianBlur(raw_yrb, 5)
        mask_skin = cv2.inRange(raw_yrb, self.mask_lower_yrb, self.mask_upper_yrb)

        # morphological transform to remove unwanted part
        kernel = np.ones((8, 8), np.uint8)

        res_skin = cv2.bitwise_and(img_src, img_src, mask=mask_skin)
        #res_skin_dn = cv2.fastNlMeansDenoisingColored(res_skin, None, 10, 10, 7,21)

        return res_skin


# Update Position of ROI
    def update_ROI(self, img_src):
        Rxmin, Rymin = 0, 0
        Rxmax, Rymax = img_src.shape[1]-1, img_src.shape[0]-1
        return Rxmin, Rymin, Rxmax, Rymax


# Find contour and track hand inside ROI
    def find_contour(self, img_src, Rxmin, Rymin, Rxmax, Rymax):
        cv2.rectangle(img_src, (Rxmax, Rymax), (Rxmin, Rymin), (0, 255, 0), 0)
        crop_res = img_src#[Rymin: Rymax, Rxmin:Rxmax]
        grey = cv2.cvtColor(crop_res, cv2.COLOR_BGR2GRAY)

        _, thresh1 = cv2.threshold(grey, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        #cv2.imshow('Thresh', thresh1)
        _, contours, hierchy = cv2.findContours(thresh1.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # draw contour on threshold image
        if len(contours) > 0:
            cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)

        return contours, crop_res


# Check ConvexHull  and Convexity Defects
    def get_defects(self, cnt, drawing):
        defects = None        
        hull = cv2.convexHull(cnt)
        cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
        cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 0)
        hull = cv2.convexHull(cnt, returnPoints=False)       # For finding defects
        if hull.size > 2:
            defects = cv2.convexityDefects(cnt, hull)        
        
        return defects


# Gesture Recognition
    def gesture_recognize(self, cnt, defects, count_defects, crop_res):
        # use angle between start, end, defect to recognize # of finger show up
        angles = []
        if defects is not None and cv2.contourArea(cnt) >= 1800:
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                far = tuple(cnt[f][0])
                a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 180/math.pi
                if start[1] == len(crop_res)-2 and end[1] == len(crop_res)-2:
                    break
                if angle <= 90:
                    angles.append(angle)
                    count_defects += 1
                    cv2.circle(crop_res, start, 5, [255, 255, 0], -1)
                    cv2.circle(crop_res, end, 5, [255, 255, 0], -1)
                    cv2.circle(crop_res, far, 5, [0, 0, 255], -1)
                cv2.line(crop_res, start, end, [0, 255, 0], 2)
                
        gesture = 'gesture'
        if count_defects == 1:
            if angles[0] > 35:
                gesture = 'seven'
            else:
                gesture = 'two'
        elif count_defects == 2:
            gesture = 'three'
        elif count_defects == 3:
            gesture = 'four'
        elif count_defects == 4:
            gesture = 'five'
        elif count_defects == 5:
            if cv2.contourArea(cnt) > 20000:
                gesture = 'one'
            else:
                gesture = 'one'
        # return the result of gesture recognition
        return count_defects, gesture

# Use PyAutoGUI to control mouse event
    def input_control(self, count_defects, img_src, gesture):
        # update position difference with previous frame (for move mouse)
        d_x, d_y = 0, 0
        if self.preCX is not None:
            d_x = self.ROIx - self.preCX
            d_y = self.ROIy - self.preCY
        
        # checking current command, and filter out unstable hand gesture
        cur_cmd = 0
        if self.cmd_switch:
            if self.last_cmds.count(count_defects) >= self.last_cmds.n_maj:
                cur_cmd = count_defects
                #print 'major command is ', cur_cmd
            else:
                cur_cmd = 0     # self.last_cmds.major()
        else:
            cur_cmd = count_defects
        

# main function of the project (run all processes)
    def run(self):
        while True:
        #while self.cam.isOpened():
            if self.n_frame == 0:
                ini_time = time.time()
            #ret, self.frame = self.cam.read()
            self.frame = self.cam.read()
            if self.frame is None:
                time.sleep(0.1)
                continue
            self.frame = cv2.flip(self.frame, 1)
            org_vis = self.frame.copy()
            #org_vis = cv2.fastNlMeansDenoisingColored(self.frame, None, 10,10,7,21) # try to denoise but time comsuming

            ### Skin detect filter
            yrb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2YCR_CB)
            res_skin = self.skin_detect(yrb, org_vis)
			
            ## check if want to do skin calibration
            if self.calib_switch:
                self.skin_calib(yrb)
            
            org_fg = res_skin
            
            ### Find Contours and track hand inside ROI
            Rxmin, Rymin, Rxmax, Rymax = self.update_ROI(org_fg)
            contours, crop_res = self.find_contour(org_fg, Rxmin, Rymin, Rxmax, Rymax)
            
            ### Get Convexity Defects if Contour in ROI is bigger enough 
            drawing = np.zeros(crop_res.shape, np.uint8)
            min_area = 1000
            max_area = 8500
            cnts = []

            areas = []
            gestures = []
            Ms = []
            if len(contours) > 0:
                for i in range(len(contours)):
                    cnt = contours[i]
                    area = cv2.contourArea(cnt)
                    areas.append(area)
                    if area > min_area and area < max_area:
                        cnts.append(cnt)
                
                for cnt in cnts:
                    # use minimum rectangle to crop contour for faster gesture checking
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(crop_res, (x, y), (x+w, y+h), (0, 0, 255), 0)

                    # debug draw a  circle at center
                    M = cv2.moments(cnt)
                    if M['m00'] != 0:
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])
                        cv2.circle(org_fg, (cx+Rxmin, cy+Rymin), 10, [0, 255, 255], -1)
                    
                    ### Check ConvexHull  and Convexity Defects
                    defects = self.get_defects(cnt, drawing)

                    ### Gesture Recognition
                    count_defects = 0
                    count_defects, gesture = self.gesture_recognize(cnt, defects, count_defects, crop_res)

                    ### Input Control (Mouse Event)
                    self.input_control(count_defects, org_fg, gesture)
                    gestures.append(gesture)
                    Ms.append((cx+Rxmin, cy+Rymin))
                    # update center position of ROI for next frame
                    self.preCX = self.ROIx
                    self.preCY = self.ROIy
            
            print(gestures)
            print(Ms)
            mesg = ""
            
            
            if len(Ms) == 1:
                mesg = str(gestures[0])
                x = Ms[0][0]
                y = Ms[0][1]
                c = math.sqrt((x - 160)**2 + (y - 120)**2)
                theta = math.atan2(y-120, x-160) * 180 / math.pi
                if c < 20:
                    mesg = mesg + "_click"
                else:
                    mesg = mesg + "_rot " + str(theta)
            elif len(Ms) == 2:
                m1x = Ms[0][0]
                m2x = Ms[1][0]
                m1y= Ms[0][1]
                m2y = Ms[1][1]
                if m1x < m2x:
                    mesg = mesg + str(gestures[1])
                    if m2y < 100:
                        mesg = mesg + "_up"
                    else:
                        mesg = mesg + "_down"
                    mesg = mesg + ","
                    mesg = mesg + str(gestures[0])
                    if m1y < 100:
                        mesg = mesg + "_up"
                    else:
                        mesg = mesg + "_down"
                else:
                    mesg = mesg + str(gestures[0])
                    if m1y < 100:
                        mesg = mesg + "_up"
                    else:
                        mesg = mesg + "_down"
                    mesg = mesg + ","
                    mesg = mesg + str(gestures[1])
                    if m2y < 100:
                        mesg = mesg + "_up"
                    else:
                        mesg = mesg + "_down"
            else:
                mesg = "gesture"
            client_socket.send(mesg.encode())

            ch = cv2.waitKey(5) & 0xFF
            if ch == 27:
                break
            elif ch == ord('c'):
                self.cmd_switch = not self.cmd_switch
            elif ch == ord('s'):
                self.calib_switch = not self.calib_switch
            elif ch == ord('t'):
                self.track_switch = not self.track_switch

        cv2.destroyAllWindows()


if __name__ == '__main__':
    # main function start here
    try:
        video_src = sys.argv[1]
    except:
        video_src = 0
    #host = "192.168.1.231"
    host = "169.254.76.143"
    port = 5000
    client_socket = socket.socket()
    client_socket.connect((host, port))
    print host
    print "starting..."
    App(video_src).run()
