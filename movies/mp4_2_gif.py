#!/usr/bin/env python3

"""
Voodoo magic levels of FFMPEG tribal knowledge required.
Don't ask me how most of it works, just be on-your-knees-kissing-the-dirt grateful that MILLIONS of people hack onto and into FFMPEG so that this information is available, and the workflow works.

Resources.

1. MOVIE 2 GIF: http://blog.pkh.me/p/21-high-quality-gif-with-ffmpeg.html
2. ffprobe movie info 2 JSON: https://tanimislamblog.wordpress.com/2018/09/12/ffprobe-to-get-output-in-json-format/
"""

import os, sys, subprocess, numpy, uuid, json
from distutils.spawn import find_executable
from argparse import ArgumentParser

ffmpeg_exec = find_executable( 'ffmpeg' )
ffprobe_exec = find_executable( 'ffprobe' )
assert(all(map(lambda tok: tok is not None, ( ffmpeg_exec, ffprobe_exec ))))

parser = ArgumentParser( )
parser.add_argument( '--mp4', dest='mp4file', type=str, action='store', required = True,
                     help = 'Name of an MP4 file in this directory.' )
args = parser.parse_args( )
assert( os.path.isfile( args.mp4file ) )
assert( os.path.basename( args.mp4file ).endswith( '.mp4' ) )
#
## GIF output and PALETTE file
giffile = args.mp4file.replace('.mp4', '.gif' )
palettefile = '%s.png' % str( uuid.uuid4( ) )
#
## get info JSON to get width, fps
proc = subprocess.Popen(
  [ ffprobe_exec, '-v', 'quiet', '-show_streams',
    '-show_format', '-print_format', 'json', args.mp4file ],
  stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
stdout_val, stderr_val = proc.communicate( )
mp4file_info = json.loads( stdout_val )
# from dictionary, get width
width_of_mp4 = int( mp4file_info[ 'streams' ][ 0 ][ 'width' ] )
fps_string = mp4file_info[ 'streams' ][ 0 ][ 'avg_frame_rate' ]
fps = int( float( fps_string.split('/')[0] ) * 1.0 /
           float( fps_string.split('/')[1] ) )
#
## now do the voodoo magic from resource #1
## step #1: create palette, run at fps
cmd = [
  ffmpeg_exec, '-y', '-v', 'warning', '-i', args.mp4file,
  '-vf', 'fps=%d,scale=%d:-1:flags=lanczos,palettegen' % ( fps, width_of_mp4 ),
  palettefile ]
proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
stdout_val, stderr_val = proc.communicate( )
assert( os.path.isfile( palettefile ) )
#
## step #2: take palette file, MP4 file, create animated GIF
cmd = [
  ffmpeg_exec, '-y', '-v', 'warning', '-i', args.mp4file,
  '-i', palettefile, '-lavfi', 'fps=%d,scale=%d:-1:flags=lanczos[x];[x][1:v]paletteuse' % (
    fps, width_of_mp4 ), giffile ]
proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
stdout_val, stderr_val = proc.communicate( )
#
## now batting cleanup
try: os.remove( palettefile )
except: pass
