import os
from statistics import mean
import multiprocessing as mp
import numpy as np
import datetime
from frigate.edgetpu import LocalObjectDetector, EdgeTPUProcess, RemoteObjectDetector, load_labels

my_frame = np.expand_dims(np.full((300,300,3), 1, np.uint8), axis=0)
labels = load_labels('/labelmap.txt')

######
# Minimal same process runner
######
# object_detector = LocalObjectDetector()
# tensor_input = np.expand_dims(np.full((300,300,3), 0, np.uint8), axis=0)

# start = datetime.datetime.now().timestamp()

# frame_times = []
# for x in range(0, 1000):
#   start_frame = datetime.datetime.now().timestamp()

#   tensor_input[:] = my_frame
#   detections = object_detector.detect_raw(tensor_input)
#   parsed_detections = []
#   for d in detections:
#       if d[1] < 0.4:
#           break
#       parsed_detections.append((
#           labels[int(d[0])],
#           float(d[1]),
#           (d[2], d[3], d[4], d[5])
#       ))
#   frame_times.append(datetime.datetime.now().timestamp()-start_frame)

# duration = datetime.datetime.now().timestamp()-start
# print(f"Processed for {duration:.2f} seconds.")
# print(f"Average frame processing time: {mean(frame_times)*1000:.2f}ms")

######
# Separate process runner
######
def start(id, num_detections, detection_queue, event):
  object_detector = RemoteObjectDetector(str(id), '/labelmap.txt', detection_queue, event)
  start = datetime.datetime.now().timestamp()

  frame_times = []
  for x in range(0, num_detections):
    start_frame = datetime.datetime.now().timestamp()
    detections = object_detector.detect(my_frame)
    frame_times.append(datetime.datetime.now().timestamp()-start_frame)

  duration = datetime.datetime.now().timestamp()-start
  print(f"{id} - Processed for {duration:.2f} seconds.")
  print(f"{id} - Average frame processing time: {mean(frame_times)*1000:.2f}ms")

event = mp.Event()
edgetpu_process = EdgeTPUProcess({'1': event})

start(1, 1000, edgetpu_process.detection_queue, event)
print(f"Average raw inference speed: {edgetpu_process.avg_inference_speed.value*1000:.2f}ms")

####
# Multiple camera processes
####
# camera_processes = []

# pipes = {}
# for x in range(0, 10):
#   pipes[x] = mp.Pipe(duplex=False)

# edgetpu_process = EdgeTPUProcess({str(key): value[1] for (key, value) in pipes.items()})

# for x in range(0, 10):
#   camera_process = mp.Process(target=start, args=(x, 100, edgetpu_process.detection_queue, pipes[x][0]))
#   camera_process.daemon = True
#   camera_processes.append(camera_process)

# start = datetime.datetime.now().timestamp()

# for p in camera_processes:
#   p.start()

# for p in camera_processes:
#   p.join()

# duration = datetime.datetime.now().timestamp()-start
# print(f"Total - Processed for {duration:.2f} seconds.")