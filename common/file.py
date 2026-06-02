from pathlib import Path
import struct

class BinaryFile:
    def __init__(self, filename: Path, encode: int = 0):
        if not 0 <= encode <= 255:
            raise ValueError("encode must be a byte")
        fname = find_file_case_insensitive(filename)
        with open(fname, 'rb') as f:
            self.data = bytes(b ^ encode for b in f.read())
        self.ptr = 0

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.data)

    def seek(self, offset: int):
        self.ptr = offset

    def advance(self, size: int):
        self.ptr += size

    def readByte(self):
        u = self.data[self.ptr]
        self.ptr += 1
        return u

    def read16LE(self):
        lo = self.readByte()
        hi = self.readByte()
        return lo + (hi << 8)

    def read16LE_signed(self):
        value = struct.unpack_from("<h", self.data, self.ptr)[0]
        self.ptr += 2
        return value

    def get(self, index: int):
        return self.data[index]

    def get16LE(self, index: int):
        lo = self.get(index)
        hi = self.get(index + 1)
        return lo + (hi << 8)




def find_file_case_insensitive(path: Path) -> Path:
    folder = path.parent
    filename = path.name
    filename_lower = filename.lower()

    matches = [
        p for p in folder.iterdir()
        if p.is_file() and p.name.lower() == filename_lower
    ]

    if len(matches) == 0:
        raise FileNotFoundError(f"No file found for '{filename}' in {folder}")

    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous file '{filename}': {[m.name for m in matches]}"
        )

    return matches[0]
