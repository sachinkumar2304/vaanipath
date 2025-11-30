#!/usr/bin/env python3
"""
Create a real minimal MP4 video using proper structure
"""
import struct
import io

def create_mp4_with_video_track():
    """Create a minimal but valid MP4 file with actual video data"""
    
    output = io.BytesIO()
    
    # ftyp box
    ftyp_data = b'isom\x00\x00\x00\x00isomiso2mp41'
    ftyp_box = struct.pack('>I', len(ftyp_data) + 8) + b'ftyp' + ftyp_data
    output.write(ftyp_box)
    
    # Create a minimal mdat box with some video frame data
    # This is a simplified H.264 NAL unit
    video_data = (
        b'\x00\x00\x00\x01'  # NAL start code
        b'\x67'  # SPS (Sequence Parameter Set)
        b'\x42\x00\x0a\xff\xe1\x00\x16\x96\x54\x05\x01\x0b\xf8\x00\x00\x03\x00\x80\x00\x00\x1f\x48\x00'
        b'\x00\x00\x01'  # NAL start code
        b'\x68'  # PPS (Picture Parameter Set)
        b'\xce\x06\xe2'
        b'\x00' * 512  # Dummy frame data
    )
    
    mdat_box = struct.pack('>I', len(video_data) + 8) + b'mdat' + video_data
    output.write(mdat_box)
    
    # Create moov box (simplified)
    moov_data = create_moov_box()
    moov_box = struct.pack('>I', len(moov_data) + 8) + b'moov' + moov_data
    output.write(moov_box)
    
    return output.getvalue()

def create_moov_box():
    """Create a minimal moov box"""
    mvhd = create_mvhd_box()
    trak = create_trak_box()
    return mvhd + trak

def create_mvhd_box():
    """Create movie header box"""
    data = (
        b'\x00'  # version
        b'\x00\x00\x00'  # flags
        b'\x00\x00\x00\x00'  # creation time
        b'\x00\x00\x00\x00'  # modification time
        b'\x00\x00\x03\xe8'  # timescale (1000)
        b'\x00\x00\x00\x64'  # duration (100)
        b'\x00\x01\x00\x00'  # playback speed
        b'\x01\x00'  # volume
        b'\x00' * 10  # reserved
        # Matrix
        b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00'
        b'\x00\x00\x00\x00'  # preview time
        b'\x00\x00\x00\x02'  # next track ID
    )
    return struct.pack('>I', len(data) + 8) + b'mvhd' + data

def create_trak_box():
    """Create track box"""
    tkhd = create_tkhd_box()
    edts = create_edts_box()
    mdia = create_mdia_box()
    return struct.pack('>I', len(tkhd) + len(edts) + len(mdia) + 8) + b'trak' + tkhd + edts + mdia

def create_tkhd_box():
    """Create track header box"""
    data = (
        b'\x00'  # version
        b'\x00\x00\x0f'  # flags
        b'\x00\x00\x00\x00'  # creation time
        b'\x00\x00\x00\x00'  # modification time
        b'\x00\x00\x00\x01'  # track ID
        b'\x00\x00\x00\x00'  # reserved
        b'\x00\x00\x00\x64'  # duration
        b'\x00' * 8  # reserved
        b'\x00\x00'  # layer
        b'\x00\x00'  # alternate group
        b'\x01\x00'  # volume
        b'\x00' * 2  # reserved
        # Matrix
        b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00'
        b'\x00\x00\x04\x00'  # width
        b'\x00\x00\x03\x00'  # height
    )
    return struct.pack('>I', len(data) + 8) + b'tkhd' + data

def create_edts_box():
    """Create edit list box"""
    elst_data = (
        b'\x00'  # version
        b'\x00\x00\x00'  # flags
        b'\x00\x00\x00\x01'  # number of entries
        b'\x00\x00\x00\x64'  # track duration
        b'\x00\x00\x00\x00'  # media time
        b'\x00\x01\x00\x00'  # media rate
    )
    elst = struct.pack('>I', len(elst_data) + 8) + b'elst' + elst_data
    return struct.pack('>I', len(elst) + 8) + b'edts' + elst

