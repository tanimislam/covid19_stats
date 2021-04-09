import sys, signal
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )
signal.signal( signal.SIGINT, signal_handler )
import os, numpy, tempfile, warnings, tabulate, logging, json
from covid19_stats import COVID19Database
from covid19_stats.engine.core import create_readme_from_template
from argparse import ArgumentParser

#
## suppress warnings
warnings.simplefilter( 'ignore' )

_default_covid19_url = 'https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies'
#_default_covid19_url = 'https://tanimislam.gitlab.com/covid19movies'

def main( ):
    parser = ArgumentParser( )
    parser.add_argument(
        '-m', '--mainurl', dest='mainurl', type=str, action='store',
        default = _default_covid19_url,
        help = 'Name of the URL where the COVID-19 summary data lives. Default is %s.' % _default_covid19_url )
    parser.add_argument(
        '-d', '--dirname', dest='dirname', type=str, action='store', default = os.getcwd( ),
        help = 'Directory in which the README.rst lives, for the covid19_stats repository. Default is %s.' % os.getcwd( ) )
    parser.add_argument(
        '-j', '--json', dest='json', type=str, action='store',
        help = 'Optional argument. If defined give the JSON file that contains the summary COVID-19 cases and deaths information of the top N MSAs.' )
    parser.add_argument(
        '--noverify', dest='do_verify', action = 'store_false', default = True,
        help = 'If chosen, then do not verify necessary SSL connections.' )
    
    args = parser.parse_args( )
    assert( os.path.isdir( os.path.expanduser( args.dirname ) ) )
    #
    ## now run the thing
    create_readme_from_template(
        mainURL = args.mainurl, 
        dirname_for_readme_location = os.path.expanduser( args.dirname ),
        verify = args.do_verify, topN_json = args.json )
