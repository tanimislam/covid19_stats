import os, sys, numpy, glob, tabulate, logging, requests, json
import datetime, pandas, titlecase, networkx
from pathos.multiprocessing import Pool, cpu_count
from itertools import chain
from dateutil.relativedelta import relativedelta
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from jinja2 import Environment, FileSystemLoader, Template
from urllib.parse import urljoin
from dateutil.relativedelta import relativedelta
#
from covid19_stats import COVID19Database, resourceDir
from covid19_stats.engine import gis

def get_boundary_dict( fips_collection ):
    fips_data_2018 = COVID19Database.fips_data_2018( )
    boundary_dict = dict(map(lambda fips: (
        fips, fips_data_2018[ fips ][ 'points' ] ), fips_collection ) )
    return boundary_dict

def get_mp4_album_name( data ):
    data_states_territories_names = set( COVID19Database.data_states( ) ) | set(
        COVID19Database.data_nonconus_states_territories())
    if data['prefix'] in data_states_territories_names:
        return 'STATE'
    if data['prefix'].lower( ) == 'conus':
        return 'CONUS'
    return 'METROPOLITAN STATISTICAL AREA'

#
## now stuff associated with the fips : county/state mapping
def get_county_state( fips ):
    fips_countystate_dict = COVID19Database.fips_countystate_dict( )
    if fips not in fips_countystate_dict: return None
    return fips_countystate_dict[ fips ]

def get_fips_msa( county, state ):
    fips_msas_2019 = COVID19Database.fips_msas_2019( )
    data_msas_2019 = COVID19Database.data_msas_2019( )
    #
    tup = ( county, state )
    assert( tup in cs_fips_dict )
    fips = cs_fips_dict[ tup ]
    msaname = fips_msas_2019[ fips ]
    data_msa = data_msas_2019[ msaname ]
    return ( fips, data_msa )

def get_msa_data( msaname ):
    data_msas_2019 = COVID19Database.data_msas_2019( )
    assert( msaname in data_msas_2019 )
    return data_msas_2019[ msaname ].copy( )

def get_data_fips( fips ):
    all_counties_nytimes_covid19_data = COVID19Database.all_counties_nytimes_covid19_data( )
    data_by_date = sorted(filter(lambda entry: entry['fips'] == fips,
                                 all_counties_nytimes_covid19_data ),
                          key = lambda entry: entry['date'] )
    return data_by_date

def get_max_cases_county( inc_data ):
    df = inc_data['df']
    fips_max, case_max = max(map(lambda key: ( key.split('_')[-1].strip( ), df[key].max( ) ),
                                 filter(lambda key: key.startswith('cases_'), df)),
                             key = lambda tup: tup[-1] )
    cs_max = get_county_state( fips_max )
    return { 'fips' : fips_max, 'cases' : case_max, 'county' : cs_max[ 'county'],
            'state' : cs_max[ 'state' ] }

