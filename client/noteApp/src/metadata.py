import os
from datetime import datetime
import zlib

# Calculate the CRC32 to detect changes in files
def calculate_crc32(data: bytes) -> int:
    return zlib.crc32(data)

# Get metadata
file_path = 'project escape.md'
stat = os.stat(file_path)
with open(file_path, 'r') as file:
  file_data = file.read()

checksum = calculate_crc32(file_data)

print("filename: ", file_path)
print("inode: ", stat.st_ino)
print("crc32: ", checksum)
print("size: ", stat.st_size)
print("mtime: ", datetime.fromtimestamp(stat.st_mtime))
print("ctime: ", datetime.fromtimestamp(stat.st_birthtime))
print("state: ")


