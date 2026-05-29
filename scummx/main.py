import sys
from common import BinaryFile, EGA

from pathlib import Path
from PIL import Image

gamedir = Path(sys.argv[1])

f = BinaryFile(gamedir / '01.LFL', 0xFF)
f.seek(4)
room_width = f.read16LE()
room_height = f.read16LE()
img = Image.new("P", (room_width, room_height))
img.putpalette(EGA)
f.seek(0x0A)
ptr = f.read16LE()
f.seek(ptr)

print(room_width, room_height, ptr)

dither_table = [0]*128
img = Image.new("P", (room_width, room_height))
img.putpalette(EGA)
run = 0
for x in range(room_width):
    for y in range(room_height):
        if run==0:
            u = f.readByte()
            if u & 0x80:
                run = u & 0x7F
                dither=True
            else:
                run = u >> 4
                dither=False
            color = u & 0x0F
            if run==0:
                run = f.readByte()
        if not dither:
            dither_table[y] = color
        img.putpixel((x, y), dither_table[y])
        run -= 1
img.save("ciao.png")

exit(1)

