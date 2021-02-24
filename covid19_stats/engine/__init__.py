import os, sys, numpy

def get_string_commas_num( num ):
    """
    This is the secret-sauce of formatting integers as strings with commas for every 3 digits. For example, ``1234`` becomes "1,234". I copied code from `this location`_.

    :param int num: input number.
    :returns: the nicely formatted output :py:class:`string <str>` representing an input number.
    :type: str

    .. _`this location`: https://intellipaat.com/community/2447/how-to-print-number-with-commas-as-thousands-separators
    """
    return "%s" % f"{num:,d}"

def find_plausible_maxnum( maxnum ):
    """
    Returns a default plausible limit, for the plotting of COVID-19 cumulative cases and deaths located in :py:mod:`viz <covid19_stats.engine.viz>`.

    :param int maxnum: the maximum number.
    :returns: a new :py:class:`integer <int>` larger than ``maxnum``, that provides a visually aesthetic upper limit for plotting.
    :rtype: int
    """
    if maxnum <= 75: return 100
    pow_exp = int( numpy.log10( maxnum ) )
    scl = maxnum / 10**pow_exp
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
