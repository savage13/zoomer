#!/usr/bin/env python3

# Orignal concept from https://github.com/rnbwdsh/gif_recursion
#  Rewritten to better understanding, smoother zoom, arguments and 

import os
import sys
import argparse
from PIL import Image

parser = argparse.ArgumentParser(prog = 'zoomer')
parser.add_argument('-i', '--input', required=True)
parser.add_argument('-o', '--output', required=True)
parser.add_argument('-O', '--overwrite', action='store_true')
parser.add_argument('-p', '--point', required=True)
parser.add_argument('-t', '--time', default=1)
parser.add_argument('-f', '--fps', default=30)
parser.add_argument('-c', '--crop')

args = parser.parse_args()

FPS = args.fps
TIME = args.time
STEPS = FPS * TIME
DURATION = TIME * 1000 // STEPS # in milliseconds

# Grabbed from numpy, we do not need the entire library
def linspace(start, stop, num=50, endpoint=True):
    if endpoint:
        dx = (stop - start) / (num-1)
    else:
        dx = (stop - start) / num
    return [start + i * dx for i in range(num)]

def logspace(start, stop, num=50, base=10, endpoint=True):
    import math
    vals = linspace(start, stop, num)
    return [math.pow(base, k) for k in vals]

def in_logspace(start, stop, num=50, base=10, endpoint=True):
    import math
    x0 = math.log(start, base)
    x1 = math.log(stop, base)
    return logspace(x0, x1, num=num, base=base, endpoint=endpoint)

if not os.path.exists(args.input):
    print('error input file does not exist', args.input)
    sys.exit(1)

try:
    image = Image.open(args.input)
except Exception as e:
    print("error reading image: ", e)
    sys.exit(1)
if args.crop:
    image = image.crop(list(map(int,args.crop.split(','))))
frames = []

if os.path.exists(args.output):
    if not args.overwrite:
        print('error output file exists', args.output)
        sys.exit(1)

w0 = image.size[0]
h0 = image.size[1]

px,py = list(map(float, args.point.split(',')))
# 0.2165, 0.42

x0 = w0 * px
y0 = h0 * py

scales  = in_logspace(1, 100, STEPS)
scales2 = in_logspace(0.05, 1, STEPS)

for k,(s1,s2) in enumerate(zip(scales, scales2)):
    print("Step, zoom-in, zoom-out: {:4} {:7.3f} {:7.3f}".format( k, s1, s2))
    # Crop image, zoom and "enhance"
    #   Use the inverse scale to find the cropped image size
    tx1 = (0  - x0) * 1/s1 + x0 # Left
    ty1 = (0  - y0) * 1/s1 + y0 # Top
    tx2 = (w0 - x0) * 1/s1 + x0 # Right
    ty2 = (h0 - y0) * 1/s1 + y0 # Bottom

    # Create new frame
    new_frame = image.crop([tx1,ty1,tx2,ty2]).resize((w0,h0))

    # Resize image and shrink down
    tx1 = (0  - x0) * s2 + x0 # Left
    ty1 = (0  - y0) * s2 + y0 # Top
    tx2 = (w0 - x0) * s2 + x0 # Right
    ty2 = (h0 - y0) * s2 + y0 # Bottom
    tx1,ty1,tx2,ty2 = list(map(int, [tx1,ty1,tx2,ty2]))
    w = tx2 - tx1 # Width
    h = ty2 - ty1 # Height
    tiny = image.resize((w,h))
    # Paste smaller image into new frame
    new_frame.paste( tiny, box=(tx1,ty1,tx2,ty2))

    # Append new image to set of frames
    frames.append( new_frame )

print("time(s), frame-duration(ms), steps:",TIME, DURATION, STEPS)
# save output


frames[0].save(args.output, format='GIF',
               append_images=frames[1:-1],
               save_all=True,
               duration=DURATION, loop=0)
