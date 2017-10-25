PipeFFmpeg
===========

A frontend for ffmpeg(libav) using only pipes,
to encode/decode/convert videos by each frame,
not under GPL, but under BSD license.

Features:

 - To get ffmpeg's infomation (versions,codecs,formats,pix_fmts,...) 
 - To decode frames from a video 
 - To encode a video within posting frames in Python

You can install and test pipeffmpeg as follows:

 1. download ffmpeg(libav) binary or source and build that
    (not necessary as shared-library).
 2. set bin/ffmpeg or ffmpeg.exe(under Windows) into PATH environment
 3. download pipeffmpeg.py into your current directory or site-packages

pipeffmpeg (currently version 0.1.1) is also available at PyPI

> pip install pipeffmpeg

Please report issues as well as configuration details for your working 
PipeFFmpeg installations at <k.kanryu@gmail.com>

Thus, your feedback is welcome at <k.kanryu@gmail.com>.

