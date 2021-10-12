from Stitcher import Stitcher
import cv2

def cv_show(name,img):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 读取拼接图片
imageA = cv2.imread("left_01.png")
imageB = cv2.imread("right_01.png")

# 把图片拼接成全景图
stitcher = Stitcher()
(result, vis) = stitcher.stitch([imageA, imageB], showMatches=True)

# 显示所有图片
cv_show('Image A', imageA)
cv_show('Image B', imageB)
cv_show('Keypoint Matches', vis)
cv_show('Result', result)
cv2.imwrite('result.png', result)
