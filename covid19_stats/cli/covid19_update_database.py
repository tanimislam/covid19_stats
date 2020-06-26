import os, sys, logging, subprocess, time
from covid19_stats import covid19ResDir
from distutils.spawn import find_executable
from argparse import ArgumentParser

def main( ):
    time0 = time.time( )
    #
    parser = ArgumentParser( description = 'Run this to update the NY TIMES COVID 19 DATABASE.' )
    parser.add_argument( '--info', dest='do_info', action='store_true', default = False,
                        help = 'If chosen, run with INFO logging.' )
    args = parser.parse_args( )
    logger = logging.getLogger( )
    if args.do_info: logger.setLevel( logging.INFO )
    #
    git_exec = find_executable( 'git' )
    assert( git_exec is not None )
    assert( os.path.isdir( covid19ResDir ) )
    logging.info( 'GIT EXEC = %s.' % git_exec )
    logging.info( 'COVID 19 DATABASE = %s.' % covid19ResDir )
    proc = subprocess.Popen([ git_exec, '-C', covid19ResDir, 'pull', 'origin', 'master' ],
                            stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    stdout_val, stderr_val = proc.communicate( )
    print( 'took %0.3f seconds to update COVID 19 DATABASE.' % (
        time.time( ) - time0 ) )
