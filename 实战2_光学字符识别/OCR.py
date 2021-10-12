import cv2
import numpy as np
import argparse

from numpy.lib.histograms import histogram_bin_edges
from numpy.lib.type_check import imag

def cv_show(name, img):
    cv2.startWindowThread()
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.waitKey(1)

def order_points(pts):
    # 一共四个坐标点
    rect = np.zeros((4, 2), dtype = 'float32')

    # 按顺序找到对应坐标0123分别是左上，右上，右下，左下
    # 计算左上，右下
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # 计算右上和左下
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect

def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w* r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    resized = cv2.resize(image, dim, interpolation=inter)
    return resized

def four_point_transform(image, pts):
    # 获取输入坐标点
    rect = order_points(pts)
    (tl,tr, br, bl) = rect

    # 计算输入的w和b值
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxwidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxheight = max(int(heightA), int(heightB))

    # 变换后对应坐标位置
    dst = np.array([
        [0, 0],
        [maxwidth - 1, 0],
        [maxwidth - 1, maxheight - 1],
        [0, maxheight - 1]], dtype = 'float32')

    # 计算变换矩阵
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxwidth,maxheight))

    return warped

image = cv2.imread('image1.jpg')

ratio = image.shape[0] / 500.0
orig = image.copy()

image = resize(orig, height=500)

# 预处理
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)

# 展示预处理结果
print('STEP 1: 边缘检测')
cv2.imshow('Image', image)
cv2.imshow('Edged', edged)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 轮廓检测
cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

# 遍历轮廓
for c in cnts:
    # 计算轮廓近似
    peri = cv2.arcLength(c, True)
    # c表示输入的点集
    # 第二个参数表示从原始轮廓到近似轮廓的最大距离，它是一个准确度参数
    # True表示封闭的
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)

    # 轮廓有4个点的时候拿出来
    if len(approx) == 4:
        screenCnt = approx
        break

# 显示结果
print('STEP 2: 获取轮廓')
cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
cv_show('OutLine', image)

# 透视变换
warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

# 二值处理
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
ref = cv2.threshold(warped, 100, 255, cv2.THRESH_BINARY)[1]
cv2.imwrite('scan.jpg', ref)

# 展示结果
print('STPE3 : 变换')
cv2.imshow('Original', resize(orig, height = 650))
cv2.imshow('Scanned', resize(ref, height = 650))
cv2.waitKey(0)

