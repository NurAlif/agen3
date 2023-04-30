import asyncio
import os
import fractions
import cv2
import queue
import threading
from typing import Tuple
import time

from aiortc import VideoStreamTrack
from av import VideoFrame

webcam = None

AUDIO_PTIME = 0.020 
VIDEO_CLOCK_RATE = 900
VIDEO_PTIME = 1 / 5  
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=640,
    capture_height=480,
    display_width=240,
    display_height=160,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d wbmode=0 awblock=true gainrange='8 8' ispdigitalgainrange='4 4' exposuretimerange='2000000 2000000' aelock=true !"
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


class VideoOpencvTrack(VideoStreamTrack):
    def __init__(self, cap):
        super().__init__()
        self.cap = cap

    _start: float
    _timestamp: int

    async def next_timestamp(self) -> Tuple[int, fractions.Fraction]:
        if self.readyState != "live":
            print("ERROR track unready!")
            return None

        if hasattr(self, "_timestamp"):
            self._timestamp += int(VIDEO_PTIME * VIDEO_CLOCK_RATE)
            wait = self._start + (self._timestamp / VIDEO_CLOCK_RATE) - time.time()
            await asyncio.sleep(wait)
        else:
            self._start = time.time()
            self._timestamp = 0
        return self._timestamp, VIDEO_TIME_BASE

    async def recv(self):
        img = self.cap.read_out()

        if img is None:
            print("emptyframe")
            return None

        pts, time_base = await self.next_timestamp()

        new_frame = VideoFrame.from_ndarray(img, format="bgr24")
        new_frame.pts = pts
        new_frame.time_base = time_base

        return new_frame


class VideoCapture:

    def __init__(self):
        self.frameOut = None
        self.frameIn = None
        self.cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()  
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read_in(self):
        return self.q.get()
    def store_out(self, frame):
        self.frameIn = frame
    def read_out(self):
        temp = self.frameOut
        self.frameOut = self.frameIn
        return temp