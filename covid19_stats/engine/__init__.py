import os, sys, numpy

#
## secret sauce formatting comma'd integers from https://intellipaat.com/community/2447/how-to-print-number-with-commas-as-thousands-separators
def get_string_commas_num( num ):
    return "%s" % f"{num:,d}"

def find_plausible_maxnum( maxcases ):
    if maxcases <= 75: return 100
    pow_exp = int( numpy.log10( maxcases ) )
    scl = maxcases / 10**pow_exp
    #
    ## spit out 1.7 * 10**pow_exp
    if scl <= 4.0/3: return int( 1.7 * 10**pow_exp )
    #
    ## spit out 3.2 * 10**pow_exp
    if scl <= 1.7 * 4.0 / 3: return int( 3.2 * 10**pow_exp )
    #
    ## spit out 5.6 * 10**pow_exp
    if scl <= 3.2 * 4.0 / 3: return int( 5.6 * 10**pow_exp )
    #
    ## spit out 10**(pow_exp + 1)
    if scl <= 7.5: return int( 10**(pow_exp + 1) )
    #
    ## otherwise, return 2 * 10**(pow_exp + 1 )
    return int( 1.7 * 10**( pow_exp + 1 ) )
