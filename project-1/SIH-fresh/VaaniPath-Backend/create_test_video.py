#!/usr/bin/env python3
"""
Create a minimal valid MP4 video file for testing
"""
import struct

def create_minimal_mp4(filename):
    """Create a minimal valid MP4 file"""
    
    with open(filename, 'wb') as f:
        # ftyp box (file type box)
        ftyp = b'ftypisom\x00\x00\x00\x00isomiso2mp41'
        f.write(struct.pack('>I', len(ftyp) + 8))
        f.write(ftyp)
        
        # mdat box (media data box) - minimal video data
        # This is a simplified MP4 structure
        video_data = b'\x00' * 1024  # 1KB of dummy video data
        mdat_size = len(video_data) + 8
        f.write(struct.pack('>I', mdat_size))
        f.write(b'mdat')
        f.write(video_data)
        
        # moov box (movie box) - minimal structure
        moov_data = (
            b'\x00\x00\x00\x6cmvhd' +  # mvhd header
            b'\x00\x00\x00\x00' +  # version and flags
            b'\x00\x00\x00\x00' +  # creation time
            b'\x00\x00\x00\x00' +  # modification time
            b'\x00\x00\x03\xe8' +  # timescale (1000)
            b'\x00\x00\x00\x00' +  # duration
            b'\x00\x01\x00\x00' +  # playback speed (1.0)
            b'\x01\x00' +  # volume (1.0)
            b'\x00' * 10 +  # reserved
            b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' +  # matrix
            b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
            b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
            b'\x00\x00\x00\x00' +  # preview time
            b'\x00\x00\x00\x02'  # next track ID
        )
        
        moov_size = len(moov_data) + 8
        f.write(struct.pack('>I', moov_size))
        f.write(b'moov')
        f.write(moov_data)

if __name__ == "__main__":
    create_minimal_mp4("test_video.mp4")
    print("✅ Created test_video.mp4 (minimal valid MP4)")
