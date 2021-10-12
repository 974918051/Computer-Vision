##  · 功能：对两张图片进行拼接

### 大致思路：

#### 1、读取需要拼接的两张图片A和B，检测他们的SIFT关键特征点，并且计算特征描述子

#### 2、对两张图片的所有特征点进行匹配，得到匹配结果
#### 3、对A进行视角变换得到变换后的图片result（图片size已经发生改变），然后将B传入result最左端，得到拼接后对图片

### 使用方法：
#### 首先运行ImageStich中的Stitcher.py文件

#### 其次运行ImageStiching.py文件，得到拼接后对图片

#### **注意：xfeatures2d算法以申请专利，需安装3.4.2.16版本的OpenCV**

### 效果展示：

图A：![](实战3_图像拼接/ImageStich/left_01.png)

图B：![](实战3_图像拼接/ImageStich/right_01.png)

拼接后：![](实战3_图像拼接/ImageStich/result.png)

