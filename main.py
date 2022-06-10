import cv2
import numpy as np
from time import sleep
import playsound

import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

kit.servo[2].angle = 90
#channel = 27
channel_realay = 18
GPIO.setmode(GPIO.BCM)
#GPIO.setup(channel, GPIO.OUT)
GPIO.setup(channel_realay, GPIO.OUT)

kit.servo[1].angle = 100

cap = cv2.VideoCapture(0)

def center_handle(x,y,w,h):
    cx = int((x+x+w)/2)
    cy = int((y+y+h)/2)
    return cx, cy

detect = []
offset = 23  #allowable error between pixel
counter = 0

min_width = 20
min_height = 20

while(cap.isOpened()):
    _, frame = cap.read()
    frame_count = frame[190:410, 520:920]
    frame_rec = frame[210:420, 100:270]
    frame_pixel = frame[210:420, 275:680]
    
    try:
        hsv_frame = cv2.cvtColor(frame_rec, cv2.COLOR_BGR2HSV)
        gray_frame_count = cv2.cvtColor(frame_count, cv2.COLOR_BGR2GRAY)
        gray_frame_pixel = cv2.cvtColor(frame_pixel, cv2.COLOR_BGR2GRAY)
        gray_frame_rec = cv2.cvtColor(frame_rec, cv2.COLOR_BGR2GRAY)
        _, thresh_count = cv2.threshold(gray_frame_count, 80, 255, cv2.THRESH_BINARY)
        _, thresh_rec = cv2.threshold(gray_frame_rec, 80, 255, cv2.THRESH_BINARY)
        _, thresh_pixel = cv2.threshold(gray_frame_pixel, 80, 255, cv2.THRESH_BINARY)
        
    except:
        print("EOF")
        
    contours_count, _ = cv2.findContours(thresh_count, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_rec, _ = cv2.findContours(thresh_rec, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_pixel, _ = cv2.findContours(thresh_pixel, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.line(frame_count, (150, 0), (150, 550), (0, 255, 255))
    
    for cnt in contours_count:
        (x,y,w,h) = cv2.boundingRect(cnt)

        validate_counter = (w>=min_width) and (h>=min_height)
        if not validate_counter:
            continue
        area = cv2.contourArea(cnt)
        cv2.rectangle(frame_count, (x,y), (x+w, y+h), (255,0,0), 2)
        
        center = center_handle(x,y,w,h)
        detect.append(center)
        cv2.circle(frame_count, center, 4, (0,0,255), -1)
        
        for (x,y) in detect:
            if x<(150+offset) and x>(150-offset):
                counter = counter+1    
            cv2.line(frame_count, (150, 0), (150, 550), (0, 127, 255), 3)
            detect.remove((x,y))
            
    for cnt2 in contours_pixel:
        (x,y,w,h) = cv2.boundingRect(cnt2)
        area2 = cv2.contourArea(cnt2)
        if area2 > 20000:
            cv2.rectangle(frame_pixel, (x,y), (x+w, y+h), (0,0,255), 2)
            cv2.putText(frame_pixel, str(area2), (x,y), 1, 1, (0,255,0))
            
            GPIO.output(channel_realay, GPIO.LOW)
            
            playsound.playsound('alart.mp3', True)

            kit.servo[1].angle = 0
            sleep(0.5)
            kit.servo[1].angle = 100

    
    for cnt1 in contours_rec:
        (x,y,w,h) = cv2.boundingRect(cnt1)
        area1 = cv2.contourArea(cnt1)

        if (area1 > 1000):
            cv2.rectangle(frame_rec, (x,y), (x+w, y+h), (255,0,0), 2)
            centerX = int((x+x+w)/2)
            centerY = int((y+y+h)/2)
            
            pixel_center = hsv_frame[centerY, centerX]
            hue_value = pixel_center[0]
            
            color = "Undefined"

            
            if hue_value < 17:
                color = "RED"
                #sleep(0.5)
                kit.servo[2].angle = 30
                sleep(1)
                kit.servo[2].angle = 90
             
                #sleep(2.5)

            elif  hue_value < 20:
                color = "ORANGE"
                kit.servo[2].angle = 30
                sleep(1)
                kit.servo[2].angle = 90
               
                
            elif hue_value < 35:
                color = "YELLOW"
                kit.servo[2].angle = 90
                sleep(0.6)
                kit.servo[2].angle = 30
                sleep(1.4)
                kit.servo[2].angle = 90
               
                
            elif hue_value < 90:
                color = "Green"
                kit.servo[2].angle = 90
                sleep(0.5)
                kit.servo[2].angle = 180
                sleep(1.3)
                kit.servo[2].angle = 90
               
                
            elif hue_value < 100:
                color = "White"
                kit.servo[2].angle = 90
                sleep(0.5)
                kit.servo[2].angle = 170
                sleep(1.3)
                kit.servo[2].angle = 90
   
               

            elif hue_value < 130:
               
                color = "Blue"
                #kit.servo[2].angle = 90
                kit.servo[2].angle = 90
                sleep(0.5)
                kit.servo[2].angle = 180
                sleep(1.3)
                kit.servo[2].angle = 90
                
                
            elif hue_value > 160:
                color = "RED"
                kit.servo[2].angle = 90
                sleep(0.5)
                kit.servo[2].angle = 30
                sleep(1)
                kit.servo[2].angle = 90
                
                
            pixel_center_bgr = frame_rec[centerY, centerX]
            b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2])
            cv2.putText(frame, color, (10,70), 0, 1.5, (b,g,r), 2)
            cv2.circle(frame_rec,(centerX, centerY), 7, (255, 255, 255), -1)
            
    cv2.putText(frame, "product counter:"+str(counter), (300, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 5)
    
    
    cv2.imshow("frame", frame)
    #cv2.imshow("Counting Frame", frame_count)
    #cv2.imshow("Color recognition Frame", frame_rec)
    
    k = cv2.waitKey(1)
    if k == 27:
        break
    elif k == ord("n"):
        GPIO.output(channel_realay, GPIO.HIGH)
    elif k == ord("m"):
        GPIO.output(channel_realay, GPIO.LOW) 
    
    
cap.release()
cv2.destroyAllWindows()


