"""Generate solid-colour PNG placeholder icons with stdlib only. Replace with real artwork later."""
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "web" / "public"


def png(size, rgb=(179, 38, 30)):
    raw = b"".join(b"\x00" + bytes(rgb) * size for _ in range(size))
    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


for s in (192, 512):
    (OUT / f"icon-{s}.png").write_bytes(png(s))
print("icons written")
