import os, sys, numpy, logging, time, warnings, json
from pathos.multiprocessing import Pool, ThreadPool, cpu_count
from mpi4py import MPI
from itertools import product
from argparse import ArgumentParser
#
from covid19_stats.engine import core, viz, find_plausible_maxnum
from covid19_stats import COVID19Database

warnings.filterwarnings("ignore") # suppress all warnings

"""
This constructs a lot of different *MOVIES* that construct the following movies and figures. This follows the functionality of ``covid19_create_movie_or_summary``: (m) create a movie for a metropolitan statistical area (MS) of continental US (CONUS); (s) make a summary plot, and incident data file, for a specific MSA or CONUS; (mcd) --cases, make a large-sized movie of CASES for an MSA or CONUS; and (mcd) --deaths, make a large-sized movie of DEATHS for an MSA or CONUS.

Just lift functionality of the separate parts from the PYTHON file, ``covid19_create_movie_or_summary.py``
"""

def _get_data_state_or_territory( statename ):
    mapping_state_rname_conus = COVID19Database.mapping_state_rname_conus( )
    mapping_state_rname_nonconus = COVID19Database.mapping_state_rname_nonconus( )
    data_states = COVID19Database.data_states( )
    data_nonconus_states_territories = COVID19Database.data_nonconus_states_territories( )
    if statename in mapping_state_rname_conus:
        data_state = data_states[
            mapping_state_rname_conus[ statename ] ]
        inc_data = core.get_incident_data( data_state )
        return inc_data, _get_maxnum( inc_data )
    if statename in mapping_state_rname_nonconus:
        data_state = data_nonconus_states_territories[
            mapping_state_rname_nonconus[ statename ] ]
        inc_data = core.get_incident_data( data_state )
        return inc_data, _get_maxnum( inc_data )
    raise ValueError("Error, the chosen state or territory, %s, not in one of the %d defined." % (
        statename, len( mapping_state_rname_conus ) + len( mapping_state_rname_nonconus ) ) )

def _summarize_state_or_territory( statename, dirname, time0 ):
    assert( os.path.isdir( dirname ) )
    inc_data, maxnum = _get_data_state_or_territory( statename )
    viz.get_summary_demo_data(
        inc_data, maxnum_colorbar = maxnum,
        dirname = dirname, store_data = False )
    logging.info( 'at %0.3f seconds to create summary of %s.' % (
        time.time( ) - time0, statename ) )

def _movie_state_or_territory( statename, dirname, time0 ):
    assert( os.path.isdir( dirname ) )
    inc_data, maxnum = _get_data_state_or_territory( statename )
    movie_name = viz.create_summary_movie_frombeginning(
        inc_data, maxnum_colorbar = maxnum,
        dirname = dirname )
    logging.info( 'at %0.3f seconds to create movie of %s.' % (
        time.time( ) - time0, statename ) )

def _movie_casedeaths_state_or_territory( statename, dirname, time0, type_disp = 'cases' ):
    assert( os.path.isdir( dirname ) )
    assert( type_disp.lower( ) in ( 'cases', 'deaths' ) )
    inc_data, maxnum = _get_data_state_or_territory( statename )
    viz.create_summary_cases_or_deaths_movie_frombeginning(
        inc_data, maxnum_colorbar = maxnum,
        type_disp = type_disp.lower( ), dirname = dirname,
        save_imgfiles = False )
    logging.info( 'at %0.3f seconds to create %s movie of %s.' % (
        time.time( ) - time0, type_disp.upper( ), statename ) )

def _get_data( msa_or_conus_name ):
    if msa_or_conus_name.lower( ) == 'conus':
        data_conus = COVID19Database.data_conus( )
        inc_data = core.get_incident_data( data_conus )
        return inc_data, _get_maxnum( inc_data )
    if msa_or_conus_name.lower( ) in COVID19Database.data_msas_2019( ):
        data_msas_2019 = COVID19Database.data_msas_2019( )
        inc_data = core.get_incident_data( data_msas_2019[ msa_or_conus_name.lower( ) ] )
        return inc_data, _get_maxnum( inc_data )
    raise ValueError("Error, the chosen MSA name %s not one of the %d defined." % (
        msa_or_conus_name.lower( ), len( COVID19Database.data_msas_2019( ) ) ) )

