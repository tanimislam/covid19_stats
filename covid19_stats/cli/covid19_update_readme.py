import sys, signal
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )
signal.signal( signal.SIGINT, signal_handler )
import os, numpy, tempfile, warnings, tabulate, logging, json
from covid19_stats import COVID19Database
from covid19_stats.engine import create_readme_from_template
from argparse import ArgumentParser

_default_covid19_url = 'https://tanimislam.github.io/covid19movies'

def main( ):
    parser = ArgumentParser( )
    parser.add_argument(
        '-m', '--mainurl', dest='mainurl', type=str, action='store',
        default = _default_covid19_url,
        help = 'Name of the URL where the COVID-19 summary data lives. Default is %s.' % _default_covid19_url )
    parser.add_argument(
        '-d', '--dirname', dest='dirname', type=str, action='store', required = True,
        help = 'Directory in which the README.rst lives, for the covid19_stats repository.' )
    parser.add_argument(
        '--noverify', dest='do_verify', action = 'store_false', default = True,
        help = 'If chosen, then do not verify necessary SSL connections.' )
    
    args = parser.parse_args( )
    assert( os.path.isdir( args.dirname ) )
    #
    ## now run the thing
    create_readme_from_template(
        mainURL = args.mainurl, 
        dirname_for_readme_location = args.dirname,
        verify = args.do_verify )
