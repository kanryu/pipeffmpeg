# -*- coding: utf-8 -*-
"""
##################################################################################
# PipeFFmpeg v0.1
#
# Copyright (C) 2011 KATO Kanryu <k.kanryu@gmail.com>
#
##################################################################################
#  This file is distibuted under 3-BSD
#  See COPYING file attached.
##################################################################################
#
#    TODO:
#       * decode each frame of video stream to stdout(python get it in callback)
#       * encode each frame from stdin(python push it in callback)
#       * transcode to other codec which has ffmpeg-command
#       * support audio-stream
#
#    Abilities
#     * Get version from ffmpeg-command on your system
#     * Get codecs
#     * Get formats
#     * Get pix_fmts
#     * Get metadata from a video file
"""

import subprocess as sp
import os
import sys

FFMPEG_BIN = 'ffmpeg'
"""ffmpeg's path

if ffmpeg command doesn't exist in PATHs, you should change this."""
_attempt_finished = False


def _attempt_ffmpeg():
    global _attempt_finished
    if _attempt_finished: return
    try:
        p = sp.Popen(
            FFMPEG_BIN,
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )
        del p
        _attempt_finished = True
    except EnvironmentError:
        print "pyffmpeg: you should set pyffmpeg.FFMPEG_BIN as a valid 'ffmpeg' command path"
        raise

def get_pipe2(option=None):
    '''get pipes from ffmpeg process'''
    _attempt_ffmpeg()
    cmd = [FFMPEG_BIN]
    if option:
        if type(option) == str:
            cmd.append(option)
        if type(option) == list:
            cmd += option

    return sp.Popen(
        cmd,
        stdin=sp.PIPE,
        stdout=sp.PIPE,
    )

def get_pipe3(option=None):
    '''get pipes from ffmpeg process with stderr'''
    _attempt_ffmpeg()
    cmd = [FFMPEG_BIN]
    if option:
        if type(option) == str:
            cmd.append(option)
        if type(option) == list:
            cmd += option
    return sp.Popen(
        " ".join(cmd),
        stdin=sp.PIPE,
        stdout=sp.PIPE,
        stderr=sp.PIPE,
    )

def _plugins_gen(option, sep=' ------', stdpipe='stderr'):
    p = get_pipe3(option)
    first_skip = True
    if stdpipe == 'stderr': stdpipe = p.stderr
    if stdpipe == 'stdout': stdpipe = p.stdout
    for line in stdpipe.readlines():
        line = line.rstrip()
        if first_skip:
            if line[:len(sep)] == sep: first_skip = False
            continue
        if line == '': break
        yield line
    del p


class Codec:
    '''video/audio/subtitle codecs supported by ffmpeg'''
    types = {'V': 'video', 'A': 'audio', 'S': 'subtitle'}
    def __init__(self, line):
        self.decoding = line[1] == 'D'
        self.encoding = line[2] == 'E'
        self.type = Codec.types[line[3]]
        self.draw_horiz_band  = line[4] == 'S'
        self.direct_rendering = line[5] == 'D'
        self.frame_truncation = line[6] == 'T'
        self.name = line[8:]

    def __repr__(self):
        return '<Codec %s for %s>' % (self.name, self.type)

def get_codecs():
    '''get codecs for ffmpeg'''
    result = {}
    for line in _plugins_gen('-codecs', sep=' ------', stdpipe='stdout'):
        result[line[8:]] = Codec(line)
    return result


class Format:
    '''file formats supported by ffmpeg'''
    def __init__(self, line):
        self.demuxing = line[1] == 'D'
        self.muxing   = line[2] == 'E'
        self.name = line[4:]

    def __repr__(self):
        muxing = ''
        if self.demuxing: muxing += 'D'
        if self.muxing: muxing += 'E'
        return '<Format %s %s>' % (self.name, muxing)

def get_formats():
    '''get codecs for ffmpeg'''
    result = {}
    for line in _plugins_gen('-formats', sep=' --', stdpipe='stdout'):
        result[line[4:]] = Format(line)
    return result


