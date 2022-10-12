from faulthandler import disable
from pickle import FALSE
from time import time
import tkinter as tk
from datetime import date, datetime
from tkinter.tix import Tree
from turtle import position
import threading
import time
import app
from cam_audio_recorder import start_AVrecording, stop_AVrecording 

FILE = "exercises.txt"
global stop_video
     
class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent,*args, **kwargs)
        self.parent = parent
        self.stopVideo = False
        self.repeatVideo = False
        
        # Set screen dimensions
        height = self.parent.winfo_screenheight()
        width = self.parent.winfo_screenwidth()
        self.parent.geometry("250x350+"+str(width-250 * 2)+"+"+str((int)(height/4)))

        #Read file
        self.datetime = datetime.now()
        self.counter = 0
        self.exercises = open(FILE, 'r').read().splitlines()

        self.startCamThread()

        #Create Interative Menu
        self.lblExercise = tk.Label(parent, text=self.exercises[self.counter], fg ="red", height=4, width=32,
            font=("Comic Sans MS", 12, "bold"))  
        self.lblExercise.pack()
        
        redbutton = tk.Button(parent, text="SEND", fg ="red", height=4, width=16,
            font=("Times New Roman", 8, "bold"), command=self.save_and_send_cam_audio_recording)  
        redbutton.pack()
        redbutton = tk.Button(parent, text ="REPEAT", fg ="red", height=4, width=16,
            font=("Times New Roman", 8, "bold"), command=self.restart)   
        redbutton.pack()
        redbutton = tk.Button(parent, text ="EXIT", fg ="red", height=4, width=16,
            font=("Times New Roman", 8, "bold"))
        redbutton.pack()

    def startCamThread(self):
        self.thread = threading.Thread(target=self.startRecord, daemon=True)
        self.thread.start()

    def startRecord(self):
        while(True):
            start_AVrecording(self.datetime.strftime("%Y_%m_%d_%H_%M_%S_"+str(self.exercises[self.counter])))

            print("Recording for {0}".format(self.datetime.strftime("%Y_%m_%d_%H_%M_%S_"+str(self.exercises[self.counter]))))
            while(not self.stopVideo):
                pass

            stop_AVrecording(self.datetime.strftime("%Y_%m_%d_%H_%M_%S_"+str(self.exercises[self.counter])))

            if(self.repeatVideo):
                self.repeatVideo = False
            else:
                self.counter = self.counter + 1
                if (self.counter >= len(self.exercises)):
                    break
        
                self.lblExercise.config(text=self.exercises[self.counter])
                self.lblExercise.config(state=tk.DISABLED)
            
            self.stopVideo = False


    def save_and_send_cam_audio_recording(self):
        self.stopVideo = True
        
    
    def restart(self):
        self.stopVideo = True
        self.repeatVideo = True

if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()