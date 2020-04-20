import os, sys, numpy, glob, tabulate
import datetime, pandas, titlecase, networkx
import pathos.multiprocessing as multiprocessing
from itertools import chain
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from engine import gis, mainDir

def _get_stat_line( line ):
  line_split = list(map(lambda tok: tok.strip(), line.split(',')))
  dstring = line_split[0]
  county_name = line_split[1]
  state_name = line_split[2]
  fips = line_split[-3].strip( )
  if fips == '': return None
  cases_cumulative = int( line_split[-2] )
  death_cumulative = int( line_split[-1] )
  return {
      'date' : datetime.datetime.strptime(
        dstring, '%Y-%m-%d' ).date( ),
      'county' : county_name,
      'state' : state_name,
      'fips' : fips,
      'cumulative cases' : cases_cumulative,
      'cumulative death' : death_cumulative }

def _get_fips_county_state( entry ):
    return ( entry[ 'fips' ], entry[ 'county' ], entry[ 'state' ] )

all_counties_nytimes_covid19_data = list(filter(None,
    map(_get_stat_line,
        list( map(lambda line: line.strip(), filter(
            lambda line: len( line.strip( ) ) != 0,
            open( os.path.join( mainDir, "covid-19-data", "us-counties.csv" ), "r" ).readlines())))[1:])))

all_counties_state = list(map(
    lambda entry: { 'county' : entry[0], 'state' : entry[1] },
    set(map(lambda entry: ( entry['county'], entry['state'] ), all_counties_nytimes_covid19_data ) ) ) )

fips_data_2018 = gis.load_fips_data( )

fips_adj_2018 = gis.load_fips_adj( )

fips_countystate_dict = dict(map(lambda f_c_s: ( f_c_s[0], {
    'county' : f_c_s[1], 'state' : f_c_s[2] } ), set(
        map(_get_fips_county_state, all_counties_nytimes_covid19_data ) ) ) )

cs_fips_dict = dict(map(lambda f_c_s: ( ( f_c_s[1], f_c_s[2] ), f_c_s[0] ), set(
    map(_get_fips_county_state, all_counties_nytimes_covid19_data ))))

#
## from a collection of FIPS, find the clusterings -- which set are adjacent to each other, which aren't
def get_clustering_fips( collection_of_fips ):
    fips_rem = set( collection_of_fips )
    #
    ## our adjacency matrix from this
    subset = set(filter(lambda tup: all(map(lambda tok: tok in fips_rem, tup)), fips_adj_2018 )) | \
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
            
#
## now stuff associated with the fips : county/state mapping
def get_county_state( fips ):
    if fips not in fips_countystate_dict: return None
    return fips_countystate_dict[ fips ]
#
data_msas_2019 = gis.load_msas_data( )
fips_msas_2019 = dict(chain.from_iterable(
    map(lambda entry: map(lambda fips: ( fips, entry['prefix'] ), entry['fips']), 
        data_msas_2019.values( ) ) ) )

def get_fips_msa( county, state ):
    tup = ( county, state )
    assert( tup in cs_fips_dict )
    fips = cs_fips_dict[ tup ]
    msaname = fips_msas_2019[ fips ]
    data_msa = data_msas_2019[ msaname ]
    return ( fips, data_msa )

def get_msa_data( msaname ):
    assert( msaname in data_msas_2019 )
    return data_msas_2019[ msaname ].copy( )

def get_data_county( county_name, state = 'California' ):
  data_by_date = sorted(filter(lambda entry: county_name in entry['county'] and
                               entry['state'] == state, all_counties_nytimes_covid19_data ),
                        key = lambda entry: entry['date'] )
  return data_by_date

def get_incident_data( data = data_msas_2019['bayarea'] ):
    prefix = data[ 'prefix' ]
    regionName = data[ 'region name' ]
    fips_collection = set( data['fips'] )
    counties_and_states = list(map(lambda fips: fips_countystate_dict[ fips ], fips_collection ) )
    #
    ## now this creates a dictionary of incidents and deaths per county (in Bay Area) per date
    all_data_region = sorted( chain.from_iterable(
        map(lambda cs: get_data_county( cs['county'], state = cs['state'] ), counties_and_states ) ),
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
    total_bbox = calculate_total_bbox( fips_collection )
    boundary_dict = get_boundary_dict( fips_collection )
    incident_data = {
        'df' : df_cases_deaths_region, 'bbox' : total_bbox, 'boundaries' : boundary_dict,
        'last day' : df_cases_deaths_region.days_from_beginning.max( ) }
    return incident_data

def calculate_total_bbox( fips_collection ):
    bbox_tot_array = numpy.array(
        list(map(lambda fips: fips_data_2018[ fips ][ 'bbox' ], fips_collection ) ) )
    min_lng = bbox_tot_array[:,0].min( )
    min_lat = bbox_tot_array[:,1].min( )
    max_lng = bbox_tot_array[:,2].max( )
    max_lat = bbox_tot_array[:,3].max( )
    return (min_lng, min_lat, max_lng, max_lat)

def get_boundary_dict( fips_collection ):
    boundary_dict = dict(map(lambda fips: ( fips, fips_data_2018[ fips ][ 'points' ] ), fips_collection ) )
    return boundary_dict

def get_maximum_cases( inc_data ):
    df = inc_data[ 'df' ]
    max_case_tup = max(map(lambda key: (
        key.replace('cases_', '').strip( ),
        df[key].max( ) ), filter(lambda key: key.startswith('cases_'), df ) ),
                       key = lambda tup: tup[1] )
    return max_case_tup

def display_tabulated_metros( form = 'simple' ):
    assert( form in ( 'simple', 'github', 'rst' ) )
    all_metros = sorted(
        data_msas_2019.values( ),
        key = lambda entry: entry['population'])[::-1]

    #
    ## now get incident data for each metro
    incident_data_dict = { }
    with multiprocessing.Pool( processes = multiprocessing.cpu_count( ) ) as pool:
        incident_data_dict = dict(pool.map(
            lambda prefix: ( prefix, get_incident_data( data_msas_2019[ prefix ] ) ),
            data_msas_2019 ) )
    date_last = max(map(lambda inc_data: inc_data['df'].date.max( ), incident_data_dict.values()))
    
    #
    ## secret sauce formatting comma'd integers from https://intellipaat.com/community/2447/how-to-print-number-with-commas-as-thousands-separators
    def _get_string_commas_num( num ):
        return "%s" % f"{num:,d}"

    def _get_row( tup ):
        idx, data_msa = tup
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
        return (
            rank, prefix, regionName, population_s,
            date_first_s, last_day,
            num_cases, num_death )
    
    data_tabulated = list(map(
        _get_row, enumerate(all_metros)))
    print( 'HERE ARE THE %d METRO AREAS, ORDERED BY POPULATION' % len( all_metros ) )
    print( 'DATA AS OF %s.' % date_last.strftime( '%d %B %Y' ) )
    print( '%s\n' % tabulate.tabulate(
        data_tabulated, headers = [
            'RANK', 'IDENTIFIER', 'NAME', 'POPULATION', 'FIRST INC.',
            'NUM DAYS', 'NUM CASES', 'NUM DEATHS' ] ) )
