# Credit: Adopted from https://github.com/manishminocha/BackgroundSubtraction/blob/master/sgbgs.py

from sklearn.cluster import KMeans
import scipy.stats as stats
import numpy as np
import cv2
import math
import shutil   # to clean directory
import os     # to create directory



def initializeModel(frame, numPixels):
    """initialize each pixel in the estimated background using K means on the first frame"""
    
    frame = frame.reshape((numPixels,1)) # reshape frame into a 1D array of pixels
    clt = KMeans(n_clusters = K)
    clt.fit(frame)
    print ("K means has converged after iterations", clt.n_iter_)
    inertia = clt.inertia_
    u = clt.cluster_centers_ # shape: (K, 1)
    r = clt.labels_          # shape: (numpix,)
    
    si = np.zeros(K)
    for j in range (0,K):
        si[j] = (inertia/numPixels) # just approximation since scikit does not seem to give std
    
   
    # transform r matrix as matrix with boolean values across K dimension (i.e., M in the paper)
    rprime=np.zeros((numPixels,K))
    for j in range (0,K):
        for pixel in range (0,numPixels):
            if r[pixel] == j:
                rprime[pixel][j]=1
                
    #  shape: (numpix, K)
    sig = np.zeros((numPixels,K))
    omega = np.zeros((numPixels,K))
    mean = np.zeros((numPixels,K))
    
    # every pixel has the same initialization
    for j in range (0,K):
         for pixel in range (0, numPixels):
            mean[pixel][j] = u[j]
            sig[pixel][j] = si[j]
            omega[pixel][j]=(1/K)*(1-alpha) + alpha * rprime[pixel][j]  # w0 = 1/K
    
    return (sig, mean, omega)



def sort(K,ratio,omega,mean,sig,pixel):
    """sort the gaussians in terms of omega/sigma"""
    
    records =[]
    for j in range(0, K):
        records.append(( ratio[j], omega[pixel][j], mean[pixel][j],sig[pixel][j] ))
        
    records.sort(key = lambda t:t[0] ,reverse=True)

    for j in range(0,K):
        (ratio[j],omega[pixel][j],mean[pixel][j],sig[pixel][j])=records[j]
                                 
    return (ratio,omega,mean,sig)



def extractFrames(videoCapture, numPixels):

    # delete frames folder and create again
    if os.path.isdir(framesFolder):
        shutil.rmtree(framesFolder)
    os.makedirs(framesFolder)

    frameId = videoCapture.get(1)       # ID of the current frame
    ret, frame = videoCapture.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    
    # initialize K means clustering for first frame
    if (frameId == 0):
        (sig, mean, omega ) = initializeModel(frame,numPixels)

    while(videoCapture.isOpened()):
        ret, frame = videoCapture.read()
        if (ret != True):
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        frameId = frameId + 1

        if (frameId % math.floor(frameCapture) == 0): # in case we do not want to process every frame

            (background, foreground) = processFrame(frame, sig, omega, mean, numPixels)
                       
            # save foreground mask and estimated background
            print ("Writing processed frame %d" % frameId)
            background = background.reshape(videoHeight,videoWidth)
            foreground = foreground.reshape(videoHeight,videoWidth)
            cv2.imwrite(r"%s/foreground_%s.jpg" % (framesFolder, str(int(frameId)).zfill(4)), foreground)
            cv2.imwrite(r"%s/background_%s.jpg" % (framesFolder, str(int(frameId)).zfill(4)), background)
           
    # return the total number of frames in the video
    return frameId



def processFrame(frame, sig, omega, mean, numPixels):
    ratio = [0 for i in range(K)]
    frame = frame.reshape((numPixels,1))
    background, foreground = np.zeros(numPixels, dtype = np.uint8), np.zeros(numPixels, dtype = np.uint8)


    for pixel in range (0,numPixels):
       
        gaussianMatched = 0
        sumOmega = 0
        for j in range (0,K):
            if abs(frame[pixel] - mean[pixel][j]) < (2.5 * sig[pixel][j]):  # matched
#                 ro = alpha * stats.norm.pdf(frame[pixel],mean[pixel][j],sig[pixel][j])
                mean[pixel][j] = (1 - ro) * mean[pixel][j] + ro * frame[pixel]
                var = (1 - ro) * sig[pixel]**2 + ro * (frame[pixel] - mean[pixel][j]) ** 2
                sig[pixel] = var**(0.5)
                omega[pixel][j] = (1 - alpha) * omega[pixel][j] + alpha
                gaussianMatched = 1
            else:
                omega[pixel][j] = (1 - alpha) * omega[pixel][j]
            sumOmega = sumOmega + omega[pixel][j]
               
        for j in range(0, K):
            omega[pixel][j] = omega[pixel][j] / sumOmega
            ratio[j] = omega[pixel][j] / sig[pixel][j]

        # sort in terms of omega/sigma
        (ratio,omega,mean,sig)= sort(K,ratio,omega,mean,sig,pixel)


        # if unmatched
        if gaussianMatched == 0:
            mean[pixel][K - 1] = frame[pixel]
            sig[pixel][K - 1] = 9999          # a large sigma
            omega[pixel][K - 1] = 0.000001    # a small omega

        sumOmega = 0
        B = 0
        for j in range(0, K):
            sumOmega = sumOmega + omega[pixel][j]
            if sumOmega > T:
                B = j
                break
            
        for j in range(0, B + 1 ):
            if gaussianMatched == 0 or abs(frame[pixel] - mean[pixel][j]) > (2.5 * sig[pixel][j]):
                # foreground pixel
                foreground[pixel] = 255
                background[pixel] = mean[pixel][j]
                break
            else: 
                # background pixel
                foreground[pixel] = 0
                background[pixel] = frame[pixel]

    return background, foreground



def compileVideo(nFrames, videoWidth, videoHeight,filename):
    """compile frames to video"""
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    print ("Trying to compile ", filename, "file")
    outputVideo = cv2.VideoWriter(r"%s.avi" % (filename), fourcc, 30.0, (videoWidth, videoHeight))
    
    for counter in range (0, nFrames-1):
        Frame = cv2.imread(r"%s/%s_%s.jpg" % (framesFolder, filename,str(int(counter)).zfill(4)), 1)
        outputVideo.write(Frame)
    outputVideo.release()
    
    

if __name__ == "__main__":
    videoFile = 'vtest.avi'
    framesFolder = './frames/'
    frameCapture = 3        # capture every Nth frame in video
    K = 3                   # number of gaussians
    alpha = 0.3             # learning rate
    T = 0.9                 # minimum portion of the data that should be accounted for in the background
    ro = 0.1                # to save time, it is not calculated on-line but determined beforehand
    
    
    videoCapture = cv2.VideoCapture(videoFile)

    # understand video propertirs
    videoWidth = round( videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
    videoHeight = round( videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frameRate = round( videoCapture.get(cv2.CAP_PROP_FPS))
    numPixels = videoWidth * videoHeight

    # extract frames from video
    numFrames = extractFrames(videoCapture, numPixels)

    # compile frames to video
    compileVideo(int(numFrames), videoWidth, videoHeight,"foreground")
    compileVideo(int(numFrames), videoWidth, videoHeight,"background")

    # end
    print("Cleaning Up")
    videoCapture.release()
    cv2.destroyAllWindows()