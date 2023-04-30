#!/usr/bin/env python3

import cv2
import torch
import random
import time
import numpy as np
import tensorrt as trt
from collections import OrderedDict,namedtuple

import math

import streamer

#DEF YOLO START

binding_addrs = None
context = None
bindings = None

w = '/home/name/best.trt'
device = torch.device('cuda:0')

def init_tensorrt():
    global binding_addrs
    global context
    global bindings

    # Infer TensorRT Engine
    Binding = namedtuple('Binding', ('name', 'dtype', 'shape', 'data', 'ptr'))
    logger = trt.Logger(trt.Logger.INFO)
    trt.init_libnvinfer_plugins(logger, namespace="")
    with open(w, 'rb') as f, trt.Runtime(logger) as runtime:
        model = runtime.deserialize_cuda_engine(f.read())
    bindings = OrderedDict()
    for index in range(model.num_bindings):
        name = model.get_binding_name(index)
        dtype = trt.nptype(model.get_binding_dtype(index))
        shape = tuple(model.get_binding_shape(index))
        data = torch.from_numpy(np.empty(shape, dtype=np.dtype(dtype))).to(device)
        bindings[name] = Binding(name, dtype, shape, data, int(data.data_ptr()))
    binding_addrs = OrderedDict((n, d.ptr) for n, d in bindings.items())
    context = model.create_execution_context()

    # warmup for 10 times
    for _ in range(10):
        tmp = torch.randn(1,3,480,320).to(device)
        binding_addrs['images'] = int(tmp.data_ptr())
        context.execute_v2(list(binding_addrs.values()))




def letterbox(im, new_shape=(480, 320), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, r, (dw, dh)

def postprocess(boxes,r,dwdh):
    dwdh = torch.tensor(dwdh*2).to(boxes.device)
    boxes -= dwdh
    boxes /= r
    return boxes

names = ['bola', 'gawang']
colors = {name:[random.randint(0, 255) for _ in range(3)] for i,name in enumerate(names)}
#DEF YOLO END

videocap = None


class Tracking:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.m = 100.0

    def set(self, tar):
        self.x = tar.x
        self.y = tar.y
        self.m = tar.m

def detect(track_ball):

    global videocap

    global bindings
    global binding_addrs
    global context

    img = videocap.read_in()

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    image = img.copy()
    image, ratio, dwdh = letterbox(image, auto=False)
    image = image.transpose((2, 0, 1))
    image = np.expand_dims(image, 0)
    image = np.ascontiguousarray(image)

    im = image.astype(np.float32)

    im = torch.from_numpy(im).to(device)
    im/=255

    start = time.perf_counter()
    binding_addrs['images'] = int(im.data_ptr())
    context.execute_v2(list(binding_addrs.values()))
    exec_cost = time.perf_counter()-start

    nums = bindings['num_dets'].data
    boxes = bindings['det_boxes'].data
    classes = bindings['det_classes'].data

    boxes = boxes[0,:nums[0][0]]
    classes = classes[0,:nums[0][0]]

    for box,cl in zip(boxes,classes):
        box = postprocess(box,ratio,dwdh).round().int()
        name = names[cl]
        color = colors[name]
        cv2.rectangle(img,tuple(box[:2].tolist()),tuple(box[2:].tolist()),color,2)

    videocap.store_out(img)


def startInference():

    global videocap

    init_tensorrt()

    videocap = streamer.VideoCapture()
    
    print('Inference started...')
    return 0

def inferenceLoop(track_ball):
    while(True):
        detect(track_ball)
