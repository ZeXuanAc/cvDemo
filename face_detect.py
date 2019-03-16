import cv2
import os
import flip
import logging.config


class FaceDetect(object):

    def __init__(self, imagePathPrefix="image", imageHPathPrefix="imageH", resultPathPrefix="result", scaleFactor=1.2):
        logging.config.fileConfig("config" + os.sep + "logger.conf")    # 采用配置文件
        self.logger = logging.getLogger("file")
        self.imagePathPrefix = imagePathPrefix + os.sep
        self.resultPathPrefix = resultPathPrefix + os.sep
        self.imageHPathPrefix = imageHPathPrefix + os.sep
        self.scaleFactor = scaleFactor
        if not os.path.exists(os.getcwd() + os.sep + imageHPathPrefix):
            os.mkdir(os.getcwd() + os.sep + imageHPathPrefix)
        if not os.path.exists(os.getcwd() + os.sep + resultPathPrefix):
            os.mkdir(os.getcwd() + os.sep + resultPathPrefix)

    def faceDetect(self, imageName, haarxml, imagePathPrefix="image" + os.sep):

        self.logger.info(imageName)
        ex_data = {"image_name": imageName}
        ex_data.update({"image_path_name": imagePathPrefix + imageName})
        # Create the haar cascade
        faceCascade = cv2.CascadeClassifier(haarxml)

        # Read the image
        image = cv2.imread(imagePathPrefix + imageName)
        self.logger.info("----图片大小，长：%s ---宽：%s", str(image.shape[1]), str(image.shape[0]))
        ex_data.update({"image_width": image.shape[0], "image_height": image.shape[1]})
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
        # Draw a rectangle around the faces
        for index, (x, y, w, h) in enumerate(faces):
            ul = (x, y)
            ll = (x, y + h)
            ur = (x + w, y)
            lr = (x + w, y + h)
            self.logger.info("----face[%s]位置%s, %s, %s, %s", str(index + 1), ul, ll, ur, lr)
            detected_face.append([ul, ll, ur, lr])
            resultImg = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        ex_data.update({"face_num": len(faces)})
        ex_data.update({"detected_face": detected_face})
        if len(faces) != 0:
            cv2.imwrite(flip.reName(self.resultPathPrefix + imageName, "-result"), resultImg)

        # cv2.imshow("Faces found", image)
        # cv2.waitKey(0)
        print(ex_data)
        return ex_data

    @staticmethod
    def getFileList(p):
        p = str(p)
        if p == "":
            return []
        p = p.replace("/", "\\")
        if p[-1] != "\\":
            p = p+"\\"
        a = os.listdir(p)
        b = [x for x in a if os.path.isfile(p + x)]
        return b

    def getSuggestMsg(self, ex_data, face_type):
        pass

    def start(self):
        imageDir = os.getcwd() + os.sep + self.imagePathPrefix
        cascPath1 = "xml" + os.sep + "haarcascade_frontalface_default.xml"
        cascPath2 = "xml" + os.sep + "haarcascade_profileface.xml"

        images = self.getFileList(imageDir)
        errorList = []

        self.logger.info("\n======人脸检测======\n\n")
        for i in range(images.__len__()):
            result1 = self.faceDetect(images[i], cascPath1)
            if result1['face_num'] == 0:
                self.logger.info("正脸检测不到人脸，对%s做侧脸检测", images[i])
                result2 = self.faceDetect(images[i], cascPath2)
                if result2['face_num'] == 0:
                    self.logger.info("侧脸检测不到人脸，对%s做水平翻转后侧脸检测", images[i])
                    imageHName = flip.flipHorizontal(images[i], self.imageHPathPrefix)
                    result3 = self.faceDetect(imageHName, cascPath2, self.imageHPathPrefix)
                    if result3 != "1":
                        errorList.append(result3['image_path_name'])
            else:
                result1.update({"suggest_msg": self.getSuggestMsg(result1, "front")})
            self.logger.info("\n\n")
        self.logger.info("本次图像检测共%s张图片，检测到%s张含有类似人脸的图片， %s张未检测到人脸"
              , images.__len__(), images.__len__() - errorList.__len__(), errorList.__len__())
        self.logger.info("未检测到的人脸图片为：" + ",".join(errorList))


if __name__ == "__main__":
    faceDetect = FaceDetect()
    faceDetect.start()
    pass