def _get_maxnum( inc_data ):
    max_cases = core.get_max_cases_county( inc_data )[ 'cases' ]
    maxnum = find_plausible_maxnum( max_cases )
    return maxnum

def _summarize_metro_or_conus( msa_or_conus_name, dirname, time0 ):
    assert( os.path.isdir( dirname ) )
    inc_data, maxnum = _get_data( msa_or_conus_name )
    viz.get_summary_demo_data( inc_data, maxnum_colorbar = maxnum, dirname = dirname, store_data = False )
    logging.info( 'at %0.3f seconds to create summary of %s.' % (
        time.time( ) - time0, msa_or_conus_name.lower( ) ) )

def _summarize( msas_or_conus, dirname, time0 ):
    all_msas = set(map(lambda msa_or_conus: msa_or_conus.lower( ), msas_or_conus))
    with ThreadPool(processes = min(8, cpu_count( ), len( all_msas ) ) ) as pool:
        _ = list(pool.map(lambda msa_or_conus: _summarize_metro_or_conus(
            msa_or_conus, dirname, time0 ), all_msas ) )
    logging.info( 'at %0.3f seconds to create all %d summaries.' % (
        time.time( ) - time0, len( all_msas ) ) )

def _movie_metro_or_conus( msa_or_conus_name, dirname, time0 ):
    assert( os.path.isdir( dirname ) )
    inc_data, maxnum = _get_data( msa_or_conus_name )
    movie_name = viz.create_summary_movie_frombeginning(
        inc_data, maxnum_colorbar = maxnum,
        dirname = dirname )
    logging.info( 'at %0.3f seconds to create movie of %s.' % (
        time.time( ) - time0, msa_or_conus_name.lower( ) ) )

def _movie( msas_or_conus, dirname, time0 ):
    all_msas = set(map(lambda msa_or_conus: msa_or_conus.lower( ), msas_or_conus))
    with ThreadPool(processes = min(8, cpu_count( ), len( all_msas ) ) ) as pool:
        _ = list(pool.map(lambda msa_or_conus: _movie_metro_or_conus(
            msa_or_conus, dirname, time0 ), all_msas ) )
    logging.info( 'at %0.3f seconds to create all %d movies.' % (
        time.time( ) - time0, len( all_msas ) ) )

def _movie_casedeaths_metro_or_conus( msa_or_conus_name, dirname, time0, type_disp = 'cases' ):
    assert( os.path.isdir( dirname ) )
    assert( type_disp.lower( ) in ( 'cases', 'deaths' ) )
    inc_data, maxnum = _get_data( msa_or_conus_name )
    viz.create_summary_cases_or_deaths_movie_frombeginning(
        inc_data, maxnum_colorbar = maxnum,
        type_disp = type_disp.lower( ), dirname = dirname,
        save_imgfiles = False )
    logging.info( 'at %0.3f seconds to create %s movie of %s.' % (
        time.time( ) - time0, type_disp.upper( ), msa_or_conus_name.lower( ) ) )

def _movie_casedeaths( msas_or_conus, dirname, time0, type_disp = 'cases' ):
    all_msas = set(map(lambda msa_or_conus: msa_or_conus.lower( ), msas_or_conus))
    with ThreadPool(processes = min(8, cpu_count( ), len( all_msas ) ) ) as pool:
        _ = list(pool.map(lambda msa_or_conus: _movie_casedeaths_metro_or_conus(
            msa_or_conus, dirname, time0, type_disp = type_disp ), all_msas ) )
    logging.info( 'at %0.3f seconds to create all %d movies of %s.' % (
        time.time( ) - time0, len( all_msas ), type_disp.upper( ) ) )

def _get_min_time0( ):
    time0_arr = numpy.array([ time.time( ) ])
    time0_min = time0_arr.copy( )
    MPI.COMM_WORLD.Allreduce( time0_arr, time0_min, MPI.MIN )
    return time0_min[ 0 ]

