import sys, signal
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )
signal.signal( signal.SIGINT, signal_handler )
import os, numpy, warnings, logging, time
from argparse import ArgumentParser
#
from covid19_stats.engine import core, viz2
from covid19_stats import COVID19Database

#
## suppress warnings
warnings.simplefilter( 'ignore' )

def _get_state_names( ):
    mapping_state_rname_conus = list( COVID19Database.mapping_state_rname_conus( ).keys( ) )
    mapping_state_rname_nonconus = list( COVID19Database.mapping_state_rname_nonconus( ).keys( ) )
    return sorted( set( mapping_state_rname_conus + mapping_state_rname_nonconus ) )

def _get_msa_names( ):
    return sorted( COVID19Database.data_msas_2019( ) )

def _get_inc_data_msa_or_conus( msa_or_conus_name ):
    if msa_or_conus_name.lower( ) == 'conus':
        data = COVID19Database.data_conus( )
        return core.get_incident_data( data )
    if msa_or_conus_name.lower( ) in COVID19Database.data_msas_2019( ):
        data = COVID19Database.data_msas_2019( )[ msa_or_conus_name.lower( ) ]
        return core.get_incident_data( data )
    raise ValueError("Error, the chosen MSA name %s not one of the %d defined, or you have not chosen 'conus'." % (
        msa_or_conus_name.lower( ), len( COVID19Database.data_msas_2019( ) ) ) )

def _get_inc_data_state( statename ):
    mapping_state_rname_conus = COVID19Database.mapping_state_rname_conus( )
    mapping_state_rname_nonconus = COVID19Database.mapping_state_rname_nonconus( )
    data_states = COVID19Database.data_states( )
    data_nonconus_states_territories = COVID19Database.data_nonconus_states_territories( )
    if statename in mapping_state_rname_conus:
        data_state = data_states[ mapping_state_rname_conus[ statename ] ]
        return core.get_incident_data( data_state )
    if statename in mapping_state_rname_nonconus:
        data_state = data_nonconus_states_territories[
            mapping_state_rname_nonconus[ statename ] ]
        return core.get_incident_data( data_state )
    raise ValueError("Error, the chosen state or territory, %s, not in one of the %d defined." % (
        statename, len( mapping_state_rname_conus ) + len( mapping_state_rname_nonconus ) ) )

def _summarize_inc_data_rate( inc_data, dirname, time0 ):
    assert( os.path.isdir( dirname ) )
    viz2.get_summary_demo_rate_data( inc_data, dirname = dirname, store_data = False )
    logging.info( 'at %0.3f seconds to create summary of %s.' % (
        time.time( ) - time0, inc_data[ 'prefix' ] ) )

def _movie_inc_data_rate( inc_data, dirname, time0, save_imgfiles = False ):
    assert( os.path.isdir( dirname ) )
    viz2.create_summary_rate_movie_frombeginning(
        inc_data, dirname = dirname, save_imgfiles = save_imgfiles )
    logging.info( 'at %0.3f seconds to create movie of %s.' % (
        time.time( ) - time0, inc_data[ 'prefix' ] ) )

def _movie_casedeaths_inc_data_rate(
    inc_data, dirname, time0, type_disp = 'cases',
    save_imgfiles = False ):
    assert( os.path.isdir( dirname ) )
    assert( type_disp.lower( ) in ( 'cases', 'deaths' ) )
    viz2.create_summary_cases_or_deaths_rate_movie_frombeginning(
        inc_data, dirname = dirname, type_disp = type_disp,
        save_imgfiles = save_imgfiles )
    logging.info( 'at %0.3f seconds to create %s movie of %s.' % (
        time.time( ) - time0, type_disp.upper( ), inc_data[ 'prefix' ] ) )

