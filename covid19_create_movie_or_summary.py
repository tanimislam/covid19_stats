#!/usr/bin/env python3

import os, sys, numpy, tabulate, tempfile
from engine import viz, core
from argparse import ArgumentParser

#
## secret sauce formatting comma'd integers from https://intellipaat.com/community/2447/how-to-print-number-with-commas-as-thousands-separators
def _get_string_commas_num( num ):
    return "%s" % f"{num:,d}"

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
        '2019 EST. POP = %s.' % _get_string_commas_num( population ),
        'FIRST CASE:  %s.' % first_date.strftime( '%d %B %Y' ),
        'LATEST CASE: %s (%d days after first case)' % (
            last_date.strftime( '%d %B %Y' ), last_day ),
        'MAXIMUM NUMBER OF CASES: %d (in %s County, %s)' % (
            max_cases, max_cs[ 'county' ], max_cs[ 'state' ] ),
        'MAXIMUM NUMBER OF CASES FOR VISUALIZATION: %d.' % maxnum,
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
    subparsers = parser.add_subparsers( help = 'Choose either showing list of metros, or make a movie of a metro region', dest = 'choose_option' )
    parser_showmetros = subparsers.add_parser( 'M', help = 'If chosen, then list all the metropolitan areas through which we can look.' )
    parser_showmetros.add_argument( '-f', '--format', help = 'Format of the table that displays MSA summary. Default is "simple".',
                                   type=str, action='store', choices = [ 'simple', 'github', 'rst' ], default = 'simple' )
    #
    parser_moviemetro = subparsers.add_parser( 'm', help = 'Make a movie of the COVID-19 cases and deaths trend for the specific Metropolitan Statistical Area (MSA).' )
    parser_moviemetro.add_argument( '-n', '--name', dest='name', type=str, action='store', default = 'bayarea',
        help = 'Make a movie of this metropolitan area. Default is "bayarea"' )
    parser_moviemetro.add_argument( '-M', '--maxnum', dest='maxnum', type=int, action='store', default = 5000,
                                   help = ' '.join([
                                       'The limit of cases/deaths to visualize.',
                                       'Default is 5000.',
                                       'You should use a limit larger (by at least 2, no more than 10) than the maximum number of cases recorded for a county in that MSA.' ]) )
    #
    parser_summmetro  = subparsers.add_parser( 's', help = 'Make a summary plot, and incident data file, of COVID-19 cases and deaths trend, for the specific Metropolitan Statistical Area (MSA).' )
    parser_summmetro.add_argument( '-n', '--name', dest='summmetro_name', type=str, action='store', default = 'bayarea',
                                  help = ' '.join([
                                      'Create a summary plot and incident data file of this metropolitan area.',
                                      'Default is "bayarea".' ]))
    parser_summmetro.add_argument( '-M', '--maxnum', dest='summmetro_maxnum', type=int, action='store', default = 5000,
                                  help = ' '.join([
                                      'The limit of cases/deaths to visualize.',
                                      'Default is 5000.',
                                      'You should use a limit larger (by at least 2, no more than 10) than the maximum number of cases recorded for a county in that MSA.' ]) )
    args = parser.parse_args( )
    #
    ## just show the metros
    if args.choose_option == 'M':
        core.display_tabulated_metros( form = args.format )
        return
    if args.choose_option == 'm':
        #
        ## now create the following stuff...
        msaname = args.name.strip( )
        if msaname not in core.data_msas_2019:
            print( 'Error, the chosen MSA name %s not one of the %d defined.' % (
                msaname, len( data.engine_msas_2019 ) ) )
            return
        maxnum = args.maxnum
        if maxnum < 1:
            print( 'Error, maximum number for visualization %d < 1.' % maxnum )
            return
        data_msa = core.data_msas_2019[ msaname ]
        _summarize_data( data_msa, maxnum )
        status = _try_continue( )
        if status:        
            movie_name = viz.create_summary_movie_frombeginning(
            data = data_msa, maxnum_colorbar = maxnum )
            return
    if args.choose_option == 's':
        #
        ## now create the following stuff...
        msaname = args.summmetro_name.strip( )
        if msaname not in core.data_msas_2019:
            print( 'Error, the chosen MSA name %s not one of the %d defined.' % (
                msaname, len( data.engine_msas_2019 ) ) )
            return
        maxnum = args.summmetro_maxnum
        if maxnum < 1:
            print( 'Error, maximum number for visualization %d < 1.' % maxnum )
            return
        
        data_msa = core.data_msas_2019[ msaname ]
        _summarize_data( data_msa, maxnum )
        status = _try_continue( )
        if status:
            viz.get_summary_demo_data( data_msa, maxnum_colorbar = maxnum )
            return
            
            
if __name__ == '__main__':
    main( )
