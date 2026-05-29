from pathlib import Path


class BinaryFile:
    def __init__(self, filename, encode: int = 0):
        if not 0 <= encode <= 255:
            raise ValueError("encode must be a byte")
        with open(filename, 'rb') as f:
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

    def get(self, index: int):
        return self.data[index]

    def get16LE(self, index: int):
        lo = self.get(index)
        hi = self.get(index + 1)
        return lo + (hi << 8)




def find_file_case_insensitive(folder: Path, filename: str) -> Path:
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
