__author__ = 'Tanim Islam'
__email__ = 'tanim.islam@gmail.com'

import sys, os

_mainDir = os.path.dirname( os.path.abspath( __file__ ) )
#
## resources directory and covid-19 git submodule 
resourceDir = os.path.join( _mainDir, 'resources' )
covid19ResDir = os.path.join( _mainDir, 'covid-19-data' )
#
## must both exist
assert(all(map( dirname,  os.path.isdir( dirname ), ( resourceDir, covid19ResDir ) ) ) )
