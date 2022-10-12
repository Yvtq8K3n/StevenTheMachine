#!/usr/bin/env python
# -*- coding: utf-8 -*-
# VideoRecorder.py

from __future__ import print_function, division
import numpy as np
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os
import ffmpeg

RUN = 20

class VideoRecorder():
    "Video class based on openCV"
    def __init__(self, name="temp_video.avi", fourcc="MJPG", sizex=640, sizey=480, camindex=0, fps=15):
        self.isReady = False
        self.open = True
        self.duration = 0
        self.device_index = camindex
        self.fps = fps                  # fps should be the minimum constant rate at which the camera can
        self.fourcc = fourcc            # capture images (with no decrease in speed over time; testing is required)
        self.frameSize = (sizex, sizey) # video formats and sizes also depend and vary according to the camera used
        self.video_filename = name
        self.video_cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
        self.video_writer = cv2.VideoWriter_fourcc(*fourcc)
        self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
        self.frame_counts = 1
        self.start_time = time.time()

    def record(self):
        "Video starts being recorded"
        counter = 1
        counter = 1
        timer_start = time.time()
        timer_current = 0
        while self.open:
            ret, video_frame = self.video_cap.read()
            if ret:
                self.video_out.write(video_frame)
                print(str(counter) + " " + str(self.frame_counts) + " frames written " + str(timer_current))
                self.frame_counts += 1
                counter += 1
                timer_current = time.time() - timer_start
                self.duration += 1/self.fps
                gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
                cv2.imshow('video_frame', gray)
                cv2.waitKey(1)
                
                while(self.duration - audio_thread.duration >= 0.2 and audio_thread.open):
                    time.sleep(0.2)
            else:
                break

    def stop(self):
        "Finishes the video recording therefore the thread too"
        if self.open:
            self.open=False
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()

    def start(self):
        "Launches the video recording function using a thread"
        video_thread = threading.Thread(target=self.record)
        video_thread.start()

class AudioRecorder():
    "Audio class based on pyAudio and Wave"
    def __init__(self, filename="temp_audio.wav", rate=44100, fpb=1024, channels=1, audio_index=0):
    #def __init__(self, filename="temp_audio.wav", rate=44100, fpb=2**12, channels=1, audio_index=0):
        self.open = True
        self.rate = rate
        self.duration = 0
        self.frames_per_buffer = fpb
        self.channels = channels
        self.format = pyaudio.paInt16
        self.audio_filename = filename
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      input_device_index=audio_index,
                                      frames_per_buffer = self.frames_per_buffer)
        self.audio_frames = []

    def record(self):
        "Audio starts being recorded"
        self.stream.start_stream()
        t_start = time.time_ns()
        while self.open:
            try:
                self.duration += self.frames_per_buffer / self.rate 
                data = self.stream.read(self.frames_per_buffer)
                self.audio_frames.append(data)
            except Exception as e:
                print('\n' + '*'*80)
                print('PyAudio read exception at %.1fms\n' % ((time.time_ns() - t_start)/10**6))
                print(e)
                print('*'*80 + '\n')
            while(self.duration - video_thread.duration >= 0.5):
                time.sleep(0.5)

    def stop(self):
        "Finishes the audio recording therefore the thread too"
        self.open = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        waveFile = wave.open(self.audio_filename, 'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(self.audio.get_sample_size(self.format))
        waveFile.setframerate(self.rate)
        waveFile.writeframes(b''.join(self.audio_frames))
        waveFile.close()

    def start(self):
        "Launches the audio recording function using a thread"
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()

def start_AVrecording(filename="test", audio_index=0, sample_rate=44100):
    global video_thread
    global audio_thread
    video_thread = VideoRecorder()
    audio_thread = AudioRecorder(audio_index=audio_index, rate=sample_rate)

    video_thread.start()
    audio_thread.start()
    return filename

def stop_AVrecording(filename="test"):
    audio_thread.stop()

    #Only stop of video has all frames
    frame_counts = video_thread.frame_counts
    while (frame_counts <= RUN * video_thread.fps):
        #print("Making work")
        frame_counts = video_thread.frame_counts
    video_thread.stop()


    #Resumo
    elapsed_time = time.time() - video_thread.start_time
    recorded_fps = frame_counts / elapsed_time
    print("total frames " + str(frame_counts))
    print("elapsed time " + str(elapsed_time))
    print("recorded fps " + str(recorded_fps))
    print("ima stuck")
   

    print("slow are u?")

    # Makes sure the threads have finished
    while threading.active_count() > 1:
        time.sleep(1)

    print("test it")
    video_stream = ffmpeg.input(video_thread.video_filename)
    print("harder it")
    audio_stream = ffmpeg.input(audio_thread.audio_filename)
    print("Love it")
    stream = ffmpeg.output(video_stream, audio_stream, "out.mp4")
    print("Yeaagg")
    ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
    print("What?")
     

    # Merging audio and video signal
    '''if abs(recorded_fps - 6) >= 0.01:    # If the fps rate was higher/lower than expected, re-encode it to the expected
        print("Re-encoding")
        cmd = "ffmpeg -r " + str(recorded_fps) + " -i temp_video.avi -pix_fmt yuv420p -r 6 temp_video2.avi"
        subprocess.call(cmd, shell=True)
        print("Muxing")
        cmd = "ffmpeg -y -ac 2 -channel_layout mono -i temp_audio.wav -i temp_video2.avi -pix_fmt yuv420p " + filename + ".avi"
        subprocess.call(cmd, shell=True)
    else:
        print("Normal recording\nMuxing")
        cmd = "ffmpeg -y -ac 2 -channel_layout mono -i temp_audio.wav -i temp_video.avi -pix_fmt yuv420p " + filename + ".avi"
        subprocess.call(cmd, shell=True)
        print("..")'''

def file_manager(filename="test"):
    "Required and wanted processing of final files"
    local_path = os.getcwd()
    '''if os.path.exists(str(local_path) + "/temp_audio.wav"):
        os.remove(str(local_path) + "/temp_audio.wav")
    if os.path.exists(str(local_path) + "/temp_video.avi"):
        os.remove(str(local_path) + "/temp_video.avi")
    if os.path.exists(str(local_path) + "/temp_video2.avi"):
        os.remove(str(local_path) + "/temp_video2.avi")
    # if os.path.exists(str(local_path) + "/" + filename + ".avi"):'''
    #     os.remove(str(local_path) + "/" + filename + ".avi")

def list_audio_devices(name_filter=None):
    pa = pyaudio.PyAudio()
    device_index = None
    sample_rate = None
    for x in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(x)
        print(pa.get_device_info_by_index(x))
        if name_filter is not None and name_filter in info['name']:
            device_index = info['index']
            sample_rate = int(info['defaultSampleRate'])
            break
    return device_index, sample_rate

if __name__ == '__main__':
    start_AVrecording()
    time.sleep(RUN)
    stop_AVrecording()
    file_manager()