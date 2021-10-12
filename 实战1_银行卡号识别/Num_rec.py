import cv2
import numpy as np
import matplotlib.pyplot as plt

# 定义show函数
def cv_show(name, img):
    cv2.startWindowThread()
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.waitKey(1)

# 定义轮廓排序函数
def sort_contours(cnts, method='left-to-right'):
    reverse = False
    i = 0
    
    if method == 'right-to-left' or method == 'bottom-to-top':
        reverse = True
        
    if method == 'top-to-bottom' or method == 'bottom-to-top':
        i = 1
    boundingBoxes = [cv2.boundingRect(c) for c in cnts] #找到最小外接矩形,返回包含x,y,h,w四个值的tuple
    # zip(cnts,boundingBoxes）位置上指可迭代的元素；key是指按什么方式进行排序，这里key=lambda b:b[1][i] b只
    # 是一个变量名，可以是任何一个变量，b[1][i]指按第二元素中的第i个元素就行排序也就是按boundingBoxes中的第i个元素
    # 进行排序；reverse是反转，false为不反转，true为反转。
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                key = lambda b: b[1][i], reverse=reverse))
    return cnts, boundingBoxes

img = cv2.imread('模版.png')
cv_show('模版', img)

ref = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv_show('模版_灰度图', ref)

ref = cv2.threshold(ref, 10, 255, cv2.THRESH_BINARY_INV)[1]
cv_show('模版_二值图', ref)

# 轮廓检测
## cv2.findContours()函数应输入二值图（即黑白图），cv2.RETR_EXTERNAL只检测外轮廓，cv2.CHAIN_APPROX_SIMPLE只保留终点坐标
## cv2.findContours()函数返回两个值，一个是轮廓本身，还有一个是每条轮廓对应的属性
_, refCnts, hierarchy = cv2.findContours(ref.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

cv2.drawContours(img, refCnts, -1, (0,0,255), 3)
cv_show('img', img)
# print(np.array(refCnts).shape)
# 轮廓排序
refCnts = sort_contours(refCnts, method='left-to-right')[0]
digits = {}

## 模版处理方法：
# 遍历每个轮廓
for (i, c) in enumerate(refCnts):
    # 计算外接矩形，并且resize大小
    (x, y, w, h) = cv2.boundingRect(c)
    roi = ref[y:y + h, x:x + w]
    roi = cv2.resize(roi, (57, 88))
    digits[i] = roi
    # cv_show('roi', roi)
# print(digits.items())
# input()

## 输入图像处理
image = cv2.imread('卡1.png')
image = cv2.resize(image, (300,189))
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

cv_show('gray', gray)

# 礼帽操作，突出图像更明亮的区域
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,3))# 初始化两个卷积核
sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))

tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, rectKernel)
cv_show('tophat', tophat)

grad_x = cv2.Sobel(tophat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)# ksize=-1相当于3*3的卷积核
# grad_y = cv2.Sobel(tophat, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)
# grad = cv2.addWeighted(grad_x, 0.5, grad_y, 0.5, 0)

grad_x = np.absolute(grad_x)
# cv_show('grad_x', grad_x)
(minVal, maxVal) = (np.min(grad_x), np.max(grad_x))
grad_x = (255 * ((grad_x - minVal) / (maxVal - minVal))) # 归一化
grad_x = grad_x.astype('uint8')

# print(np.array(grad_x).shape)
cv_show('grad_x', grad_x)

# 通过闭操作（先膨胀，后腐蚀），将数字连在一起
grad_x = cv2.morphologyEx(grad_x, cv2.MORPH_CLOSE, rectKernel)
cv_show('grad_x', grad_x)
# 二值化处理，THRESH_OTSU会自动寻找合适的阈值，适合双峰，需把阈值参数设置为0
thresh = cv2.threshold(grad_x, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
cv_show('thresh', thresh)

# 再进行一次闭操作
thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
cv_show('thresh', thresh)

# 计算轮廓
_, threshCnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                                 cv2.CHAIN_APPROX_SIMPLE)
cnts = threshCnts
cur_img = image.copy()
cv2.drawContours(cur_img, cnts, -1, (0,0,255), 3)
cv_show('img', cur_img)

# 遍历轮廓
locs = []

for (i, c) in enumerate(cnts):
    # 计算矩形
    (x, y, w, h) = cv2.boundingRect(c)
    ar = w / float(h)
    
    # 选择合适的区域，根据实际任务来
    if ar > 2.5 and ar < 4.0:
        if(w > 40 and w < 55) and (h > 10 and h < 20):
            locs.append((x, y, w, h))

# 将轮廓从左到右排序
locs = sorted(locs, key=lambda x:x[0])
output = []

# 遍历每个轮廓中的数字
for (i, (gx, gy, gw, gh)) in enumerate(locs):
    groupOutput = []
    # 根据坐标提取每个轮廓
    group = gray[gy - 5:gy + gh +5, gx - 5:gx + gw +5]
#     cv_show('group', group)
    
    # 预处理
    group = cv2.threshold(group, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1] # 二值化
#     cv_show('group', group)
    # 计算每一组的轮廓
    _, digitCnts, hierarchy = cv2.findContours(group.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 排序
    digitCnts = sort_contours(digitCnts, method ='left-to-right')[0]
    
    # 计算每个轮廓中的每个数值
    for c in digitCnts:
        (x, y, w, h) = cv2.boundingRect(c)
        roi = group[y:y + h, x:x + w]
        roi = cv2.resize(roi, (57, 88))
        cv_show('roi', roi)

        # 计算匹配得分
        scores = []

        # 在模板中计算每一个得分
        for (digit, digitROI) in digits.items():
            # 模板匹配
            result = cv2.matchTemplate(roi, digitROI, cv2.TM_CCOEFF)
            (_, score, _, _) = cv2.minMaxLoc(result)
            scores.append(score)

        groupOutput.append(str(np.argmax(scores)))
        print(groupOutput)
 

    cv2.rectangle(image, (gx - 5, gy - 5), (gx + gw + 5, gy + gh + 5), (0,0,255), 1)
    cv2.putText(image, ''.join(groupOutput), (gx, gy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0,0,255), 2)
    output.extend(groupOutput)

# print('Credit Card Type:{}'.format(FIRST_NUMBER[output[0]]))
print('Credit Card #:{}'.format(''.join(output)))
cv_show('Image', image)