def get_incident_data( data = None ):
    if data is None: data = get_msa_data( 'bayarea' )
    prefix = data[ 'prefix' ]
    regionName = data[ 'region name' ]
    fips_collection = set( data['fips'] )
    #
    ## now this creates a dictionary of incidents and deaths per county
    all_data_region = sorted(
        chain.from_iterable(map(
            get_data_fips, fips_collection ) ),
        key = lambda entry: entry['date'] )
    #
    ## now create a dictionary of cases, with key being the date, value being list of entries of counties for that date
    all_data_region_bydate = { }
    for entry in all_data_region:
        mydate = entry[ 'date' ]
        all_data_region_bydate.setdefault( mydate, [] ).append( entry )  
    #
    ## now create a dictionary of cumulative deaths and cases by date
    cases_deaths_region_bydate = dict(
        map(lambda mydate: ( mydate, { 'cumulative cases' : sum(
            map(lambda entry: entry['cumulative cases' ], all_data_region_bydate[ mydate ] ) ),
                                      'cumulative death' : sum(
                                          map(lambda entry: entry['cumulative death' ],
                all_data_region_bydate[ mydate ] ) ) } ),
            all_data_region_bydate ) )
    #
    ## now create the dataframe to analyse
    df_cases_deaths_region = pandas.DataFrame({
        'date' : sorted( cases_deaths_region_bydate ),
        'cases' : list(map(lambda mydate:
                        cases_deaths_region_bydate[mydate][ 'cumulative cases' ],
                        sorted( cases_deaths_region_bydate ) ) ),
        'death' : list(map(lambda mydate:
                        cases_deaths_region_bydate[mydate][ 'cumulative death' ],
                        sorted( cases_deaths_region_bydate ) ) ) } )
    df_cases_deaths_region[ 'days_from_beginning' ] = list(
        map(lambda mydate: ( mydate - min( cases_deaths_region_bydate ) ).days, 
            df_cases_deaths_region.date ) )
    #
    ## now get the cumulative cases and cumulative deaths by FIPS code
    cases_deaths_region_byfips_bydate = { }
    for mydate in all_data_region_bydate:
        data_mydate = { }
        fips_excl = fips_collection - set(map(lambda entry: entry['fips'], all_data_region_bydate[ mydate ]))
        for fips in fips_excl:
            data_mydate[ fips ] = { 'cumulative cases' : 0, 'cumulative death' : 0 }
        for entry in all_data_region_bydate[ mydate ]:
            data_mydate[ entry[ 'fips' ] ] = {
                'cumulative cases' : entry[ 'cumulative cases' ],
                'cumulative death' : entry[ 'cumulative death' ] }
        cases_deaths_region_byfips_bydate[ mydate ] = data_mydate
    #
    ## now add cumulative deaths and cases by fips data to the dataframe
    for fips in sorted(fips_collection):
        df_cases_deaths_region[ 'cases_%s' % fips ] = list(
            map(lambda mydate: cases_deaths_region_byfips_bydate[ mydate ][ fips ][ 'cumulative cases' ],
                sorted( cases_deaths_region_bydate ) ) )
        df_cases_deaths_region[ 'deaths_%s' % fips ] = list(
            map(lambda mydate: cases_deaths_region_byfips_bydate[ mydate ][ fips ][ 'cumulative death' ],
                sorted( cases_deaths_region_bydate ) ) )
    #
    ## now calculate the bounding box of this collection of fips data
    boundary_dict = get_boundary_dict( fips_collection )
    total_bbox = gis.calculate_total_bbox( chain.from_iterable(
        boundary_dict.values( ) ) )
    incident_data = {
        'df' : df_cases_deaths_region, 'bbox' : total_bbox, 'boundaries' : boundary_dict,
        'last day' : df_cases_deaths_region.days_from_beginning.max( ) }
    return incident_data

def get_maximum_cases( inc_data ):
    df = inc_data[ 'df' ]
    max_case_tup = max(map(lambda key: (
        key.replace('cases_', '').strip( ),
        df[key].max( ) ), filter(lambda key: key.startswith('cases_'), df ) ),
                       key = lambda tup: tup[1] )
    return max_case_tup

def create_readme_from_template(
    mainURL = 'https://tanimislam.github.io/covid19movies',
    dirname_for_readme_location = os.getcwd( ), verify = True,
    topN_json = None ):
    def _get_string_commas_num( num ):
        return "%s" % f"{num:,d}"
    
    assert( os.path.isdir( dirname_for_readme_location ) )
    response = requests.get( mainURL, verify = verify )
    if response.status_code != 200:
        raise ValueError("Error, could not access %s." % mainURL )
    #
    ## now see if I can find this entry
    if topN_json is None:
        topNjson_url = os.path.join( mainURL, 'covid19_topN_LATEST.json' )
        response = requests.get( topNjson_url, verify = verify )
        if response.status_code != 200:
            raise ValueError("Error, could not access the JSON data for the top-N MSA COVID-19 summary data." %
                             topNjson_url )
        #
        ## now load JSON into data
        msa_summary = sorted(json.loads( response.content ), key = lambda entry: entry[ 'RANK' ] )
    else:
        assert( os.path.isfile( topN_json ) )
        assert( os.path.basename( topN_json ).endswith( '.json' ) )
        msa_summary = sorted( json.load( open( topN_json, 'r' ) ), key = lambda entry: entry[ 'RANK' ] )
    assert( len( msa_summary ) > 0 )
    #
    ## now figure out the date, formatted properly
    first_inc_date = datetime.datetime.strptime( msa_summary[ 0 ][ 'FIRST INC.' ], '%d %B %Y' ).date( )
    days_after_first = int( msa_summary[ 0 ][ 'NUM DAYS' ] )
    num_days_after = relativedelta( days = days_after_first )
    latest_date = first_inc_date + num_days_after
    latest_date_formatted = latest_date.strftime( '%d %B %Y' ).upper( )
    #
    ## now fill out the entries in the table
    def _return_entry_formatted( entry ):
        return {
            'RANK' : entry[ 'RANK' ],
            'PREFIX' : entry[ 'PREFIX' ],
            'NAME' : entry[ 'NAME' ],
            'POP_FORMATTED' : _get_string_commas_num( entry[ 'POPULATION' ] ),
            'FIRST_INCIDENT': entry[ 'FIRST INC.' ],
            'NUM_DAYS' : entry[ 'NUM DAYS' ],
            'NUM_CASES_FORMATTED' : _get_string_commas_num( entry[ 'NUM CASES' ] ),
            'NUM_DEATHS_FORMATTED': _get_string_commas_num( entry[ 'NUM DEATHS' ] ),
            'MAX_CASE_COUNTY_FORMATTED' : _get_string_commas_num( entry[ 'MAX CASE COUNTY' ] ),
            'MAX_CASE_COUNTY_NAME' : entry[ 'MAX CASE COUNTY NAME' ] }
    covid19_stats_data = {
        'latest_date_formatted' : latest_date_formatted,
        'msa_summary' : list(map(_return_entry_formatted, msa_summary ) ),
        'msa_summary_num' : len( msa_summary ),
    }
    #
    ## now jinja-fy it!
    env = Environment( loader = FileSystemLoader( resourceDir ) )
    template = env.get_template( 'README_template.rst' )
    with open( os.path.join( dirname_for_readme_location, 'README.rst' ), 'w' ) as openfile:
        openfile.write( '%s\n' % template.render( covid19_stats_data = covid19_stats_data ) )
    

