# -*- coding: utf-8 -*-
import os
from distutils.core import setup

version='0.1.1'
README = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(README).read() + '\n\n'

setup(
    name='pipeffmpeg',
    version=version,
    description=('A frontend for ffmpeg(libav) using only pipes, to encode/decode/convert videos by each frame'),
    long_description=long_description,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Video',
    ],
    keywords='video ffmpeg convert libav encode decode transcode',
    author='KATO Kanryu',
    author_email='k.kanryu@gmail.com',
#    url='http://knivez.homelinux.org/pipeffmpeg/',
    url='https://github.com/kanryu/pipeffmpeg',
    license='BSD',
    py_modules=['pipeffmpeg'],
    package_data={'pipeffmpeg': ['test.mp4']},
    data_files=[('', ['test.mp4'])], # only distfile, not to be installed
)