class PixelFormat:
    '''pixel format and bit per pixels for each pixel'''
    def __init__(self, line):
        self.input  = line[0] == 'I'
        self.output = line[1] == 'O'
        self.hardware  = line[2] == 'H'
        self.paletted  = line[3] == 'P'
        self.bitstream = line[5] == 'B'
        options = [t for t in line[8:].split(' ') if t != '']
        self.name, self.components, self.bpp = options[0], int(options[1]), int(options[2])

    def __repr__(self):
        io  = 'I' if self.input else '.'
        io += 'O' if self.output else '.'
        return '<PixelFormat %s %s %d %d>' % (self.name, io, self.components, self.bpp)


def get_pixel_formats():
    '''get pix_fmts for ffmpeg'''
    result = {}
    for line in _plugins_gen('-pix_fmts', sep='-----', stdpipe='stdout'):
        pix = PixelFormat(line)
        result[pix.name] = pix
    return result



def get_ffmpeg_version():
    """get versions about ffmpeg and lib**
    
    e.g.
    FFmpeg SVN-r26400
    libavutil     50.36. 0 / 50.36. 0
    libavcore      0.16. 1 /  0.16. 1
    libavcodec    52.108. 0 / 52.108. 0
    libavformat   52.93. 0 / 52.93. 0
    libavdevice   52. 2. 3 / 52. 2. 3
    libavfilter    1.74. 0 /  1.74. 0
    libswscale     0.12. 0 /  0.12. 0
    libpostproc   51. 2. 0 / 51. 2. 0
    """
    p = get_pipe3('-version')
    result = {}
    for line in p.stdout.readlines():
        line = line.rstrip()
        idx = line.find(' ')
        name = line[:idx]
        version = line[idx:].lstrip()
        result[name] = version
    del p
    return result

def get_ffmpeg_info():
    """get infomation about ffmpeg(included versions)
    
    e.g.:
    FFmpeg version SVN-r26400, Copyright (c) 2000-2011 the FFmpeg developers
      built on Jan 17 2011 22:59:06 with gcc 4.5.2
      configuration: --enable-memalign-hack --enable-gpl --enable-version3 --enable-postproc --enable-li
    bopencore-amrnb --enable-libopencore-amrwb --enable-libgsm --enable-libmp3lame --enable-librtmp --en
    able-libvorbis --enable-libtheora --enable-libxvid --enable-libvpx --enable-libx264 --disable-ffserv
    er --disable-ffplay --disable-ffprobe --enable-avisynth --enable-small --enable-w32threads --extra-l
    dflags=-static --extra-cflags='-mtune=core2 -mfpmath=sse -msse -fno-strict-aliasing'
      libavutil     50.36. 0 / 50.36. 0
      libavcore      0.16. 1 /  0.16. 1
      libavcodec    52.108. 0 / 52.108. 0
      libavformat   52.93. 0 / 52.93. 0
      libavdevice   52. 2. 3 / 52. 2. 3
      libavfilter    1.74. 0 /  1.74. 0
      libswscale     0.12. 0 /  0.12. 0
      libpostproc   51. 2. 0 / 51. 2. 0
    Hyper fast Audio and Video encoder
    usage: ffmpeg [options] [[infile options] -i infile]... {[outfile options] outfile}...

    Use -h to get full help or, even better, run 'man ffmpeg'
    """
    p = get_pipe3()
    result = {}
    for line in p.stderr.readlines():
        if line[:6] == 'FFmpeg':
            result['FFmpeg'] = line[15:line.find(',')]
            continue
        if line[2:2+5] == 'built':
            result['built'] = line[11:].rstrip()
            continue
        if line[2:15] == 'configuration':
            result['configuration'] = line[17:].rstrip()
            continue
        if line[2:5] == 'lib':
            line = line[2:].rstrip()
            idx = line.find(' ')
            name = line[:idx]
            result[name] = line[idx:].lstrip()
            continue
    del p
    return result


