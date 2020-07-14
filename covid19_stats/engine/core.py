import os, sys, numpy, glob, tabulate, logging
import datetime, pandas, titlecase, networkx
import pathos.multiprocessing as multiprocessing
from itertools import chain
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
#
from covid19_stats import resourceDir, covid19ResDir
from covid19_stats.engine import gis

def _get_stat_line( line ):
    line_split = list(map(lambda tok: tok.strip(), line.split(',')))
    dstring = line_split[0]
    county_name = line_split[1].strip( )
    state_name = line_split[2].strip( )
    fips = line_split[-3].strip( )
    #
    ## NYC IS SPECIAL!!!
    if county_name == 'New York City': fips = '00001'
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

all_counties_nytimes_covid19_data = list(filter(None,
    map(_get_stat_line,
        list( map(lambda line: line.strip(), filter(
            lambda line: len( line.strip( ) ) != 0,
    open( os.path.join( covid19ResDir, "us-counties.csv" ), "r" ).readlines())))[1:])))


#
## FIPS data for county shapes 2018
fips_data_2018 = gis.load_fips_data( )

def get_boundary_dict( fips_collection ):
    boundary_dict = dict(map(lambda fips: (
        fips, fips_data_2018[ fips ][ 'points' ] ), fips_collection ) )
    return boundary_dict


def calculate_total_bbox( shapes ):
    def _get_bbox( shp ):
        lng_min = shp[:,0].min( )
        lng_max = shp[:,0].max( )
        lat_min = shp[:,1].min( )
        lat_max = shp[:,1].max( )
        return lng_min, lat_min, lng_max, lat_max
    bbox_shapes = numpy.array(list(map(_get_bbox, shapes)))
    lng_min = bbox_shapes[:,0].min( )
    lat_min = bbox_shapes[:,1].min( )
    lng_max = bbox_shapes[:,2].max( )
    lat_max = bbox_shapes[:,3].max( )
    return lng_min, lat_min, lng_max, lat_max

#
## now population data for fips found from MSAs
fips_popdict_2019 = gis.load_fips_popmap_2019( )

#
## create a custom FIPS dataset for NYC alone, FIPS #00001
def create_nyc_custom_fips( bdict ):
    from shapely.geometry import Polygon, MultiPolygon
    from shapely.ops import unary_union
    def _create_poly( shape ):
        lngs = shape[:,0]
        lats = shape[:,1]
        p = Polygon( list(zip( lngs, lats ) ) )
        return p
    
    #
    ## these are the FIPS for the FIVE NYC BOROUGHS
    #fips_five_boroughs = fips_missing_2019 & data_nyc['fips']
    #
    ## first get a boundary dict: fips -> points
    #bdict = get_boundary_dict( fips_five_boroughs )
    #
    ## second, construct a list of all the Polygons corresponding to these boroughs
    all_polys = list(map(_create_poly, chain.from_iterable( bdict.values( ) ) ) )
    #
    ## third, make a collection of MultiPolygon from the unary_union of these Polygons
    newpolys = unary_union( MultiPolygon( all_polys ) )
    #
    ## fourth, get the new shapes, ordered by area from smallest to largest
    newshapes = list(map(lambda poly: numpy.array( poly.exterior.coords.xy ).T, # take a Polygon, convert it into shape format we understand
        sorted( newpolys.geoms, key = lambda poly: poly.area )[::-1] # sort by maximum to minimum area
        ) )
    #
    ## fifth (and finally), return this new FIPS data structure: { 'bbox' : bbox, 'points' : list-of-shapes }
    ## FIPS # is 00001
    bbox = calculate_total_bbox( newshapes ) # bbox
    geom_nyc = { 'bbox' : bbox, 'points' : newshapes }
    return geom_nyc

#
## FIPS data for county adjacency 2018
fips_adj_2018 = gis.load_fips_adj( )

#
## CENSUS dictionary of FIPS to COUNTY/STATE
fips_countystate_dict, cs_fips_dict = gis.load_fips_counties_data( )
#
data_msas_2019 = gis.load_msas_data( )
fips_msas_2019 = dict(chain.from_iterable(
    map(lambda entry: map(lambda fips: ( fips, entry['prefix'] ), entry['fips']), 
        data_msas_2019.values( ) ) ) )
#
## these are the FIPS missing, highlighting NYC
## include FIPS = 00001 EXCEPT for fips_adj_2018
## SHOULD WE ALSO DELETE THE FIVE BOROUGHS FIPS??
_fips_missing_2019 = set( fips_msas_2019 ) - set(
    map(lambda entry: entry['fips'], all_counties_nytimes_covid19_data ) )
_fips_five_boroughs = _fips_missing_2019 & data_msas_2019['nyc']['fips']
#
nyc_fips = '00001'
fips_data_2018[ nyc_fips ] = create_nyc_custom_fips(
    get_boundary_dict( _fips_five_boroughs ) )
## DELETE
for fips in _fips_five_boroughs: fips_data_2018.pop( fips )
#
fips_countystate_dict[ nyc_fips ] = { 'county' : 'New York City', 'state' : 'New York' }
#
cs_fips_dict[ ( 'New York City', 'New York' ) ] = nyc_fips
## DELETE FIRST THEN SECOND
for cs_found in map(lambda fips: fips_countystate_dict[ fips ], _fips_five_boroughs ):
    tup = ( cs_found[ 'county' ], cs_found[ 'state' ] )
    cs_fips_dict.pop( tup )
