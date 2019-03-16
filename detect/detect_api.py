# -*- coding:utf-8 -*-
import cv2
import os
from detect.xml import XML_PATH
from web import WEB_PATH

# 获取坐标
def detect(file_name):
    cascPath = os.path.join(XML_PATH, "haarcascade_frontalface_default.xml")
    print(cascPath)
    faceCascade = cv2.CascadeClassifier(cascPath)
    image_path = os.path.join(WEB_PATH, "upload", file_name)
    print(image_path)
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )
    print("Found {0} faces!".format(len(faces)))
    result = {}
    L = []
    for (x, y, w, h) in faces:
        face = []
        print(x, y, w, h)
        face.append([int(x), int(y)])
        face.append([int(x + w), int(y + h)])
        L.append(face)

    result = {"faces": L, "face_count": len(faces)}
    return result

def array_get():
    L = [[[56, 55], [131, 130]], [[168, 70], [234, 136]], [[267, 69], [354, 156]], [[354, 78], [428, 152]]]
    return L
