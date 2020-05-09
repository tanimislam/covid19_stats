#!/usr/bin/env python

import os, sys, subprocess
from distutils.spawn import find_executable

maxnum_dict = {
  'batonrouge' : 5000,
  'bayarea' : 5000,
  'chicago' : 50000,
  'dc' : 5000,
  'losangeles' : 50000,
  'neworleans' : 10000,
  'richmond' : 1000,
  'seattle' : 20000,
  'nyc' : 200000 }

for metro, maxnum in maxnum_dict.items( ):
  proc = subprocess.Popen([ '../covid19_create_movie_or_summary.py', 'm', '-n', metro, '-M', '%d' % maxnum, '-y' ],
                          stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
  stdout_val, stderr_val = proc.communicate( )

