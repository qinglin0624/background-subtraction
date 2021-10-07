# Note: You need to install Opencv-contrib to run this script.

import numpy as np 
import cv2 


if __name__ == "__main__":
    
    cap = cv2.VideoCapture('vtest.avi')
    fgbg1 = cv2.bgsegm.createBackgroundSubtractorMOG()

    # save output video
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    fps =cap.get(cv2.CAP_PROP_FPS)
    size = (int(cap.get(3)),int(cap.get(4)))
    out = cv2.VideoWriter('output.mp4',fourcc, fps, size,isColor = False)

    while(1): 
        # read frames 
        ret, img = cap.read(); 
        if ret == True:
            # apply mask for background subtraction 
            fgmask1 = fgbg1.apply(img)

            out.write(fgmask1)

            cv2.imshow('Original', img)
            cv2.imshow('MOG', fgmask1)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break;
        else:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()