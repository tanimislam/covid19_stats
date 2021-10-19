import os, sys, numpy, logging, time, warnings, json
from pathos.multiprocessing import cpu_count
from mpi4py import MPI
from itertools import product
from argparse import ArgumentParser
#
from covid19_stats.engine import core, viz, viz2
from covid19_stats import COVID19Database

os.environ[ 'NUMEXPR_MAX_THREADS' ] = '%d' % ( max(1, divmod( cpu_count( ), 2 )[0] ) )

warnings.filterwarnings("ignore") # suppress all warnings

"""
This constructs a lot of different *MOVIES* that construct the following movies and figures. This follows the functionality of ``covid19_create_movie_or_summary``: (m) create a movie for a metropolitan statistical area (MS) of continental US (CONUS); (s) make a summary plot, and incident data file, for a specific MSA or CONUS; (mcd) --cases, make a large-sized movie of CASES for an MSA or CONUS; and (mcd) --deaths, make a large-sized movie of DEATHS for an MSA or CONUS.

Just lift functionality of the separate parts from the PYTHON file, ``covid19_movie_updates``.
"""

def _summarize( inc_data, dirname, time0 ):
    assert( os.path.isdir( dirname ) )
    viz.get_summary_demo_data(
        inc_data, dirname = dirname, store_data = False )
    viz2.get_summary_demo_rate_data( inc_data, dirname = dirname, store_data = False )
    logging.info( 'at %0.3f seconds to create summary of %s.' % (
        time.time( ) - time0, inc_data[ 'prefix' ] ) )

def _movie( inc_data, dirname, time0 ):
    assert( os.path.isdir( dirname ) )
    movie_name = viz.create_summary_movie_frombeginning(
        inc_data, dirname = dirname )
    movie_7day_name = viz2.create_summary_rate_movie_frombeginning(
        inc_data, dirname = dirname )
    logging.info( 'at %0.3f seconds to create movie of %s.' % (
        time.time( ) - time0, inc_data[ 'prefix' ] ) )

def _movie_casedeaths( inc_data, dirname, time0, type_disp = 'cases' ):
    assert( os.path.isdir( dirname ) )
    assert( type_disp.lower( ) in ( 'cases', 'deaths' ) )
    viz.create_summary_cases_or_deaths_movie_frombeginning(
        inc_data, type_disp = type_disp.lower( ), dirname = dirname,
        save_imgfiles = False )
    viz2.create_summary_cases_or_deaths_rate_movie_frombeginning(
        inc_data, dirname = dirname, type_disp = type_disp.lower( ),
        save_imgfiles = False )
    logging.info( 'at %0.3f seconds to create %s movie of %s.' % (
        time.time( ) - time0, type_disp.upper( ), inc_data[ 'prefix' ] ) )

def _get_min_time0( ):
    time0_arr = numpy.array([ time.time( ) ])
    time0_min = time0_arr.copy( )
    MPI.COMM_WORLD.Allreduce( time0_arr, time0_min, MPI.MIN )
    return time0_min[ 0 ]

def _get_region_data( region_filename ):
    data = json.load( open( region_filename, 'r' ) )
    return {
        'prefix' : data[ 'prefix' ],
        'region name' : data[ 'region name' ],
        'fips' : set( data[ 'fips' ] ),
        'population' : data[ 'population' ] }
    
def main( ):
    rank = MPI.COMM_WORLD.Get_rank( )
    time0 = _get_min_time0( )
    parser = ArgumentParser( )
    parser.add_argument( '-r', '--region', metavar='region', type=str, required = True,
                        help = 'region as JSON file.' )
    parser.add_argument( '-d', '--dirname', dest='dirname', type=str, action='store', default = os.getcwd( ),
                        help = 'The name of the directory to which to put all this stuff. Default is %s.' % os.getcwd( ) )
    parser.add_argument( '-i', '--info', dest='do_info', action='store_true', default = False,
                        help = 'If chosen, then turn on INFO logging.' )
    args = parser.parse_args( )
    assert( os.path.isdir( args.dirname ) )
    assert( os.path.isfile( os.path.expanduser( args.region ) ) )
    assert( os.path.basename( os.path.expanduser( args.region ) ).endswith('.json' ) )
    #
    ## I do four things
    ntasks = 4
    nprocs = min( MPI.COMM_WORLD.Get_size( ), ntasks )
    if rank >= ntasks: return
    #
    ## check on whether to turn on INFO logging
    logger = logging.getLogger( )
    if args.do_info: logger.setLevel( logging.INFO )
    #
    ## get incident data for the region
    region_filename = os.path.abspath( os.path.expanduser( args.region ) )
    region_data = _get_region_data( region_filename )
    inc_data = core.get_incident_data( region_data )
    #
    ## now do the thing...
    all_tuples_to_process = list(range(4))
    tuples_to_process = all_tuples_to_process[rank::nprocs]
    for thing_to_do in tuples_to_process:
        if thing_to_do == 0: _summarize( inc_data, args.dirname, time0 )
        elif thing_to_do == 1: _movie( inc_data, args.dirname, time0 )
        elif thing_to_do == 2: _movie_casedeaths( inc_data, args.dirname, time0, type_disp = 'cases' )
        elif thing_to_do == 3: _movie_casedeaths( inc_data, args.dirname, time0, type_disp = 'deaths' )
    MPI.COMM_WORLD.Barrier( )

    if rank != 0: return
    logging.info( 'processed all FOUR operations on %s (%s) in %0.3f seconds.' % (
        inc_data[ 'prefix' ], inc_data[ 'region name'], time.time( ) - time0 ) )