def display_tabulated_metros_fromjson( summary_data_json ):
    def _get_string_commas_num( num ):
        return "%s" % f"{num:,d}"
    
    def _get_row( entry ):
        return (
            entry[ 'RANK' ],
            entry[ 'PREFIX' ],
            entry[ 'NAME' ],
            _get_string_commas_num( entry[ 'POPULATION' ] ),
            entry[ 'FIRST INC.' ],
            entry[ 'NUM DAYS' ],
            _get_string_commas_num( entry[ 'NUM CASES' ] ),
            _get_string_commas_num( entry[ 'NUM DEATHS' ] ),
            _get_string_commas_num( entry[ 'MAX CASE COUNTY' ] ),
            entry[ 'MAX CASE COUNTY NAME' ] )

    first_entry = summary_data_json[ 0 ]
    first_inc_date = datetime.datetime.strptime( first_entry[ 'FIRST INC.' ], '%d %B %Y' ).date( )
    date_last = first_inc_date + relativedelta( days = first_entry[ 'NUM DAYS' ] )    
    data_tabulated = list(map(_get_row, sorted( summary_data_json, key = lambda entry: entry['RANK'] ) ) )
    #
    lines = [ '.. list-table:: COVID-19 STATS FOR %d METROS AS OF %s.' % (
            len( summary_data_json ), date_last.strftime( '%d %B %Y' ) ), ]
    lines.append( '   :widths: auto' )
    lines.append( '' )
    lines.append( '   * - RANK' )
    for column in (
        'IDENTIFIER', 'NAME', 'POPULATION', 'FIRST INC.',
        'NUM DAYS', 'NUM CASES', 'NUM DEATHS', 'MAX CASE COUNTY', 'MAX CASE COUNTY NAME' ):
        lines.append( '     - %s' % column )
    for row in data_tabulated:
        lines.append( '   * - %d' % row[0] )
        for entry in row[1:]:
            lines.append( '     - %s' % entry )

    return '\n'.join( lines )

