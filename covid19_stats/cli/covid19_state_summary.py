import sys, signal
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )
signal.signal( signal.SIGINT, signal_handler )
import os, numpy, tempfile, warnings, tabulate, logging
from itertools import chain
from covid19_stats.engine import ( core, viz, get_string_commas_num,
                                  find_plausible_maxnum )
from argparse import ArgumentParser

#
## suppress warnings
warnings.simplefilter( 'ignore' )

def _summarize_data( data_state, maxnum ):
    regionName = data_state[ 'region name' ]
    population = data_state[ 'population' ]
    inc_data = core.get_incident_data( data_state )
    max_fips, max_cases = core.get_maximum_cases( inc_data )
    max_cs = core.get_county_state( max_fips )
    first_date = inc_data['df'].date.min( )
    last_date = inc_data['df'].date.max( )
    last_day = inc_data[ 'last day' ]
    print( '\n'.join([
        'HERE ARE DETAILS FOR %s.' % regionName,
        '2019 EST. POP = %s.' % get_string_commas_num( population ),
        'FIRST CASE:  %s.' % first_date.strftime( '%d %B %Y' ),
        'LATEST CASE: %s (%d days after first case)' % (
            last_date.strftime( '%d %B %Y' ), last_day ),
        'MAXIMUM NUMBER OF CASES: %s (in %s, %s)' % (
            get_string_commas_num(max_cases),
            max_cs[ 'county' ], max_cs[ 'state' ] ),
        'MAXIMUM NUMBER OF CASES FOR VISUALIZATION: %s.' % get_string_commas_num( maxnum ),
        ] ) )

def _try_continue( ):
    val = str(input( 'CONTINUE (must choose one) [y/n]: ')).lower( )
    val_map = { 'y' : True, 'n' : False }
    if val not in ( 'y', 'n' ):
        print( "chosen value not one of 'y' or 'n'. Default chosen is 'n'." )
        return False
    return val_map[ val ]

def main( ):
    all_state_territory_choices = sorted(chain.from_iterable(
        map(lambda arr: arr.keys( ), (
            core.mapping_state_rname_conus,
            core.mapping_state_rname_nonconus ) ) ) )
    
    parser = ArgumentParser( )
    parser.add_argument(
        '-d', '--dirname', dest='dirname', type=str, action = 'store', default = os.getcwd( ),
        help = 'The directory into which to store the resulting files. Default is %s.' % os.getcwd( ) )
    parser.add_argument(
        '--info', dest='do_info', action='store_true', default = False,
        help = 'If chosen, then print out INFO level logging statements.' )
    parser.add_argument(
        '-n', dest='name', type=str, action='store', default = 'New York',
        help = 'Make movies or other summary data for a state. Default is "New York".',
        choices = all_state_territory_choices )
    parser.add_argument(
        '-M', '--maxnum', dest='maxnum', type=int, action='store', default = None, metavar = 'MAXNUM',
        help = ' '.join([
            'The limit of cases/deaths to visualize.',
            'Default is a plausible amount for the chosen state.',
            'You should use a limit larger (by at least 2, no more than 10) than',
            'the maximum number of cases recorded for a county in that state.' ]) )
    parser.add_argument(
        '-y', '--yes', dest='do_yes', action='store_true', default = False,
        help = 'If chosen, then do not confirm --maxnum.' )
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
    parser_moviestate = subparsers.add_parser( 'm', help = 'Make a movie of the COVID-19 cases and deaths trend for the specific state.' )
    #
    ## make summary plots of last day, and COVID-19 cases/deaths in pandas dataframe up to last day.
    parser_sumstate  = subparsers.add_parser(
        's', help = ' '.join([
            'Make a summary plot, and incident data file,',
            'of COVID-19 cases and deaths trend,',
            'for the specific state.' ] ) )
    #
    ## make a movie of cases OR deaths
    parser_movcasedeath = subparsers.add_parser(
        'mcd', help = 'Make a large-sized movie of either "CASES" or "DEATHS" for given state.' )
    parser_movcasedeath.add_argument(
        '-d', '--disp', dest='movcasedeath_display', type=str, action='store', default = 'cases', metavar = 'DISP',
        choices = ( 'cases', 'deaths' ), help = 'Whether to display the "cases" or "death" trends of the MSA or CONUS. Default is "cases".')
    #
    ##
    args = parser.parse_args( )
    logger = logging.getLogger( )
    if args.do_info: logger.setLevel( logging.INFO )
    statename = args.name.strip( )
    if statename in core.mapping_state_rname_conus:
        data_state = core.data_states[
            core.mapping_state_rname_conus[ statename ] ]
    else:
        data_state = core.data_nonconus_states_territories[
            core.mapping_state_rname_nonconus[ statename ] ]
        
    maxnum = args.maxnum
    if maxnum is None:
        max_cases = core.get_max_cases_county( core.get_incident_data( data_state ) )[ 'cases' ]
        maxnum = find_plausible_maxnum( max_cases )
    if maxnum < 1:
        print( 'Error, maximum number for visualization %d < 1.' % maxnum )
        return
    _summarize_data( data_state, maxnum )
        
    #
    ## quad movie summary
    if args.choose_option == 'm':
        if args.do_yes: status = args.do_yes
        else: status = _try_continue( )
        if not status: return
        movie_name = viz.create_summary_movie_frombeginning(
            data = data_state, maxnum_colorbar = maxnum,
            dirname = args.dirname )
    #
    ## cumulative COVID-19 stats up to last day
    elif args.choose_option == 's':
        if args.do_yes: status = args.do_yes
        else: status = _try_continue( )
        if not status: return
        viz.get_summary_demo_data(
            data_state, maxnum_colorbar = maxnum, dirname = args.dirname )
    #
    ## movie of only either COVID-19 cases or deaths
    elif args.choose_option == 'mcd':
        if args.do_yes: status = args.do_yes
        else: status = _try_continue( )
        if not status: return
        #
        viz.create_summary_cases_or_deaths_movie_frombeginning(
            data = data_state, maxnum_colorbar = maxnum,
            type_disp = args.movcasedeath_display,
            dirname = args.dirname )
