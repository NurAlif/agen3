#!/usr/bin/env python
import time

def current_milli_time():
    return round(time.time() * 1000)

def append(data_str):
    global file_object
    print(str(current_milli_time())+","+data_str+'\n')
    with open('/home/name/recorder.txt', 'a') as file_object:
        file_object.write(str(current_milli_time())+","+data_str+"\n")
        print("data added")