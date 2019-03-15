import cv2
import os
import flip


def faceDetect(imageName, haarxml, imagePathPrefix="image/", scaleFactor=1.2, resultPathPrefix="result/"):

    print(imageName)
    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(haarxml)

    # Read the image
    image = cv2.imread(imagePathPrefix + imageName)
    print("----图片大小，宽：" + str(image.shape[0]), "---长：" + str(image.shape[1]))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=scaleFactor,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    print("----Found {0} faces!".format(len(faces)))

    resultImg = image
    # Draw a rectangle around the faces
    for index, (x, y, w, h) in enumerate(faces):
        ul = (x, y)
        ll = (x, y + h)
        ur = (x + w, y)
        lr = (x + w, y + h)
        print("----face[{}]位置{}, {}, {}, {}".format(str(index + 1), ul, ll, ur, lr))
        resultImg = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    if len(faces) != 0:
        cv2.imwrite(flip.reName(resultPathPrefix + imageName, "-result"), resultImg)

    # cv2.imshow("Faces found", image)
    # cv2.waitKey(0)

    if len(faces) == 0:
        return imagePathPrefix + imageName
    else:
        return "1"


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


if __name__ == "__main__":
    imageDir = os.getcwd() + "\image"
    cascPath1 = "xml/haarcascade_frontalface_default.xml"
    cascPath2 = "xml/haarcascade_profileface.xml"

    images = getFileList(imageDir)
    frontErrorList = []
    profileErrorList = []

    print("\n======人脸检测======\n\n")
    for i in range(images.__len__()):
        result1 = faceDetect(images[i], cascPath1)
        if result1 != "1":
            print("正脸检测不到人脸，对{}做侧脸检测".format(images[i]))
            result2 = faceDetect(images[i], cascPath2)
            if result2 != "1":
                print("侧脸检测不到人脸，对{}做水平翻转后侧脸检测".format(images[i]))
                imageHName = flip.flipHorizontal(images[i], "imageH/")
                result3 = faceDetect(imageHName, cascPath2, "imageH/")
                if result3 != "1":
                    frontErrorList.append(result3)
        print("\n\n")
    print("本次图像检测共{}张图片，检测到{}张含有类似人脸的图片， {}张未检测到人脸"
          .format(images.__len__(), images.__len__() - frontErrorList.__len__(), frontErrorList.__len__()))
    print("未检测到的人脸图片为：" + ",".join(frontErrorList))


