import os, sys, logging, time, git
from covid19_stats import covid19ResDir
from argparse import ArgumentParser

def main( ):
    time0 = time.perf_counter( )
    #
    parser = ArgumentParser( description = 'Run this to update the NY TIMES COVID 19 DATABASE.' )
    parser.add_argument( '--info', dest='do_info', action='store_true', default = False,
                        help = 'If chosen, run with INFO logging.' )
    args = parser.parse_args( )
    logger = logging.getLogger( )
    if args.do_info: logger.setLevel( logging.INFO )
    assert( os.path.isdir( covid19ResDir ) )
    logging.info( 'COVID 19 DATABASE = %s.' % covid19ResDir )
    repo_nytimes = git.Repo( covid19ResDir )
    f = repo_nytimes.remote( ).pull( 'master' )
    print( 'took %0.3f seconds to update COVID 19 DATABASE.' % (
        time.perf_counter( ) - time0 ) )