def display_tabulated_metros( form = 'simple', selected_metros = None ):
    data_msas_2019 = COVID19Database.data_msas_2019( )
    assert( form in ( 'simple', 'github', 'rst', 'rst-simple', 'json' ) )
    print_table = True
    to_json = False
    if form == 'rst-simple': print_table = False
    if form == 'json': to_json = True
    all_metros = sorted(
        data_msas_2019.values( ),
        key = lambda entry: entry['population'])[::-1]
    #
    ## now if selected metros is not None
    ## only display selected metros by population max to min
    if selected_metros is not None:
        selected_metros_act = set( selected_metros ) & set(map(lambda entry: entry['prefix'], all_metros ) )
        if len( selected_metros_act ) == 0:
            raise ValueError( "Error, no metros chosen" )
        all_metros = sorted(
            filter(lambda entry: entry['prefix'] in selected_metros_act, all_metros ),
            key = lambda entry: entry['population'])[::-1]

    #
    ## now get incident data for each metro
    incident_data_dict = { }
    with Pool( processes = cpu_count( ) ) as pool:
        incident_data_dict = dict(pool.map(
            lambda prefix: ( prefix, get_incident_data( data_msas_2019[ prefix ] ) ),
            data_msas_2019 ) )
    date_last = max(map(lambda inc_data: inc_data['df'].date.max( ), incident_data_dict.values()))
    
    #
    ## secret sauce formatting comma'd integers from https://intellipaat.com/community/2447/how-to-print-number-with-commas-as-thousands-separators
    def _get_string_commas_num( num ):
        return "%s" % f"{num:,d}"

    def _get_row( tup ):
        idx, (data_msa, to_json) = tup
        rank = idx + 1
        prefix = data_msa[ 'prefix' ]
        regionName = data_msa[ 'region name' ]
        population_s = _get_string_commas_num( data_msa[ 'population' ] )
        #
        inc_data = incident_data_dict[ prefix ]
        df = inc_data[ 'df' ]
        date_first_s = df.date.min( ).strftime( '%d %B %Y' )
        last_day     = inc_data[ 'last day' ]
        num_cases    = df.cases.max( )
        num_death    = df.death.max( )
        max_case_data= get_max_cases_county( inc_data )
        max_case_co  = max_case_data[ 'cases' ]
        max_case_co_county = max_case_data[ 'county' ]
        max_case_co_state  = max_case_data[ 'state'  ]
        if to_json:
            return {
                'RANK' : rank,
                'PREFIX' : prefix,
                'NAME' : regionName,
                'POPULATION' : data_msa[ 'population' ],
                'FIRST INC.' : date_first_s,
                'NUM DAYS' : int( inc_data[ 'last day' ] ),
                'NUM CASES' : int( df.cases.max( ) ),
                'NUM DEATHS': int( df.death.max( ) ),
                'MAX CASE COUNTY' : int( max_case_data[ 'cases' ] ),
                'MAX CASE COUNTY NAME' : '%s, %s' % ( max_case_co_county, max_case_co_state )
                }
        return (
            rank, prefix, regionName, population_s,
            date_first_s, last_day,
            _get_string_commas_num(num_cases),
            _get_string_commas_num(num_death),
            _get_string_commas_num(max_case_co),
            '%s, %s' % ( max_case_co_county, max_case_co_state ) )
    
    data_tabulated = list(map(
        _get_row, enumerate(zip(all_metros, len(all_metros) * [ to_json ] ) ) ) )
    if to_json:
        return data_tabulated
    if print_table:
        print( 'HERE ARE THE %d METRO AREAS, ORDERED BY POPULATION' % len( all_metros ) )
        print( 'DATA AS OF %s.' % date_last.strftime( '%d %B %Y' ) )
        print( '%s\n' % tabulate.tabulate(
            data_tabulated, headers = [
                'RANK', 'IDENTIFIER', 'NAME', 'POPULATION', 'FIRST INC.',
                'NUM DAYS', 'NUM CASES', 'NUM DEATHS', 'MAX CASE COUNTY', 'MAX CASE COUNTY NAME'  ],
            tablefmt = form, stralign = 'left' ) )
    else:
        print( '.. list-table:: COVID-19 STATS FOR %d METROS AS OF %s.' % (
            len( all_metros ), date_last.strftime( '%d %B %Y' ) ) )
        print( '   :widths: auto' )
        print( )
        print( '   * - RANK' )
        for column in (  'IDENTIFIER', 'NAME', 'POPULATION', 'FIRST INC.',
                       'NUM DAYS', 'NUM CASES', 'NUM DEATHS', 'MAX CASE COUNTY', 'MAX CASE COUNTY NAME' ):
            print( '     - %s' % column )
        for row in data_tabulated:
            print( '   * - %d' % row[0] )
            for entry in row[1:]:
                print( '     - %s' % entry )

#
## from a collection of FIPS, find the clusterings -- which set are adjacent to each other, which aren't
def get_clustering_fips( collection_of_fips, adj = None ):
    if adj is None: adj = COVID19Database.fips_adj_2018( )
    fips_rem = set( collection_of_fips )
    #
    ## our adjacency matrix from this
    subset = set(filter(lambda tup: all(map(lambda tok: tok in fips_rem, tup)), adj )) | \
      set(map(lambda fips: ( fips, fips ), fips_rem ))
    G = networkx.Graph( sorted( subset ) )
    #
    ## now greedy clustering algo
    fips_clusters = [ ]
    while len( fips_rem ) > 0:
        first_fips = min( fips_rem )
        fips_excl = fips_rem - set([ first_fips, ])
        fips_clust = [ first_fips ]
        for fips in fips_excl:
            try:
                dist = networkx.shortest_path_length( G, first_fips, fips )
                fips_clust.append( fips )
            except: pass
        fips_clusters.append( set( fips_clust ) )
        fips_rem = fips_rem - set( fips_clust )
    return fips_clusters
