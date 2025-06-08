#!/usr/bin/env python3
import cv2
import numpy as np
from Camera import init_camera, get_frame
from readConfig import config

# finds objects of a given color range
# returns list of dicts: area, bbox, centroid

def find_color_objects(frame, lower, upper, area_thresh=config['contour_threshold']):
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,lower,upper)
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    objects=[]
    for c in contours:
        area=cv2.contourArea(c)
        if area<area_thresh: continue
        x,y,w,h=cv2.boundingRect(c)
        M=cv2.moments(c)
        if M['m00']==0: continue
        cx=int(M['m10']/M['m00'])
        cy=int(M['m01']/M['m00'])
        objects.append({'area':int(area),'bbox':(x,y,w,h),'centroid':(cx,cy),'mask':mask})
    return objects

if __name__=='__main__':
    cfg=config['colors']
    keys=['left','right']
    bounds={}
    for k in keys:
        h1,s1,v1=cfg[f'min_{k}_hsv']
        h2,s2,v2=cfg[f'max_{k}_hsv']
        lo=np.array((h1,s1,v1),np.uint8)
        hi=np.array((h2,s2,v2),np.uint8)
        if lo[1]<50: lo[1]=50
        bounds[k]=(lo,hi)
    cap=init_camera()
    while True:
        frame=get_frame(cap)
        if frame is None: break
        res=frame.copy()
        for lo,hi in bounds.values():
            objs=find_color_objects(frame,lo,hi)
            for obj in objs:
                x,y,w,h=obj['bbox']
                cx,cy=obj['centroid']
                cv2.rectangle(res,(x,y),(x+w,y+h),(0,255,0),2)
                cv2.circle(res,(cx,cy),5,(255,0,0),-1)
        cv2.imshow('out',res)
        if cv2.waitKey(1)&0xFF==ord('q'): break
    cap.release()
    cv2.destroyAllWindows()
