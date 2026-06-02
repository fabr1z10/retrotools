from common import BinaryFile
from PIL import Image
from common import EGA_RGBA, Size
import copy

class Sprite:
    def __init__(self):
        self.img: Image = None
        self.width = None
        self.height = None
        self.relx = None
        self.rely = None
        self.movex = None
        self.movey = None

class Limb:
    def __init__(self, current, start, end, frame):
        self.current = current
        self.start = start
        self.end = end
        self.frame = frame

class Anim:
    def __init__(self):
        self.limbs = [None]*16



class Costume:
    def __init__(self, b: BinaryFile):
        self.img = []
        for i in range(16):
            self.img.append(dict())
        self.base_ptr = b.ptr
        b.advance(4)
        self.anims = b.readByte()
        u = b.readByte()
        self.format = u & 0x7F
        self.mirror = (u & 0x80) != 0
        b.readByte()
        self.anim_cmd_offset = b.read16LE()
        self.frame_offset = self.base_ptr + 9
        self.data_offset = self.base_ptr + 41
        print(f'# anims: {self.anims}')
        print(f'fmt: {self.format}')
        print(f'mirror: {self.mirror}')
        print(f'anim_cmd_offset: {self.anim_cmd_offset}')
        #for i in range(55):
        #    print(i, b.get(self.base_ptr + self.anim_cmd_offset + i) & 0x7F)
        b.seek(self.data_offset)
        #print('ì',file.readByte())
        self.animations = []
        for anim in range(self.anims):
            print('----doing anim----',anim)
            a = Anim()
            addr = b.read16LE()
            o = b.ptr
            aa = self.base_ptr + addr
            b.seek(aa)
            mask = b.read16LE()
            print(f"Anim: {anim}, mask: {mask & 0xFFFF:016b} {mask}")
            usemask=0xFFFF
            i=0
            while True:
                if mask & 0x8000:
                    j = b.readByte()
                    #print(j)
                    if j ==0xFF:
                        j=0xFFFF
                    if usemask & 0x8000:
                        if j==0xFFFF:
                            curpos = 0xFFFF
                            start=0
                            frame=i
                        else:
                            extra = b.readByte()
                            #print('extra=',extra)
                            cmd = b.get(self.base_ptr + self.anim_cmd_offset + j)
                            #print('cmd=',cmd)
                            if cmd == 0x7A:
                                pass
                            elif cmd == 0x79:
                                pass
                            else:
                                curpos = j
                                start=j
                                end = j + (extra & 0x7F)
                                if extra & 0x80:
                                    curpos |= 0x8000
                                frame = anim
                            a.limbs[i] = Limb(curpos, start, end, frame)
                            print(f"Limb: {i}, curpos: {curpos}, start: {start}, end: {end}, frame: {frame}")

                    else:
                        if j != 0xFFFF:
                            b.readByte()
                i += 1
                usemask <<= 1
                mask <<= 1
                if mask & 0xFFFF == 0:
                    break
            self.animations.append(a)
            print('add')

            b.seek(o)

        print(len(self.animations))
        limb_min = [None] * 16
        limb_max = [None]*16
        self.codes = dict()
        for i, value in enumerate(self.animations):
            print(f"Doing animation {i}")
            for limb in range(16):
                if value.limbs[limb]:
                    print(f"Doing limb {limb}")
                    for u in range(value.limbs[limb].start, value.limbs[limb].end+1):
                        code = b.get(self.base_ptr + self.anim_cmd_offset + u) & 0x7F
                        self.codes[u] = code
                        if limb_min[limb] is None or code < limb_min[limb]:
                            limb_min[limb] = code
                        if limb_max[limb] is None or code > limb_max[limb]:
                            limb_max[limb] = code

            #exit(1)
        print(limb_min)
        print(limb_max)
        print("CODES:", self.codes)
        for i in range(16):
            if limb_min[i] is not None:
                for u in range(limb_min[i], limb_max[i]+1):
                    self.read_gfx(i, u, b)
        print(self.img[0])
        # for j, b in enumerate(self.img):
        #     print(f"LIMB: {j}")
        #     for i, spr in enumerate(b):
        #         print(f"FRAME {i}")

                    #img.save(f"pino_{i}_{u}.png")
        # frame_ptr = b.get16LE(self.frame_offset + 2 * 1)
        # src_ptr = base_ptr + b.get16LE(base_ptr + frame_ptr + 5 * 2)
        # b.seek(src_ptr)
        # width = b.read16LE()
        # height = b.read16LE()
        # relx = b.read16LE()
        # rely = b.read16LE()
        # movex = b.read16LE()
        # movey = b.read16LE()
        # self.read_gfx(b, Size(width, height), f"cicc.png")

        # u = file.readByte()
        # format = u & 0x7F
        # mirror = (u & 0x80) != 0
        # file.readByte()
        # anim_cmd_offset = file.read16LE()
        # frame_offset = loc.offset + 9


    def create_animation(self, anim_ids: list[int]):
        curpos: list[Limb | None] = [None] * 16
        for anim_id in anim_ids:
            anim = self.animations[anim_id]
            for i, value in enumerate(anim.limbs):
                if value:
                    curpos[i] = copy.copy(value)
        actor_x = 160
        actor_y = 100

        frames = []
        fc = 0
        fpos = set()
        nframes=0
        x_min = 320
        x_max = 0
        y_min = 200
        y_max = 0
        while True:
            frame = Image.new("RGBA", (320, 200), (0, 0, 0, 0))
            frame_positions = []
            x_move = -72
            y_move = -100

            for limb, u in enumerate(curpos):
                if u:
                    print(f"drawing limb {limb}/{u.current}")
                    frame_positions.append(u.current)
                    code = self.codes[u.current]
                    spr = self.img[limb][code]
                    #spr.img.save(f"pino{u[0]}_{u[1]}.png")
                    x_move_cur = x_move + spr.relx
                    y_move_cur = y_move + spr.rely
                    x_move += spr.movex
                    y_move -= spr.movey
                    x = actor_x + x_move_cur
                    y = actor_y + y_move_cur
                    #frame.paste(spr.img, (x, y))
                    frame.alpha_composite(spr.img, (x, y))
                    x_min = min(x_min, x)
                    x_max = max(x_max, x + spr.width)
                    y_min = min(y_min, y)
                    y_max = max(y_max, y + spr.height)
                    print(f"CIAO CIAO ", x_min, x_max, y_min, y_max)
                    u.current += 1
                    if u.current > u.end:
                        u.current = u.start
            if tuple(frame_positions) in fpos:
                break
            fpos.add(tuple(frame_positions))
            frame.save(f"frame_{fc}.png")
            nframes +=1
            print('frame pos: ', frame_positions)
            frames.append(frame)
            fc += 1

        print(f'saving animation {anim_id}, frames: {nframes}')
        bbox = (x_min, y_min, x_max, y_max)
        #cropped_frames = [frame.crop(bbox) for frame in frames]
        frames[0].save(
            "anim.gif",
            save_all=True,
            append_images=frames[1:],
            duration=1000,  # ms per frame
            loop=0,  # infinite loop,
            disposal=2,

        )



    def read_gfx(self, limb: int, code: int, f: BinaryFile):
        frame_ptr = f.get16LE(self.frame_offset + 2 * limb)
        src_ptr = self.base_ptr + f.get16LE(self.base_ptr + frame_ptr + code * 2)
        f.seek(src_ptr)
        spr = Sprite()
        spr.width = f.read16LE()
        spr.height = f.read16LE()
        spr.relx = f.read16LE_signed()
        spr.rely = f.read16LE_signed()
        spr.movex = f.read16LE_signed()
        spr.movey = f.read16LE_signed()
        print(f"Decoding {limb} / {code}")
        print(f"width: {spr.width}, height: {spr.height}, relx: {spr.relx}, "
              f"rely: {spr.rely}, movex: {spr.movex}, movey: {spr.movey}, {src_ptr-self.base_ptr}")

        shr = 4     # this is linked to colors: 4 for 16, 5 for 32
        mask = 15
        #img = Image.new("P", (width, height))
        img = Image.new("RGBA", (spr.width, spr.height), (0, 0, 0, 0))
        #img.putpalette(EGA)
        img.info["transparency"] = 0
        # start RLE decode
        x = 0
        y = 0
        while x < spr.width:
            u = f.readByte()
            color = u >> shr
            length = u & mask
            if length == 0:
                length = f.readByte()
            #print(color, length, x, y)
            for i in range(length):
                if color:
                    pcolor = 0 if color == 1 else color
                    img.putpixel((x, y), EGA_RGBA[pcolor])
                y += 1
                if y >= spr.height:
                    y = 0
                    x += 1

        # store sprite
        spr.img = img
        print(f"Storing {limb} {code}")
        self.img[limb][code] = spr
        spr.img.save(f"pino_{limb}_{code}.png")