for fips in _fips_five_boroughs: fips_countystate_dict.pop( fips )
#
## AND DELETE??
oldfips = data_msas_2019[ 'nyc' ][ 'fips' ].copy( )
data_msas_2019[ 'nyc' ][ 'fips' ] = set(list( oldfips ) + [ nyc_fips ] ) - _fips_five_boroughs
#
fips_msas_2019[ nyc_fips ] = 'nyc'
## DELETE
for fips in _fips_five_boroughs: fips_msas_2019.pop( fips )

#
## now do the same thing for the five boroughs
## remove data for 5 boroughs, replace with fake NYC FIPS
_fips_popdict_remove = set( _fips_five_boroughs ) & set( fips_popdict_2019 )
logging.debug( 'REMOVING THESE FIPS: %s.' % _fips_popdict_remove )
_pop_five_boroughs = sum(map(lambda fips: fips_popdict_2019[ fips ],
                             _fips_popdict_remove ) )
for fips in _fips_popdict_remove:
    if fips in fips_popdict_2019: fips_popdict_2019.pop( fips )
fips_popdict_2019[ nyc_fips ] = _pop_five_boroughs

#
## now data by states and by CONUS (continental US)
## will refactor so that later on it will live in engine.gis
## however, because right now because of NYC definition,
## and violence done to LOTS of GIS data, move it here AFTER violence
_conus_states = set( map(lambda elem: elem['state'], fips_countystate_dict.values( ) ) ) - set([
    'Alaska', 'Hawaii', 'Puerto Rico' ] )
data_conus = {
    'RNAME' : 'CONUS',
    'region name' : 'CONUS',
    'prefix' : 'conus',
    'fips' : list(filter(lambda fips: fips_countystate_dict[ fips ][ 'state' ] in 
                         _conus_states, fips_countystate_dict)) }
data_conus['population'] = sum(list(map(
    lambda fips: fips_popdict_2019[fips],
    set( fips_popdict_2019 ) & set( data_conus['fips'] ) ) ) )
#
## now do data for all states
data_states = { '_'.join( state.lower( ).split()) : {
    'RNAME' : state,
    'region name' : state,
    'prefix' : '_'.join( state.lower().split()),
    'fips' : list(filter(lambda fips: fips_countystate_dict[ fips ][ 'state' ] == state,
                         fips_countystate_dict)) } for
               state in _conus_states }
for prefix in sorted(data_states):
    data_states[ prefix ][ 'population' ] = sum(list(map(
        lambda fips: fips_popdict_2019[ fips ],
        set( fips_popdict_2019 ) & set( data_states[ prefix ][ 'fips' ] ) ) ) )
mapping_state_rname_conus = dict(map(lambda rname: (
    data_states[ rname ][ 'region name' ], rname ), data_states ) )
    
#
## data for non-CONUS states and territories
data_nonconus_states_territories = {
    '_'.join( state.lower( ).split()) : {
        'RNAME' : state,
        'region name' : state,
        'prefix' : '_'.join( state.lower().split()),
        'fips' : list(filter(lambda fips: fips_countystate_dict[ fips ][ 'state' ] == state,
                            fips_countystate_dict)) } for
    state in ( 'Alaska', 'Hawaii', 'Puerto Rico' ) }
for prefix in sorted(data_nonconus_states_territories):
    data_nonconus_states_territories[
        prefix ][ 'population' ] = sum(
            list(map(lambda fips: fips_popdict_2019[ fips ],
                     set( fips_popdict_2019 ) &
                     set( data_nonconus_states_territories[ prefix ][ 'fips' ] ) ) ) )
mapping_state_rname_nonconus = dict(
    map(lambda rname: ( data_nonconus_states_territories[ rname ][ 'region name' ], rname ),
        data_nonconus_states_territories ) )
                                        
                                    

#
## now stuff associated with the fips : county/state mapping
def get_county_state( fips ):
    if fips not in fips_countystate_dict: return None
    return fips_countystate_dict[ fips ]

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

def get_data_fips( fips ):
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

def get_incident_data( data = data_msas_2019['bayarea'] ):
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
    total_bbox = calculate_total_bbox( chain.from_iterable(
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

def display_tabulated_metros( form = 'simple', selected_metros = None ):
    assert( form in ( 'simple', 'github', 'rst' ) )
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
        max_case_data= get_max_cases_county( inc_data )
        max_case_co  = max_case_data[ 'cases' ]
        max_case_co_county = max_case_data[ 'county' ]
        max_case_co_state  = max_case_data[ 'state'  ]
        return (
          rank, prefix, regionName, population_s,
          date_first_s, last_day,
          _get_string_commas_num(num_cases),
          _get_string_commas_num(num_death),
          _get_string_commas_num(max_case_co),
          '%s, %s' % ( max_case_co_county, max_case_co_state ) )
    
    data_tabulated = list(map(
        _get_row, enumerate(all_metros)))
    print( 'HERE ARE THE %d METRO AREAS, ORDERED BY POPULATION' % len( all_metros ) )
    print( 'DATA AS OF %s.' % date_last.strftime( '%d %B %Y' ) )
    print( '%s\n' % tabulate.tabulate(
        data_tabulated, headers = [
            'RANK', 'IDENTIFIER', 'NAME', 'POPULATION', 'FIRST INC.',
            'NUM DAYS', 'NUM CASES', 'NUM DEATHS', 'MAX CASE COUNTY', 'MAX CASE COUNTY NAME'  ],
      tablefmt = form, stralign = 'left' ) )

#
## from a collection of FIPS, find the clusterings -- which set are adjacent to each other, which aren't
def get_clustering_fips( collection_of_fips, adj = fips_adj_2018 ):
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
