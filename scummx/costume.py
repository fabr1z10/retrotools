from common import BinaryFile

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
        base_ptr = b.ptr
        b.advance(4)
        self.anims = b.readByte()
        u = b.readByte()
        self.format = u & 0x7F
        self.mirror = (u & 0x80) != 0
        b.readByte()
        self.anim_cmd_offset = b.read16LE()
        self.frame_offset = base_ptr + 9
        self.data_offset = base_ptr + 41
        print(f'# anims: {self.anims}')
        print(f'fmt: {self.format}')
        print(f'mirror: {self.mirror}')
        print(f'anim_cmd_offset: {self.anim_cmd_offset}')
        for i in range(55):
            print(i, b.get(base_ptr + self.anim_cmd_offset + i) & 0x7F)
        b.seek(self.data_offset)
        #print('ì',file.readByte())
        self.animations = []
        for anim in range(self.anims):
            print('----doing anim----',anim)
            a = Anim()
            addr = b.read16LE()
            o = b.ptr
            aa = base_ptr + addr
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
                            cmd = b.get(base_ptr + self.anim_cmd_offset + j)
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
        for a in self.animations:
            if a.limbs[1]:
                limb=1
                for u in range(4,5):#a.limbs[1].start, a.limbs[1].end):
                    code = b.get(base_ptr + self.anim_cmd_offset + u) & 0x7F
                    print(f"Code={code}")
                    frame_ptr = b.get16LE(self.frame_offset + 2 * limb)
                    src_ptr = base_ptr + b.get16LE(base_ptr + frame_ptr + code * 2)
                    b.seek(src_ptr)
                    width = b.read16LE()
                    height = b.read16LE()
                    print(f'width: {width}')
                    print(f'height: {height}')
                    print(u, code)
                exit(1)
        # u = file.readByte()
        # format = u & 0x7F
        # mirror = (u & 0x80) != 0
        # file.readByte()
        # anim_cmd_offset = file.read16LE()
        # frame_offset = loc.offset + 9

