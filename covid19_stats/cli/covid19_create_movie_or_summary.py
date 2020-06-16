#!/usr/bin/env python3

import sys, signal
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )
signal.signal( signal.SIGINT, signal_handler )
import os, numpy, tempfile, warnings, tabulate, logging
from engine import core, viz, get_string_commas_num, find_plausible_maxnum
from argparse import ArgumentParser

#
## suppress warnings
warnings.simplefilter( 'ignore' )

def _summarize_data( data_msa, maxnum ):
    regionName = data_msa[ 'region name' ]
    population = data_msa[ 'population' ]
    inc_data = core.get_incident_data( data_msa )
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
    parser = ArgumentParser( )
    parser.add_argument( '--info', dest='do_info', action='store_true', default = False, help = 'If chosen, then print out INFO level logging statements.' )
    #
    subparsers = parser.add_subparsers( help = 'Choose one of three options: (M) summarizes stats from metros; (m) make a movie of a metro region; and (s) dumps summary plots of last incident date, and cumulative covid-19 stats, of a metro region.', dest = 'choose_option' )
    #
    ## list of metros (M)
    parser_showmetros = subparsers.add_parser( 'M', help = 'If chosen, then list all the metropolitan areas through which we can look.' )
    parser_showmetros.add_argument( '-f', '--format', help = 'Format of the table that displays MSA summary. Default is "simple".',
                                   type=str, action='store', choices = [ 'simple', 'github', 'rst' ], default = 'simple' )
    parser_showmetros.add_argument( '--metros', help = 'If chosen, list of selected metros for which to summarize COVID-19 data.',
                                   type=str, action='store' )
    #
    ## make summary movie (m)
    parser_moviemetro = subparsers.add_parser( 'm', help = 'Make a movie of the COVID-19 cases and deaths trend for the specific Metropolitan Statistical Area (MSA).' )
    parser_moviemetro.add_argument( '-n', '--name', dest='name', type=str, action='store', default = 'bayarea',
                                   help = 'Make a movie of this metropolitan area. Default is "bayarea"' )
    parser_moviemetro.add_argument( '-M', '--maxnum', dest='maxnum', type=int, action='store', default = 5000,
                                   help = ' '.join([
                                       'The limit of cases/deaths to visualize.',
                                       'Default is %s.' % get_string_commas_num( 5000 ),
                                       'You should use a limit larger (by at least 2, no more than 10) than the maximum number of cases recorded for a county in that MSA.' ]) )
    parser_moviemetro.add_argument( '--conus', dest='do_conus', action='store_true', default = False,
                                   help = 'If chosen, then make a movie of the COVID-19 cases and deaths trends for the Continental US (CONUS).' )
    parser_moviemetro.add_argument(
        '-y', '--yes', dest='do_yes_moviemetro', action='store_true', default = False,
        help = 'If chosen, then do not confirm --maxnum.' )
    #
    ## make summary plots of last day, and COVID-19 cases/deaths in pandas dataframe up to last day.
    parser_summmetro  = subparsers.add_parser( 's', help = 'Make a summary plot, and incident data file, of COVID-19 cases and deaths trend, for the specific Metropolitan Statistical Area (MSA).' )
    parser_summmetro.add_argument( '-n', '--name', dest='summmetro_name', type=str, action='store', default = 'bayarea', metavar = 'NAME',
                                  help = ' '.join([
                                      'Create a summary plot and incident data file of this metropolitan area.',
                                      'Default is "bayarea".' ]))
    parser_summmetro.add_argument( '-M', '--maxnum', dest='summmetro_maxnum', type=int, action='store', default = 5000, metavar = 'MAXNUM',
                                  help = ' '.join([
                                      'The limit of cases/deaths to visualize.',
                                      'Default is %s.' % get_string_commas_num( 5000 ),
                                      'You should use a limit larger (by at least 2, no more than 10) than the maximum number of cases recorded for a county in that MSA.' ]) )
    parser_summmetro.add_argument( '--conus', dest='do_conus_summmetro', action='store_true', default = False,
                                  help = 'If chosen, then make a movie of the COVID-19 cases and deaths trends for the Continental US (CONUS).' )
    parser_summmetro.add_argument(
        '-y', '--yes', dest='do_yes_summmetro', action='store_true', default = False,
        help = 'If chosen, then do not confirm --maxnum.' )
    #
    ## make a movie of cases OR deaths
    parser_movcasedeath = subparsers.add_parser( 'mcd', help = 'Make a large-sized movie of either "CASES" or "DEATHS" for given MSA or CONUS.' )
    parser_movcasedeath.add_argument( '-n', '--name', dest='movcasedeath_name', type=str, action='store', default = 'bayarea', metavar = 'NAME',
                                     help = ' '.join([
                                         'Create a summary plot and incident data file of this metropolitan area.',
                                         'Default is "bayarea".' ]))
    parser_movcasedeath.add_argument(
        '-d', '--disp', dest='movcasedeath_display', type=str, action='store', default = 'cases', metavar = 'DISP',
        choices = ( 'cases', 'deaths' ), help = 'Whether to display the "cases" or "death" trends of the MSA or CONUS. Default is "cases".')
    parser_movcasedeath.add_argument( '-M', '--maxnum', dest='movcasedeath_maxnum', type=int, action='store', default = 5000, metavar = 'MAXNUM',
                                  help = ' '.join([
                                      'The limit of cases/deaths to visualize.',
                                      'Default is %s.' % get_string_commas_num( 5000 ),
                                      'You should use a limit larger (by at least 2, no more than 10) than the maximum number of cases recorded for a county in that MSA.' ]) )
    parser_movcasedeath.add_argument( '--conus', dest='do_conus_movcasedeath', action='store_true', default = False,
                                  help = 'If chosen, then make a movie of the COVID-19 cases and deaths trends for the Continental US (CONUS).' )
    parser_movcasedeath.add_argument(
        '-y', '--yes', dest='do_yes_movcasedeath', action='store_true', default = False,
        help = 'If chosen, then do not confirm --maxnum.' )
    #
    ##
    args = parser.parse_args( )
    logger = logging.getLogger( )
    if args.do_info: logger.setLevel( logging.INFO )
    #
    ## just show the metros
    if args.choose_option == 'M':
        metros = None
        if args.metros is not None:
            metros = set(list(map(lambda tok: tok.strip( ), args.metros.split(','))))
        core.display_tabulated_metros( form = args.format, selected_metros = metros )
        return
    if args.choose_option == 'm':
        #
        ## now create the following stuff...
        if not args.do_conus:
            msaname = args.name.strip( )
            if msaname not in core.data_msas_2019:
                print( 'Error, the chosen MSA name %s not one of the %d defined.' % (
                    msaname, len( data.engine_msas_2019 ) ) )
                return
            data = core.data_msas_2019[ msaname ]
        else: data = core.data_conus
        maxnum = args.maxnum
        if maxnum < 1:
            print( 'Error, maximum number for visualization %d < 1.' % maxnum )
            return
        _summarize_data( data, maxnum )
        if args.do_yes_moviemetro: status = args.do_yes_moviemetro
        else: status = _try_continue( )
        if status:
            movie_name = viz.create_summary_movie_frombeginning(
                data = data, maxnum_colorbar = maxnum )
            return
        
    if args.choose_option == 's':
        #
        ## now create the following stuff...
        if not args.do_conus_summmetro:
            msaname = args.summmetro_name.strip( )
            if msaname not in core.data_msas_2019:
                print( 'Error, the chosen MSA name %s not one of the %d defined.' % (
                    msaname, len( core.data_msas_2019 ) ) )
                return
            data = core.data_msas_2019[ msaname ]
        else: data = core.data_conus
        maxnum = args.summmetro_maxnum
        if maxnum < 1:
            print( 'Error, maximum number for visualization %d < 1.' % maxnum )
            return

        _summarize_data( data, maxnum )
        if args.do_yes_summmetro: status = args.do_yes_summmetro
        else: status = _try_continue( )
        if status:
            viz.get_summary_demo_data( data, maxnum_colorbar = maxnum )
            return
    if args.choose_option == 'mcd':
        #
        ## now create the following stuff...
        if not args.do_conus_movcasedeath:
            msaname = args.movcasedeath_name.strip( )
            if msaname not in core.data_msas_2019:
                print( 'Error, the chosen MSA name %s not one of the %d defined.' % (
                    msaname, len( core.data_msas_2019 ) ) )
                return
            data = core.data_msas_2019[ msaname ]
        else: data = core.data_conus
        maxnum = args.movcasedeath_maxnum
        if maxnum < 1:
            print( 'Error, maximum number for visualization %d < 1.' % maxnum )
            return

        _summarize_data( data, maxnum )
        if args.do_yes_movcasedeath: status = args.do_yes_movcasedeath
        else: status = _try_continue( )
        if status:
            viz.create_summary_cases_or_deaths_movie_frombeginning(
                data = data, maxnum_colorbar = args.movcasedeath_maxnum,
                type_disp = args.movcasedeath_display )
            return

if __name__ == '__main__':
    main( )
