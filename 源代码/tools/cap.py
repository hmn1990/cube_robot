#!/usr/bin/env python3
# need to load bcm2835-v4l2 kernel module

# import cv2
# import numpy as np
# import math
# 
# cap = cv2.VideoCapture(0)
# print(cap.isOpened())
# 
# while cap.isOpened():
#     ret,imgobj = cap.read()
#     cv2.imshow('原始视频',imgobj)
# 
#     #cv2.drawContours(imgobj, candidates, -1, (0, 0, 255), 3)
#     cv2.imshow("image", imgobj)
#     c = cv2.waitKey(1)
#     if c == 27:
#         break
#     
# cap.release()
# cv2.destroyAllWindows()

import cv2
import numpy as np

def four_point_transform(image, rect):
    # 获取坐标点，并将它们分离开来
    # 图像尺寸
    maxWidth = 256
    maxHeight = 256
    # 构建新图片的4个坐标点
    edge = 2
    dst = np.array([
        [edge, edge],
        [maxWidth - 1 - edge, edge],
        [maxWidth - 1 - edge, maxHeight - 1 - edge],
        [edge, maxHeight - 1 - edge]], dtype = "float32")

    # 获取仿射变换矩阵并应用它
    M = cv2.getPerspectiveTransform(rect, dst)
    # 进行仿射变换
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # 返回变换后的结果
    return warped

def mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x,y)

def mark_cube(img):
    half_size = 10
    color = (0,0,0)
    # 1 2 3
    # 4 5 6
    # 7 8 9
    cv2.rectangle(img, (42-half_size,42-half_size), (42+half_size,42+half_size), color)
    cv2.rectangle(img, (128-half_size,42-half_size), (128+half_size,42+half_size), color)
    cv2.rectangle(img, (214-half_size,42-half_size), (214+half_size,42+half_size), color)
    cv2.rectangle(img, (42-half_size,128-half_size), (42+half_size,128+half_size), color)
    cv2.rectangle(img, (128-half_size,128-half_size), (128+half_size,128+half_size), color)
    cv2.rectangle(img, (214-half_size,128-half_size), (214+half_size,128+half_size), color)
    cv2.rectangle(img, (42-half_size,214-half_size), (42+half_size,214+half_size), color)
    cv2.rectangle(img, (128-half_size,214-half_size), (128+half_size,214+half_size), color)
    cv2.rectangle(img, (214-half_size,214-half_size), (214+half_size,214+half_size), color)
    
    
cap = cv2.VideoCapture(0)
# print("宽度width = %.2f\n"%cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# print("高度height = %.2f\n"%cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# print("帧率fps = %.2f\n"%cap.get(cv2.CAP_PROP_FPS))
# print("色调hue = %.2f\n"%cap.get(cv2.CAP_PROP_HUE))
# print("饱和度saturation = %.2f\n"%cap.get(cv2.CAP_PROP_SATURATION))
# print("对比度contrast = %.2f\n"%cap.get(cv2.CAP_PROP_CONTRAST))
# print("亮度brightness = %.2f\n"%cap.get(cv2.CAP_PROP_BRIGHTNESS))
# print("曝光exposure = %.2f\n"%cap.get(cv2.CAP_PROP_EXPOSURE))
#cap.set(cv2.CAP_PROP_BRIGHTNESS, 1) # 亮度 0.2
#cap.set(cv2.CAP_PROP_CONTRAST, 1) # 对比度 0.2
#print("对比度contrast = %.2f\n"%cap.get(cv2.CAP_PROP_CONTRAST))
#print("亮度brightness = %.2f\n"%cap.get(cv2.CAP_PROP_BRIGHTNESS))
while True:
    ret,img = cap.read()
    
    # 对原始图片进行变换
    
    #pts1 = np.array([[172,94],[518,98],[511,444],[163,435]], dtype = "float32")
    pts1 = np.array([[166,90],[468,96],[466,397],[164,390]], dtype = "float32")
    warped1 = four_point_transform(img, pts1)
    mark_cube(warped1)

    cv2.imshow("image", img)
    cv2.setMouseCallback("image", mouse)
    cv2.imshow("Warped1", warped1)   
    
    k = cv2.waitKey(1)
    if k == 27:
        cap.release()
        cv2.destroyAllWindows()
        break
