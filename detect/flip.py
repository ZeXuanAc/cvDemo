# -*- coding:utf-8 -*-
import cv2 as cv


def reName(imagePath, suffix):
    imagePathSplit = imagePath.split(".")
    imagePathSplit[-2] = imagePathSplit[-2] + suffix
    return ".".join(imagePathSplit)


def flipHorizontal(imageName, imageHPathPrefix="imageH/", imagePathPrefix="image/"):
    # 读取图像，支持 bmp、jpg、png、tiff 等常用格式
    imagePath = imagePathPrefix + imageName
    img = cv.imread(imagePath)

    # Flipped Horizontally 水平翻转
    h_flip = cv.flip(img, 1)
    newPath = reName(imageName, "-h")
    cv.imwrite(imageHPathPrefix + newPath, h_flip)
    return newPath


if __name__ == "__main__":
    flipHorizontal("p8.jpg")





