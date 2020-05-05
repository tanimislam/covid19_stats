import os, sys
from functools import reduce

mainDir = reduce(lambda x,y: os.path.dirname( x ), range( 2 ),
                 os.path.abspath( __file__ ) )
sys.path.append( mainDir )

#
## secret sauce formatting comma'd integers from https://intellipaat.com/community/2447/how-to-print-number-with-commas-as-thousands-separators
def get_string_commas_num( num ):
    return "%s" % f"{num:,d}"

def find_plausible_maxnum( maxcases ):
    if maxcases <= 75: return 100
    pow_exp = int( numpy.log10( maxcases ) )
    scl = maxcases / 10**pow_exp
    #
    ## spit out 2 * 10**pow_exp
    if scl <= 1.5: return int( 2 * 10**pow_exp )
    #
    ## spit out 5 * 10**pow_exp
    if scl <= 15.0/4: return int( 5 * 10**pow_exp )
    #
    ## spit out 10**(pow_exp + 1 )
    if scl <= 7.5: return int( 10**( pow_exp + 1 ) )
    #
    ## otherwise, return 2 * 10**(pow_exp + 1 )
    return int( 2 * 10**( pow_exp + 1 ) )