def _draw_out_topN( dirname, topN ):
    assert( topN > 0 )
    data_msas_2019 = COVID19Database.data_msas_2019( )
    metros = list(map(lambda entry: entry['prefix'], sorted(
        data_msas_2019.values( ),
        key = lambda entry: entry['population'])[::-1][:topN]))
    json_data = core.display_tabulated_metros(
        form = 'json', selected_metros = metros )
    json.dump( json_data, open( os.path.join( dirname, 'covid19_topN_LATEST.json' ), 'w' ),
              indent = 1 )
    
def main( ):
    rank = MPI.COMM_WORLD.Get_rank( )
    time0 = _get_min_time0( )
    parser = ArgumentParser( )
    parser.add_argument( '--region', metavar='region', type=str, nargs='*',
                        help = 'regions to choose to create summary plots, big movies, and smaller movies.' )
    parser.add_argument( '--state', metavar='state', type=str, nargs='*',
                        help = 'states to choose to create summary plots, big movies, and smaller movies.' )
    parser.add_argument( '--dirname', dest='dirname', type=str, action='store', default = os.getcwd( ),
                        help = 'The name of the directory to which to put all this stuff. Default is %s.' % os.getcwd( ) )
    parser.add_argument( '--topN', dest='topN', type=int, action='store', default = 50,
                        help = 'Print out JSON formatted COVID-19 summary data for the topN US MSAs. Default is 50.' )
    parser.add_argument( '--info', dest='do_info', action='store_true', default = False,
                        help = 'If chosen, then turn on INFO logging.' )
    args = parser.parse_args( )
    assert( os.path.isdir( args.dirname ) )
    assert( args.topN > 0 )
    #
    ## the msas or conus, and states or territories
    msas_or_conus = sorted(set(map(lambda msa_or_conus: msa_or_conus.strip( ).lower( ), args.region ) ) )
    states_or_territories = sorted(set(args.state))
    ntasks = 4 * ( len( msas_or_conus ) + len( states_or_territories ) )
    nprocs = min( MPI.COMM_WORLD.Get_size( ), ntasks )
    if rank >= ntasks: return
    #
    ## check on whether to turn on INFO logging
    logger = logging.getLogger( )
    if args.do_info: logger.setLevel( logging.INFO )
    #
    ## if rank == 0, write out the topN COVID-19 summary data
    if rank == 0: _draw_out_topN( args.dirname, args.topN )
    #
    ## now do the thing...
    all_tuples_to_process = list(product(range(4), [ 0, ], msas_or_conus)) + list(
        product(range(4), [ 1, ], states_or_territories ) )
    tuples_to_process = all_tuples_to_process[rank::nprocs]
    for thing_to_do, region_type, region in tuples_to_process:
        if region_type == 0: # do msas or conus
            msa_or_conus = region
            if thing_to_do == 0:
                _summarize_metro_or_conus( msa_or_conus, args.dirname, time0 )
            elif thing_to_do == 1:
                _movie_metro_or_conus( msa_or_conus, args.dirname, time0 )
            elif thing_to_do == 2:
                _movie_casedeaths_metro_or_conus( msa_or_conus, args.dirname, time0, type_disp = 'cases' )
            elif thing_to_do == 3:
                _movie_casedeaths_metro_or_conus( msa_or_conus, args.dirname, time0, type_disp = 'deaths' )
        else: # do states
            state = region
            if thing_to_do == 0:
                _summarize_state_or_territory( state, args.dirname, time0 )
            elif thing_to_do == 1:
                _movie_state_or_territory( state, args.dirname, time0 )
            elif thing_to_do == 2:
                _movie_casedeaths_state_or_territory( state, args.dirname, time0, type_disp = 'cases' )
            elif thing_to_do == 3:
                _movie_casedeaths_state_or_territory( state, args.dirname, time0, type_disp = 'deaths' )

    MPI.COMM_WORLD.Barrier( )

    if rank != 0: return
    logging.info( 'processed all FOUR operations on %d regions or states in %0.3f seconds.' % (
        len( msas_or_conus ) + len( states_or_territories ), time.time( ) - time0 ) )