def get_info(path_of_video):
    """get infomation of the video for ffmpeg

    e.g.:
    Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'your_video.mp4':
      Metadata:
        major_brand     : isom
        minor_version   : 1
        compatible_brands: isomavc1
        creation_time   : 2010-11-20 10:39:32
      Duration: 00:01:15.26, start: 0.000000, bitrate: 602 kb/s
        Stream #0.0(und): Video: h264, yuv420p, 512x384, 511 kb/s, 30 fps, 30 tbr, 30k tbn, 60 tbc
        Metadata:
          creation_time   : 2010-11-20 10:39:32
        Stream #0.1(und): Audio: aac, 48000 Hz, stereo, s16, 88 kb/s
        Metadata:
          creation_time   : 2010-11-20 10:39:32

    to

    {'duration': {'duration': '00:01:15.26', 'start': '0.000000', 'bitrate': '602 kb/s', 'streams': [{'p
    ix_fmt': 'yuv420p', 'bitrate': '511 kb/s', 'tbr': '30 tbr', 'raw': ['Video', 'h264', 'yuv420p', '512
    x384', '511 kb/s', '30 fps', '30 tbr', '30k tbn', '60 tbc'], 'codec': 'h264', 'fps': '30 fps', 'tbn'
    : '30k tbn', 'tbc': '60 tbc', 'type': 'Video', 'size': '512x384'}, {'Hz': '48000 Hz', 'ch': 'stereo'
    , 'bitrate': '88 kb/s', 'smp_fmt': 's16', 'raw': ['Audio', 'aac', '48000 Hz', 'stereo', 's16', '88 k
    b/s'], 'codec': 'aac', 'type': 'Audio'}]}, 'metadata': {'major_brand': 'isom', 'creation_time': '201
    0-11-20 10:39:32', 'compatible_brands': 'isomavc1', 'minor_version': '1'}}
    """
    result = {}
    at_metadata = True
    metadata = {}
    duration = {}
    for line in _plugins_gen(['-i', '"%s"' % path_of_video], sep='  libpostproc'):
        line = line.lstrip()
        if line[:5] == 'Input': continue
        if line == 'Metadata:': continue
        tokens = line.lstrip().split(': ')
        if at_metadata:
            if tokens[0] != 'Duration':
                metadata[tokens[0].rstrip()] = tokens[1]
                continue
            at_metadata = False
        if tokens[0] == 'Duration':
            duration['duration'] = tokens[1][:-7]
            duration['start'] = tokens[2][:-9]
            duration['bitrate'] = tokens[3]
            duration['streams'] = [] # Video.. Audio..
        if line[:6] == 'Stream':
            stream = {}
            submeta = tokens[2].split(', ')
            stream['raw'] = [tokens[1]] + submeta # ['Video', 'h264', 'yuv420p', '352x240', '486 kb/s', '30 fps', '30 tbr', '30 tbn', '60 tbc']
            stream['type'] = tokens[1] # Video
            if stream['type'] == 'Audio':
                stream['codec'] = submeta[0] # aac
                stream['Hz'] = submeta[1] # 48000 Hz
                stream['ch'] = submeta[2] # stereo
                stream['smp_fmt'] = submeta[3] # s16
                stream['bitrate'] = submeta[4] # 88 kb/s
            else:
                stream['codec'] = submeta[0] # h264
                stream['pix_fmt'] = submeta[1] # yuv420p
                stream['size'] = submeta[2] # 352x240
                stream['bitrate'] = submeta[3] # 486 kb/s
                stream['fps'] = submeta[4] # 30 fps
                stream['tbr'] = submeta[5] # 30 tbr
                stream['tbn'] = submeta[6] # 30 tbn
                stream['tbc'] = submeta[7] # 60 tbc
            duration['streams'].append(stream)

    return dict(metadata=metadata, duration=duration)



if __name__ == '__main__':
    print 'version:', get_ffmpeg_version()
    print 'info:', get_ffmpeg_info()
    print 'codecs:', get_codecs()
    print 'formats:', get_formats()
    print 'pix_fmts:', get_pixel_formats()
    print 'info of video:', get_info('test.mp4')
