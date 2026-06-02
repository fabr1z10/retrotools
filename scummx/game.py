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
        self.index_file = find_file_case_insensitive(self.directory / '00.lfl')

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
        return c#c.create_animation(0)

        #exit(1)





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






