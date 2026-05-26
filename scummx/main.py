import sys

from pathlib import Path
from PIL import Image


gamedir = Path(sys.argv[1])



palette = [
    0,      0,      0,      # colour 0 - black
    0,      0,      170,    # colour 1 - blue
    0,      170,    0,      # colour 2 - green
    0,      170,    170,      # colour 3 - cyan
    170,    0,      0,      # colour 4 -red
    170,    0,      170,    # colour 5 - magenta
    170,85,0,
    170,170,170,
    85,85,85,
    85,85,255,
    85,255,85,
    85,255,255,
    255,85,85,
    255,85,255,
    255,255,85,
    255,255,255
] + [0] * (256-16)*3        # pad remaining 240 colors with 0s


#img.putpixel((0, 0), 1)
#img.save("prova.png")

dither_table = [0]*128
with open(gamedir / '01.LFL', 'rb') as f:
    data = bytes(b ^ 0xFF for b in f.read())
    room_width = data[4] + (data[5] << 8)
    room_height = data[6] + (data[7] << 8)
    img = Image.new("P", (room_width, room_height))
    img.putpalette(palette)
    ptr = data[0x0A] + (data[0x0B]<<8)
    print(room_width, room_height, ptr)
    # ptr = 90
    run = 0
    for x in range(room_width):
        for y in range(room_height):
            if run==0:
                u = data[ptr]
                ptr += 1
                if u & 0x80:
                    run = u & 0x7F
                    dither=True
                else:
                    run = u >> 4
                    dither=False
                color = u & 0x0F
                if run==0:
                    run = data[ptr]
                    ptr +=1
                #print(hex(u), run, color)
            if not dither:
                dither_table[y] = color
            img.putpixel((x, y), dither_table[y])
            run -= 1
    img.save("ciao.png")


with open('cino', 'wb') as g:
    g.write(data)





