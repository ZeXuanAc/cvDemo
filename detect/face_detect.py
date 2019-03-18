# -*- coding:utf-8 -*-
import cv2
import os
from detect import flip
import logging.config
from configs import CONFIG_PATH
from detect.xml import XML_PATH

WEB_PATH = os.path.dirname(os.path.realpath(__file__))


class FaceDetect(object):

    def __init__(self, imagePathPrefix="image", imageHPathPrefix="imageH", resultPathPrefix="result", scaleFactor=1.2):
        logging.config.fileConfig(os.path.join(CONFIG_PATH, "logger.conf"))  # 采用配置文件
        self.logger = logging.getLogger("file")
        self.imagePathPrefix = imagePathPrefix + os.sep
        self.resultPathPrefix = resultPathPrefix + os.sep
        self.imageHPathPrefix = imageHPathPrefix + os.sep
        self.scaleFactor = scaleFactor
        if not os.path.exists(imageHPathPrefix):
            os.mkdir(imageHPathPrefix)
        if not os.path.exists(resultPathPrefix):
            os.mkdir(resultPathPrefix)

    def faceDetect(self, imageName, haarxml, imagePathPrefix="image" + os.sep):
        self.logger.info(imageName)
        exData = {"image_name": imageName}
        exData.update({"image_path_name": imagePathPrefix + imageName})
        # Create the haar cascade
        faceCascade = cv2.CascadeClassifier(haarxml)

        # Read the image
        image = cv2.imread(imagePathPrefix + imageName)
        self.logger.info("----图片大小，长：%s ---宽：%s", str(image.shape[1]), str(image.shape[0]))
        exData.update({"image_width": image.shape[0], "image_height": image.shape[1]})
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=self.scaleFactor,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        self.logger.info("----Found %s faces!", len(faces))

        resultImg = image
        detected_face = []
        faceXywh = []
        # Draw a rectangle around the faces
        for index, (x, y, w, h) in enumerate(faces):
            x = int(x)
            y = int(y)
            w = int(w)
            h = int(h)

            faceXywh.append([x, y, w, h])
            ul = (x, y)
            ll = (x, y + h)
            ur = (x + w, y)
            lr = (x + w, y + h)
            self.logger.info("----face[%s]位置%s, %s, %s, %s", str(index + 1), ul, ll, ur, lr)
            detected_face.append([ul, ll, ur, lr])
            resultImg = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        exData.update({"face_num": len(faces)})
        exData.update({"detected_face": detected_face})
        exData.update({"faces": faceXywh})
        if len(faces) != 0:
            cv2.imwrite(flip.reName(self.resultPathPrefix + imageName, "-result"), resultImg)

        return exData

    @staticmethod
    def getFileList(p):
        p = str(p)
        if p == "":
            return []
        p = p.replace("/", "\\")
        if p[-1] != "\\":
            p = p + "\\"
        a = os.listdir(p)
        b = [x for x in a if os.path.isfile(p + x)]
        return b

    def getSuggestMsg(self, exData, face_type):
        suggestMsg = ""
        if exData['face_num'] == 0:
            suggestMsg = "请调整人脸摆放位置（未检测到人脸）"
        if exData['face_num'] > 1:
            suggestMsg = "请调整人脸摆放位置（人脸检测到多张脸）"
        if exData['face_num'] == 1:
            if face_type == "front":
                suggestMsg += self.getDetectPosition(exData)
            elif face_type == "profile":
                suggestMsg = "请将脸向右倾转（" + self.getDetectPosition(exData) + "）"
            elif face_type == "profile_h":
                suggestMsg = "请将脸向左倾转（" + self.getDetectPosition(exData) + "）"
            if self.getFaceSize(exData) != "":
                suggestMsg + self.getFaceSize(exData)
        return suggestMsg

    @staticmethod
    def getFaceSize(exData):
        faceArea = (exData['faces'][0][0] + exData['faces'][0][2]) * (exData['faces'][0][1] + exData['faces'][0][3])
        imageArea = exData['image_width'] * exData['image_height']
        suggestMsg = ""
        if faceArea < imageArea * 1 / 9:
            suggestMsg = "请将镜头靠近些"
        if faceArea > imageArea * 1 / 4:
            suggestMsg = "请将镜头离远些"
        return suggestMsg

    @staticmethod
    def getDetectPosition(exData):
        perfect = True
        suggestMsg = "请将头稍往"
        imageWidth = exData['image_width']
        imageHeight = exData['image_height']
        errorFactor = 0.18
        face = exData['faces']
        faceCenter = (face[0][0] + face[0][2] / 2, face[0][1] + face[0][3] / 2)
        if (faceCenter[0] - imageWidth / 2) > imageWidth * errorFactor:
            perfect = False
            suggestMsg += "左"
        elif (imageWidth / 2 - faceCenter[0]) > imageWidth * errorFactor:
            perfect = False
            suggestMsg += "右"
        if (faceCenter[1] - imageHeight / 2) > imageHeight * errorFactor:
            perfect = False
            suggestMsg += "上"
        elif (imageHeight / 2 - faceCenter[1]) > imageHeight * errorFactor:
            perfect = False
            suggestMsg += "下"
        suggestMsg += "方移"
        if perfect:
            suggestMsg = "位置完美"
        return suggestMsg

    @staticmethod
    def getErrorCode(exData):
        faceNum = exData['face_num'] - 1
        if exData['face_num'] > 1:
            faceNum = -2
        return faceNum

    def startWithDir(self):
        imageDir = self.imagePathPrefix

        images = self.getFileList(imageDir)

        self.logger.info("\n======人脸检测======\n\n")
        for i in range(images.__len__()):
            self.logger.info(self.detectImg(images[i]))
            self.logger.info("\n\n")

    def detectImg(self, imageName):
        cascPath1 = os.path.join(XML_PATH, "haarcascade_frontalface_default.xml")
        cascPath2 = os.path.join(XML_PATH, "haarcascade_profileface.xml")

        face_type = "front"
        result = self.faceDetect(imageName, cascPath1, self.imagePathPrefix)
        result.update({"face_type": face_type})
        response = {"error_code": "0", "ex_data": result}
        if result['face_num'] == 0:
            self.logger.info("正脸检测不到人脸，对%s做侧脸检测", imageName)
            result2 = self.faceDetect(imageName, cascPath2, self.imagePathPrefix)
            if result2['face_num'] == 0:
                self.logger.info("侧脸检测不到人脸，对%s做水平翻转后侧脸检测", imageName)
                imageHName = flip.flipHorizontal(imageName, self.imageHPathPrefix, self.imagePathPrefix)
                result3 = self.faceDetect(imageHName, cascPath2, self.imageHPathPrefix)
                if result3['face_num'] == 0:
                    result.update(result3)
                else:
                    face_type = "profile_h"
                    result.update(result3)
            else:
                face_type = "profile"
                result.update(result2)
        result.update({"suggest_msg": self.getSuggestMsg(result, face_type), "face_type": face_type})
        response.update({"error_code": self.getErrorCode(result)})
        return response


if __name__ == "__main__":
    faceDetect = FaceDetect(os.path.join(WEB_PATH, 'upload'))
    print(faceDetect.detectImg("13.jpg"))
    # faceDetect.startWithDir()
    pass
