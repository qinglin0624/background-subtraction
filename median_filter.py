# It visualizes the performance of median filter as a method of background subtraction.

import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage import color


def median_filter(n=50, video_path='vtest.avi'):
    cap = cv2.VideoCapture(video_path)
    frames=[]
    for i in range(n):
        ret,img = cap.read()
        gray = np.float32(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        frames.append(gray)
        if i== n-1:
            ret, current = cap.read()
            current =np.float32(cv2.cvtColor(current, cv2.COLOR_BGR2GRAY))
        
    frames = np.asarray(frames)
    background = np.median(frames, axis=0)

    diff = cv2.absdiff(current, background)
    foreground_mask = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)[1]

    return current, background, foreground_mask



if __name__ == "__main__":
    
    current, background, foreground_mask = median_filter()
    
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