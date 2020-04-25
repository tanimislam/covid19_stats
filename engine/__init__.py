import os, sys
from functools import reduce

mainDir = reduce(lambda x,y: os.path.dirname( x ), range( 2 ),
                 os.path.abspath( __file__ ) )
sys.path.append( mainDir )

#
## secret sauce formatting comma'd integers from https://intellipaat.com/community/2447/how-to-print-number-with-commas-as-thousands-separators
def get_string_commas_num( num ):
  return "%s" % f"{num:,d}"
