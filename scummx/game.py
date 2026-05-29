from pathlib import Path

from PIL.ImageChops import offset

from common import BinaryFile, find_file_case_insensitive
from .costume import Costume

class ResourceLocation:
    def __init__(self, id, offset):
        self.id = id
        self.offset = offset

class Game:
    def __init__(self, directory: str):
        # try to open index file
        self.fmt_to_colors = {
            0x57: 0,
            0x58: 16,
            0x59: 32,
            0x60: 16,
            0x61: 32
        }
        self.directory = Path(directory)
        self.room_loc: dict[int, ResourceLocation] = {}
        self.costume_loc: dict[int, ResourceLocation] = {}
        self.index_file = find_file_case_insensitive(self.directory, '00.lfl')

        f = BinaryFile(self.index_file, 0xFF)
        magic_number = f.read16LE()
        if magic_number == 0x0100:
            self.read_index_enhanced(f)




    def read_costume(self, idx: int):

        loc = self.costume_loc[idx]
        print(loc.id, loc.offset)
        file = BinaryFile(self.directory / f"{loc.id:02d}.lfl", 0xFF)
        #file.save('ciao.bin')
        file.seek(loc.offset)
        c = Costume(file)
        exit(1)

        print('offset=',loc.offset)

        file.advance(4)
        anims = file.readByte()
        u = file.readByte()
        format = u & 0x7F
        mirror = (u & 0x80) != 0
        file.readByte()
        anim_cmd_offset = file.read16LE()
        frame_offset = loc.offset + 9
        for i in range(16):
            print(i, file.get16LE(frame_offset + 2*i))


        data_offset = loc.offset + 41
        print(anims, anim_cmd_offset)
        print('frame offset:', frame_offset)
        print('anim cmd offset:', anim_cmd_offset)
        file.seek(data_offset)
        #print('ì',file.readByte())
        for anim in range(anims):
            print('----doing anim----',anim)
            addr = file.read16LE()
            o = file.ptr
            aa = loc.offset + addr
            file.seek(aa)
            mask = file.read16LE()
            print(f"Anim: {anim}, mask: {mask & 0xFFFF:016b} {mask}")
            usemask=0xFFFF
            i=0
            while True:
                if mask & 0x8000:
                    j = file.readByte()
                    #print(j)
                    if j ==0xFF:
                        j=0xFFFF
                    if usemask & 0x8000:
                        if j==0xFFFF:
                            curpos = 0xFFFF
                            start=0
                            frame=i
                        else:
                            extra = file.readByte()
                            #print('extra=',extra)
                            cmd = file.get(loc.offset + anim_cmd_offset + j)
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
                            print(f"Limb: {i}, curpos: {curpos}, start: {start}, end: {end}, frame: {frame}")
                    else:
                        if j != 0xFFFF:
                            f.readByte()
                i += 1
                usemask <<= 1
                mask <<= 1
                if mask & 0xFFFF == 0:
                    break
            file.seek(o)


        for i in range(16):
            code = file.get(loc.offset + anim_cmd_offset + i) & 0x7F
            print("fo", i, file.get16LE(frame_offset + i*2), code)
        exit(1)
        #     i=0
        #     usemask = 0xFFFF
        #     while True:
        #         if mask & 0x8000:
        #             j = file.readByte()
        #             if j == 0xFF:
        #                 j = 0xFFFF
        #             if usemask & 0x8000:
        #                 if j == 0xFFFF:
        #                     curpos = 0xFFFF
        #                     start = 0
        #                     frame = i
        #                 else:
        #                     extra = file.readByte()
        #
        #
        #             exit(1)
        #         else:
        #             i+=1
        #             usemask <<= 1
        #             mask <<= 1
        #
        #
        #
        #
        # exit(1)
        #
        # aa=file.read16LE()
        # print(aa)
        # #print(file.data[data_offsets])
        # exit(1)
        #
        # print(f"# mirror = {mirror}")
        # print(f"# format = {format}")
        # palette_idx = base_ptr + 8
        # frame_offsets = base_ptr + 9 + 2*dataOffset
        # data_offsets = base_ptr + 34
        # file.seek(frame_offsets)
        # print(file.readByte())




    def read_index_enhanced(self, f):
        self.num_global_obj = f.read16LE()
        f.advance(self.num_global_obj)
        print(self.num_global_obj)
        self.num_rooms = f.readByte()
        print(self.num_rooms)
        f.advance(self.num_rooms)
        for i in range(self.num_rooms):
            self.room_loc[i] = ResourceLocation(i, f.read16LE())
        self.num_costumes = f.readByte()
        print(self.num_costumes)
        for i in range(self.num_costumes):
            self.costume_loc[i] = ResourceLocation(f.readByte(), -1)
        for i in range(self.num_costumes):
            self.costume_loc[i].offset = f.read16LE()
        #for a,b in self.costume_loc.items():
        #    print(a, b.id, b.offset)