def create_mdia_box():
    """Create media box"""
    mdhd = create_mdhd_box()
    hdlr = create_hdlr_box()
    minf = create_minf_box()
    return struct.pack('>I', len(mdhd) + len(hdlr) + len(minf) + 8) + b'mdia' + mdhd + hdlr + minf

def create_mdhd_box():
    """Create media header box"""
    data = (
        b'\x00'  # version
        b'\x00\x00\x00'  # flags
        b'\x00\x00\x00\x00'  # creation time
        b'\x00\x00\x00\x00'  # modification time
        b'\x00\x00\x03\xe8'  # timescale
        b'\x00\x00\x00\x64'  # duration
        b'\x55\xc4'  # language
        b'\x00\x00'  # quality
    )
    return struct.pack('>I', len(data) + 8) + b'mdhd' + data

def create_hdlr_box():
    """Create handler box"""
    data = (
        b'\x00'  # version
        b'\x00\x00\x00'  # flags
        b'\x00\x00\x00\x00'  # pre-defined
        b'vide'  # handler type
        b'\x00\x00\x00\x00'  # reserved
        b'\x00\x00\x00\x00'  # reserved
        b'\x00\x00\x00\x00'  # reserved
        b'VideoHandler\x00'  # name
    )
    return struct.pack('>I', len(data) + 8) + b'hdlr' + data

def create_minf_box():
    """Create media information box"""
    vmhd = create_vmhd_box()
    dinf = create_dinf_box()
    stbl = create_stbl_box()
    return struct.pack('>I', len(vmhd) + len(dinf) + len(stbl) + 8) + b'minf' + vmhd + dinf + stbl

def create_vmhd_box():
    """Create video media header box"""
    data = b'\x00\x00\x00\x00' + b'\x00' * 6 + b'\x00\x00'
    return struct.pack('>I', len(data) + 8) + b'vmhd' + data

def create_dinf_box():
    """Create data information box"""
    dref_data = b'\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x0curl\x00\x00\x00\x01'
    dref = struct.pack('>I', len(dref_data) + 8) + b'dref' + dref_data
    return struct.pack('>I', len(dref) + 8) + b'dinf' + dref

def create_stbl_box():
    """Create sample table box"""
    stsd = create_stsd_box()
    stts = create_stts_box()
    stsc = create_stsc_box()
    stsz = create_stsz_box()
    stco = create_stco_box()
    return struct.pack('>I', len(stsd) + len(stts) + len(stsc) + len(stsz) + len(stco) + 8) + b'stbl' + stsd + stts + stsc + stsz + stco

def create_stsd_box():
    """Create sample description box"""
    avc1_data = (
        b'\x00' * 6  # reserved
        b'\x00\x01'  # data reference index
        b'\x00' * 16  # reserved
        b'\x01\x00'  # width
        b'\x00\x80'  # height
        b'\x00\x48\x00\x00'  # horizontal resolution
        b'\x00\x48\x00\x00'  # vertical resolution
        b'\x00\x00\x00\x00'  # reserved
        b'\x00\x01'  # frame count
        b'\x00' * 32  # compressor name
        b'\x00\x18'  # depth
        b'\xff\xff'  # color table ID
    )
    avc1 = struct.pack('>I', len(avc1_data) + 8) + b'avc1' + avc1_data
    data = b'\x00\x00\x00\x00\x00\x00\x00\x01' + avc1
    return struct.pack('>I', len(data) + 8) + b'stsd' + data

def create_stts_box():
    """Create time-to-sample box"""
    data = b'\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01'
    return struct.pack('>I', len(data) + 8) + b'stts' + data

def create_stsc_box():
    """Create sample-to-chunk box"""
    data = b'\x00\x00\x00\x00\x00\x00\x00\x00'
    return struct.pack('>I', len(data) + 8) + b'stsc' + data

def create_stsz_box():
    """Create sample size box"""
    data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    return struct.pack('>I', len(data) + 8) + b'stsz' + data

def create_stco_box():
    """Create chunk offset box"""
    data = b'\x00\x00\x00\x00\x00\x00\x00\x00'
    return struct.pack('>I', len(data) + 8) + b'stco' + data

if __name__ == "__main__":
    mp4_data = create_mp4_with_video_track()
    with open("test_video.mp4", "wb") as f:
        f.write(mp4_data)
    print(f"✅ Created test_video.mp4 ({len(mp4_data)} bytes)")
