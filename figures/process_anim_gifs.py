#!/usr/bin/env python3

import os, sys, glob, datetime, shutil

metros_2_exclude = ( 'nyc', 'chicago', 'seattle' )

def _get_metro_date( giffile ):
  if os.path.islink( giffile ): return None
  try:
    dstring = os.path.basename( giffile ).split('.')[0].strip( )
    metro = dstring.split('_')[1].strip( )
    dstring = dstring.split('_')[-1].strip( )
    mydate = datetime.datetime.strptime(
      dstring, '%d%m%Y' ).date( )
    return ( metro, giffile, mydate )
  except: return None

#
## first remove all symbolic links
list(map(os.remove, filter(os.path.islink, glob.glob('*.gif'))))

#
## now check for dictionary of files
dict_giffiles = { }
for dat in filter(None, map(_get_metro_date, glob.glob('*.gif'))):
  metro, giffile, mydate = dat
  dict_giffiles.setdefault( metro, [] ).append(
    { 'giffile' : giffile, 'date' : mydate })

#
## look for GIF data that has two or more dates per metro
for metro in filter(lambda metro: len( dict_giffiles[ metro ] ) > 1, dict_giffiles ):
  #
  ## find files to remove, then remove them
  giffiles_2_remove = sorted(
    dict_giffiles[ metro ],
    key = lambda entry: entry[ 'date' ] )[:-1]
  list(map(os.remove, map(lambda entry: entry['giffile'], giffiles_2_remove)))

#
## now make symbolic links of them EXCEPT FOR (nyc, chicago,seattle)
for metro in set( dict_giffiles ) - set( metros_2_exclude ):
  linkname = 'covid19_%s_latest.gif' % metro
  giffile = max(dict_giffiles[ metro ])[ 'giffile' ]
  os.symlink( giffile, linkname )
#
## now do copy of nyc, chicago, seattle
for metro in set( dict_giffiles ) & set( metros_2_exclude ):
  filename = 'covid19_%s_latest.gif' % metro
  giffile = max(dict_giffiles[ metro ])[ 'giffile' ]
  shutil.copy( giffile, filename )
