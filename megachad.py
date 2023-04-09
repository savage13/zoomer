#!/usr/bin/env python3

import sys
from PIL import Image

from PIL import GifImagePlugin
GifImagePlugin.LOADING_STRATEGY = GifImagePlugin.LoadingStrategy.RGB_AFTER_DIFFERENT_PALETTE_ONLY



im = Image.open(sys.argv[1])
#im = Image.open("893702689693773895.gif")
#im = im.convert('RGBA')


#im = im.convert('RGB')

# newim = []
# for item in im.getdata():
#     if item[:3] == (255,255,255):
#         newim.append((255,255,255,0))
#     else:
#         newim.append(item)

# im.putdata(newim)

# im.save('crap.gif')
#im.set_colorkey(255,255,255)

#im = im.convert('L') # convert image to grayscale

TIME = 3.3
FPS = 30
STEPS = TIME * 30
DURATION = TIME * 1000 // STEPS
DN = int(2*100 // STEPS)
print(FPS, STEPS, DURATION, TIME, DN, im.info, im.n_frames)

fix_alpha = False

if fix_alpha:
    data = im.getdata()
    vout = []
    width, height = im.size
    for v in data:
        if v[3] < 20:
            vout.append((255,0,255,0))
        else:
            vout.append(v)
    im.putdata(vout)

frames = []

wh = im.size

size = [1.2, 1.3, 1.25, 1.5]
size = [(int(wh[0]*k), int(wh[1]*k)) for k in size]

pos = [
    [-80,-20, 0, 0],
    [0, 0, -30, 40],
    [60, -10, 0, 0 ],
    [0, 0, 50, -30 ]
]

N = im.n_frames
k = 0

bgcolor = 0xff00ff

for j in range(len(pos)):
    p = pos[j]
    start, end = p[0], p[1]
    d = 'x'
    if p[0] == 0 and p[1] == 0:
        start, end = p[2], p[3]
        d = 'y'
    sign = 1
    if start > end:
        sign = -1
    for i in range(start, end, sign * DN):
        im.seek(k%N)
        f = im.convert('RGBA').resize(size[j], Image.Resampling.LANCZOS)
        if d == 'x':
            dx = (i,0)
        else:
            dx = (0,i)
        f = f.rotate(0, translate=dx)
        tmp = Image.new('RGBA', im.size, color=bgcolor)
        tmp.paste(f, (0,0))
        frames.append(tmp)
        k += 1

frames[0].save(sys.argv[2],
               transparent=bgcolor,
               background=bgcolor,
               save_all=True, disposal=2,
               append_images=frames[1:],
               duration=90, loop=0)