def main( ):
    time0 = time.time( )
    state_names = _get_state_names( )
    msa_names = _get_msa_names( )

    parser = ArgumentParser( )
    parser.add_argument(
        '-d', '--dirname', dest='dirname', type=str, action = 'store', default = os.getcwd( ),
        help = 'The directory into which to store the resulting files. Default is %s.' % os.getcwd( ) )
    parser.add_argument(
        '--info', dest='do_info', action='store_true', default = False,
        help = 'If chosen, then print out INFO level logging statements.' )
    parser.add_argument(
        '-R', '--region', dest='region', type=str, action='store', default = 'nyc',
        help = 'Make movies or other summary 7 day averaged COVID-19 data for a geographical region. Can be a state, can be an MSA, or can be "conus". Default is "nyc".' )
    parser.add_argument(
        '--states', dest='do_states', action='store_true', default = False,
        help = 'If chosen, then print out possible states as regions that you can choose.' )
    parser.add_argument(
        '--msas', dest='do_msas', action='store_true', default = False,
        help = 'If chosen, then print out possible MSAs as regions that you can choose.' )
    #
    subparsers = parser.add_subparsers(
        help = ' '.join([
            'Choose one of three options:',
            '(m) make a movie of the COVID-19 cumulative stats for the state;',
            '(s) dumps summary plots of last incident date,',
            'and cumulative covid-19 stats, of a state;',
            'and (mcd) make a movie of either "CASES" or "DEATHS" in the state.' ] ),
        dest = 'choose_option' )
    #
    ## make summary movie (m)
    parser_moviereg = subparsers.add_parser( 'm', help = 'Make a movie of the COVID-19 7-day averaged new cases and deaths trend for a geographical region.' )
    parser_moviereg.add_argument(
        '-s', '--saveimages', dest='moviereg_saveimages', action='store_true', default=False,
        help = 'If chosen, then save the images used to create the movie into a ZIP archive.' )
    #
    ## make summary plots of last day, and COVID-19 cases/deaths in pandas dataframe up to last day.
    parser_sumreg = subparsers.add_parser(
        's', help = ' '.join([
            'Make a summary plot, and incident data file,',
            'of COVID-19 7-day averaged new cases and deaths trend,',
            'for a geographical region.' ] ) )
    #
    ## make a movie of cases OR deaths (mcd)
    parser_movcasedeath = subparsers.add_parser(
        'mcd', help = 'Make a large-sized movie of either "CASES" or "DEATHS" for a geographical region.' )
    parser_movcasedeath.add_argument(
        '-D', '--disp', dest='movcasedeath_display', type=str, action='store', default = 'cases', metavar = 'DISP',
        choices = ( 'cases', 'deaths' ), help = 'Whether to display the "cases" or "death" trends of the given state. Default is "cases".')
    parser_movcasedeath.add_argument(
        '-s', '--saveimages', dest='movcasedeath_saveimages', action='store_true', default=False,
        help = 'If chosen, then save the images used to create the movie into a ZIP archive.' )
    #
    ## argument and very preliminary functionalities
    args = parser.parse_args( )
    logger = logging.getLogger( )
    if args.do_info: logger.setLevel( logging.INFO )
    num_flags_region_names = len(list(
        filter(lambda flg: flg is True, ( args.do_states, args.do_msas ) ) ) )
    if num_flags_region_names > 1:
        print( 'Error, only one of --states or --msas must be defined. Exiting...' )
        return
    if args.do_states:
        print( 'here are the %d states: %s.' % ( len( state_names ), state_names ) )
        return
    if args.do_msas:
        print( 'here are the %d MSAs: %s.' % ( len( msa_names ), msa_names ) )
        return
    #
    ## 
    if args.region.lower( ) in msa_names + [ 'conus', ]:
        inc_data = _get_inc_data_msa_or_conus( args.region.lower( ) )
    elif args.region in state_names:
        inc_data = _get_inc_data_state( args.region )
    else:
        raise ValueError("Error, region = %s not one of the %d states, %d MSAs, or 'conus'." % (
            len( state_names ), len( msa_names ) ) )
    #
    ## quad movie summary
    if args.choose_option == 'm':
        _movie_inc_data_rate(
            inc_data, args.dirname, time0, save_imgfiles = args.moviereg_saveimages )
    #
    ## COVID-19 7-day average rate stats up to last day
    elif args.choose_option == 's':
        _summarize_inc_data_rate( inc_data, args.dirname, time0 )
    #
    ## movie of only either COVID-19 cases or deaths
    elif args.choose_option == 'mcd':
        _movie_casedeaths_inc_data_rate(
            inc_data, args.dirname, time0, type_disp = args.movcasedeath_display,
            save_imgfiles = args.movcasedeath_saveimages )
