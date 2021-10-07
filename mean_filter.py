# It visualizes the performance of mean filter as a method of background subtraction.

import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage import color


def mean_filter(n=50, video_path='vtest.avi')

    cap = cv2.VideoCapture(video_path)

    ret, frame = cap.read()
    gray = np.float32(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

    for i in range (n-1):
        ret, img = cap.read()
        img_gray = np.float32(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        gray += img_gray
        if i==n-2:
            ret, current = cap.read()
            current =np.float32(cv2.cvtColor(current, cv2.COLOR_BGR2GRAY))

    background = gray/n
    diff = cv2.absdiff(current, background)
    foreground_mask = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)[1]
    
    return current, background, foreground_mask


if __name__ == "__main__":
    
    current, background, foreground_mask = mean_filter()
    
    plt.figure(figsize=(20,6))

    plt.subplot(131)
    plt.imshow(current, cmap=plt.cm.gray)
    plt.title('frame', fontsize=18)
    plt.axis('off')

    plt.subplot(132)
    plt.imshow(background, cmap=plt.cm.gray)
    plt.title('estimated background', fontsize=18)
    plt.axis('off')


    plt.subplot(133)
    plt.imshow(foreground_mask, cmap=plt.cm.gray)
    plt.title('foreground mask', fontsize=18)
    plt.axis('off')