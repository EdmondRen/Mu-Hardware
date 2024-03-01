import sys
sys.path.append("..")

from importlib import reload
import helper_visa as vs
import time
import joblib
from pylab import *
reload(vs)
import scipy
import scipy.signal
import numpy as np


# from IPython.display import clear_output
# %matplotlib widget

import cv2


# cv2.namedWindow('img', cv2.WINDOW_NORMAL)
# for i in range(100000):
#     A = np.random.randn(100,100)
#     cv2.imshow("img", A)
#     cv2.waitKey(1)  # it's needed, but no problem, it won't pause/wait
# a=input("press any key to stop")


scope = vs.connect(address = "USB0::0x2A8D::0x9008::MY63160110::0::INSTR", timeout=30_000) # set 30 second





trigger_channel = 1
trigger_mode    = "AUTO"

acquire_channel = 1
n_avg = 20
fft_trace_length = 4096
acquire_length = fft_trace_length*n_avg



waterfall_buffer_frames = 700
waterfall_to_spectrum_ratio = 2
spectrum_buffer_frames = 30
spectrum_vertical_bins = int(waterfall_buffer_frames/waterfall_to_spectrum_ratio)
spectrum_vertical_range_dbV = [-180,0]


# Set Scope Run Mode
scope.write(f"ACQuire:BANDwidth MAX")
scope.write(f":ACQuire:TYPE {trigger_mode}")
scope.write(f":ACQuire:POINts:ANALog {acquire_length}")
# Get the Scope calibration data 
calibration_data = vs.get_calibration(scope)


# Initialize two arrays
# One for spectrum
# One for waterfall
img_spectrum  = np.zeros((spectrum_vertical_bins, fft_trace_length//2))
img_waterfall = np.zeros((waterfall_buffer_frames, fft_trace_length//2))

def update_waterfall(img_waterfall, newline):
    for i_row in range(1,img_waterfall.shape[0]):
        img_waterfall[i_row] = img_waterfall[i_row-1] 
    img_waterfall[0] = newline
    return img_waterfall

def update_spectrum(img_spectrum, img_waterfall, spectrum_buffer_frames):
    for i_col in np.arange(img_waterfall.shape[1]):
        img_spectrum[:,i_col] = np.histogram(img_waterfall[:spectrum_buffer_frames,i_col], bins = spectrum_vertical_bins, range=spectrum_vertical_range_dbV)[0]

    
# fig, (a0, a1) = plt.subplots(2, 1, figsize=(16,9), gridspec_kw={'height_ratios': [1, waterfall_to_spectrum_ratio]})  
# f, (a0, a1) = plt.subplots(2, 1, figsize=(16,9), height_ratios=[1, waterfall_to_spectrum_ratio])  
    

cv2.namedWindow('img', cv2.WINDOW_NORMAL)
cv2.startWindowThread()


# while(True):
# if 1:
t1 = time.time()
for j in range(100):
    try:
        data, time_series=vs.read_waveform(scope, trigger_channel = trigger_channel, read_channel = [acquire_channel], acquire_length = acquire_length, calibrate = True, initialize = False, calibration_data=calibration_data)
        
        sampling_frequency = 1/(time_series[1]-time_series[0])
        fft_freq, pxx  = scipy.signal.periodogram(data[acquire_channel].reshape(n_avg, fft_trace_length), fs=sampling_frequency, axis=1)
        psd = np.log10(np.sqrt(np.mean(pxx, axis=0)))[1:]*20
        fft_freq = fft_freq[1:]


        # Add new line to waterfall
        img_waterfall = update_waterfall(img_waterfall, psd)


        # update spectrum and plot,
        # BUT only every 0.1 seconds
        t2 = time.time()

        # print(t2-t1)

        if (t2-t1)>0.1:
            # clear_output(wait=True)
    
            print(j,t2-t1)
            t1=t2
            # update_spectrum(img_spectrum, img_waterfall,spectrum_buffer_frames)
            # a0.imshow(img_spectrum,origin="lower")
            # a1.imshow(img_waterfall)
            # plt.draw()

            cv2.imshow("img", img_waterfall)
            # print(img_waterfall[0])
            cv2.waitKey(1)  # it's needed, but no problem, it won't pause/wait            
            
        else:
            continue


    except KeyboardInterrupt:
        print("  KeyboardInterrupt. You pressed ctrl c...")
        break                
    except Exception as e: # Any other exception
        print("  Exception:", str(e)) # Displays the exception without raising it
        continue     

vs.disconnect(scope)

a=input("press to exit")       


