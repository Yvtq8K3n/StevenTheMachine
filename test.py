import imp
from tkinter import TRUE
from recorder import Recorder
import time

count = 0
while(TRUE):
    ola = Recorder("test"+str(count))
    ola.startRecording()
    time.sleep(240)
    ola.stopRecording()
    ola.saveRecording()
    count = count +1 