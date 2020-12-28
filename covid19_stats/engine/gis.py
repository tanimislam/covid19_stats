import os, sys, numpy, shapefile, pickle
import gzip, pandas, titlecase, logging
import pathos.multiprocessing as multiprocessing
from collections import Counter
from itertools import chain
#
from covid19_stats import resourceDir

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

def _get_record_shapefile_astup( rec, shape ):
    fips_code = rec[4]
    num_shapes = int( rec[0] )
    #
    ## now split into parts
    allpoints = numpy.array( shape.points )
    #
    ## include last point
    parts = numpy.concatenate([ shape.parts, [ allpoints.shape[0], ] ] )
    points = [ ]
    for start, end in zip( parts[:-1], parts[1:] ):
        points.append( allpoints[start:end, :] )
    data = { 'bbox' : shape.bbox, 'points' : points }
    return ( fips_code, data )

def create_and_store_fips_2018( ):
    if os.path.isfile( os.path.join(
        resourceDir, 'fips_2018_data.pkl.gz' ) ):
        return pickle.load( gzip.open( os.path.join(
            resourceDir, 'fips_2018_data.pkl.gz' ), 'rb' ) )
    #
    sf = shapefile.Reader( os.path.join( resourceDir, 'cb_2018_us_county_500k.shp' ) )
    fips_2018_data = dict(map(lambda rec_shape: _get_record_shapefile_astup(
        rec_shape[0], rec_shape[1] ), zip( sf.records(), sf.shapes())))
    pickle.dump( fips_2018_data, gzip.open( os.path.join(
        resourceDir, 'fips_2018_data.pkl.gz' ), 'wb'))
    return fips_2018_data

def do_bbox_intersect( bbox1, bbox2 ):
    lng1_min, lat1_min, lng1_max, lat1_max = bbox1
    lng2_min, lat2_min, lng2_max, lat2_max = bbox2
    if lng1_max < lng2_min or lng2_max < lng1_min: return False
    if lat1_max < lat2_min or lat2_max < lat1_min: return False
    return True
        
def get_fips_adjacency( fips, fips_data ):
    assert( fips in fips_data )
    fips_excl = set( fips_data ) - set( [ fips ] )
    possible_fips = set(filter(
        lambda fipsc: do_bbox_intersect( fips_data[ fips ][ 'bbox' ], fips_data[ fipsc ][ 'bbox' ] ), fips_excl))
    all_points_fips = numpy.concatenate( fips_data[ fips ][ 'points' ] )
    set_points_fips_as_tuples = set(map(lambda idx: tuple( all_points_fips[idx,:]), range(all_points_fips.shape[0])))
    actual_adj = [ ]
    for fipsc in possible_fips:
        all_points = numpy.concatenate( fips_data[ fipsc ][ 'points' ] )
        set_points_as_tuples = set(map(lambda idx: tuple( all_points[ idx, : ] ), range(all_points.shape[0])))
        len_inc = len( set_points_as_tuples & set_points_fips_as_tuples )
        if len_inc >= 2:
            logging.debug( '%s,%s: %d points' % ( fips, fipsc, len_inc ) )
            actual_adj.append( fipsc )
    return set( actual_adj )

def construct_adjacency( fips_data, filename = os.path.join(
            resourceDir, 'fips_2018_adj.pkl.gz' ) ):
    if os.path.isfile( filename ):
        return pickle.load( gzip.open( filename, 'rb' ) )
    with multiprocessing.Pool( processes = multiprocessing.cpu_count( ) ) as pool:
        all_adj = dict(map(lambda fips: ( fips, get_fips_adjacency( fips, fips_data ) ), fips_data ) )
        set_of_adjacents = set(chain.from_iterable(
            map(lambda fips: map(lambda fips2: tuple(sorted([ fips, fips2 ])), all_adj[fips]), all_adj)))
        if filename is not None:
            pickle.dump( set_of_adjacents, gzip.open( filename, 'wb' ) )
        return set_of_adjacents

def load_fips_adj( ):
    assert( os.path.exists( os.path.join( 
        resourceDir, 'fips_2018_adj.pkl.gz' ) ) )
    return pickle.load( gzip.open( os.path.join(
        resourceDir, 'fips_2018_adj.pkl.gz' ) ) )

def create_and_store_fips_counties_2019( ):
    if all(map(lambda fname: os.path.isfile(
        os.path.join( resourceDir, fname ) ),
                   ( 'all_2019_fips_cs_dict.pkl.gz', 'all_2019_cs_fips_dict.pkl.gz' ) ) ):
        fips_countystate_dict = pickle.load( gzip.open( os.path.join(
            resourceDir, 'all_2019_fips_cs_dict.pkl.gz' ), 'rb' ) )
        cs_fips_dict = pickle.load( gzip.open( os.path.join(
            resourceDir, 'all_2019_cs_fips_dict.pkl.gz' ), 'rb' ) )
        return fips_countystate_dict, cs_fips_dict
    #
    df = pandas.read_table( os.path.join(
        resourceDir, 'msa_2019.csv' ), encoding='latin-1', sep=',')
    df.pop('MDIV')
    df_fips = df.dropna( subset=['STCOU'] ).reset_index( )
    fips = list(map(lambda val: '%05d' % val, df_fips.STCOU ) )
    states = list(map(lambda val: _abbrev_us_state[ val.split(',')[-1].strip( ) ], df_fips.NAME))
    counties = list(map(lambda val: val.split(',')[0].strip( ), df_fips.NAME))
    fips_countystate_dict = dict(map(lambda f_c_s: ( f_c_s[0], { 'county' : f_c_s[1], 'state' : f_c_s[2] } ),
                                     zip(fips,counties,states)))
    cs_fips_dict = dict(map(lambda f_c_s: ( ( f_c_s[1], f_c_s[2] ), f_c_s[0] ),
                            zip(fips,counties,states)))
    #pickle.dump( fips_countystate_dict, gzip.open( os.path.join(
    #    resourceDir, 'msa_2019_fips_cs_dict.pkl.gz' ), 'wb' ) )
    #pickle.dump( cs_fips_dict, gzip.open( os.path.join(
    #    resourceDir, 'msa_2019_cs_fips_dict.pkl.gz' ), 'wb' ) )
    #
    ## now do the same for those
    df_rem = pandas.read_csv(
        os.path.join( resourceDir, 'all-geocodes-v2018.csv' ),
        encoding='latin-1',sep=',')
    df_rem_county_fips = df_rem[ df_rem[ 'Summary Level' ] == 50 ].reset_index( )
    df_rem_state_fips = df_rem[ df_rem[ 'Summary Level' ] == 40 ].reset_index( )
    df_rem_county_fips.pop( 'index' )
    df_rem_state_fips.pop( 'index' )
    #
    df_rem_county_fips[ 'fips' ] = list(map(
        lambda tup: '%02d%03d' % ( tup[0], tup[1] ),
        zip( df_rem_county_fips[ 'State Code (FIPS)' ],
             df_rem_county_fips[ 'County Code (FIPS)' ] ) ) )
    fips_state_dict = dict(map(
        lambda tup: ( tup[0], tup[1] ),
        zip( df_rem_state_fips[ 'State Code (FIPS)' ],
            df_rem_state_fips[ 'Area Name (including legal/statistical area description)' ] ) ) )
    #
    ## efficient set operations by creating a series
    ## all the county FIPS that are NOT in MSAs
    df_fips_msa = pandas.DataFrame({ 'fips' : list( fips_countystate_dict ) } )
    df_rem_county_fips = df_rem_county_fips[
        df_rem_county_fips.fips.isin( df_fips_msa.fips ) == False ].reset_index( )
    #
    ## now add STATE NAME as key to df_rem_county_fips
    df_rem_county_fips[ 'state' ] = list(map(
        lambda key: fips_state_dict[ key ],
        df_rem_county_fips[ 'State Code (FIPS)' ] ) )
    #
    ## have all data, now create a dictionary from this!
    rem_fips_cs_dict = dict(map(
        lambda tup: ( tup[0], { 'county' : tup[1], 'state' : tup[2] } ),
        zip( df_rem_county_fips[ 'fips' ], df_rem_county_fips[  'Area Name (including legal/statistical area description)' ],
            df_rem_county_fips[ 'state' ] ) ) )
    rem_cs_fips_dict = dict(map(
        lambda tup: ( (  tup[1], tup[2] ), tup[ 0 ] ),
        zip( df_rem_county_fips[ 'fips' ], df_rem_county_fips[  'Area Name (including legal/statistical area description)' ],
            df_rem_county_fips[ 'state' ] ) ) )
    #
    ## now validation
    ## VALID #1: length of both dicts is identical
    assert( len( rem_fips_cs_dict ) == len( rem_cs_fips_dict ) )
    #
    ## VALID #2: NO intersection in keys between rem_fips_dict and fips_countystate_dict
    assert( len( set( rem_cs_fips_dict ) & set( fips_countystate_dict ) ) == 0 )
    #
    ## VALID #3: NO intersection in keys between cs_fips_dict and rem_cs_fips_dict
    assert( len( set( cs_fips_dict ) & set( rem_cs_fips_dict ) ) == 0 )
    #
    ## NOW save to unified dataset
    fips_countystate_dict = dict(chain.from_iterable([ fips_countystate_dict.items( ), rem_fips_cs_dict.items( ) ]) )
    cs_fips_dict = dict(chain.from_iterable([ cs_fips_dict.items( ), rem_cs_fips_dict.items( ) ] ) )
    #
    ## now dump out into ALL
    pickle.dump( fips_countystate_dict,
                gzip.open( os.path.join( resourceDir, 'all_2019_fips_cs_dict.pkl.gz' ), 'wb' ) )
    pickle.dump( cs_fips_dict,
                gzip.open( os.path.join( resourceDir, 'all_2019_cs_fips_dict.pkl.gz' ), 'wb' ) )
    return fips_countystate_dict, cs_fips_dict

def load_fips_counties_data( ):
    assert(all(map(lambda fname: os.path.isfile(
        os.path.join( resourceDir, fname ) ),
                   ( 'all_2019_fips_cs_dict.pkl.gz', 'all_2019_cs_fips_dict.pkl.gz' ) ) ) )
    fips_countystate_dict = pickle.load( gzip.open( os.path.join(
        resourceDir, 'all_2019_fips_cs_dict.pkl.gz' ), 'rb' ) )
    cs_fips_dict = pickle.load( gzip.open( os.path.join(
        resourceDir, 'all_2019_cs_fips_dict.pkl.gz' ), 'rb' ) )
    #
    return fips_countystate_dict, cs_fips_dict

def create_fips_popmap_2019( ):
    if os.path.isfile( os.path.join(
        resourceDir, 'fips_2019_popdict.pkl.gz' ) ):
        return pickle.load( gzip.open( os.path.join(
            resourceDir, 'fips_2019_popdict.pkl.gz' ), 'rb' ) )
    #
    df = pandas.read_table( os.path.join(
        resourceDir, 'msa_2019.csv' ), encoding='latin-1', sep=',')
    df.pop('MDIV')
    #
    ## now this is gives info on ALL populations in counties that we find
    df_fips_pops = df.dropna( subset=['STCOU'] ).reset_index( )
    df_fips_pops.STCOU = list(map(lambda val: '%05d' % val, df_fips_pops.STCOU))
    fips_pop_dict = dict(zip( df_fips_pops.STCOU, df_fips_pops.POPESTIMATE2019 ) )
    pickle.dump( fips_pop_dict, gzip.open( os.path.join(
        resourceDir, 'fips_2019_popdict.pkl.gz' ), 'wb' ) )
    return fips_pop_dict

def load_fips_popmap_2019( ):
    return pickle.load( gzip.open( os.path.join(
        resourceDir, 'fips_2019_popdict.pkl.gz' ), 'rb' ) )
    
def create_msa_2019( ):
    if os.path.isfile( os.path.join(
        resourceDir, 'msa_2019.pkl.gz' ) ):
        return pickle.load( gzip.open( os.path.join(
            resourceDir, 'msa_2019.pkl.gz' ), 'rb' ) )
    #
    df = pandas.read_table( os.path.join(
        resourceDir, 'msa_2019.csv' ), encoding='latin-1', sep=',')
    df.pop('MDIV')
    #
    ## now fips with county and state
    df_fips = df.dropna( subset=['STCOU'] ).reset_index( )
    fips = list(map(lambda val: '%05d' % val, df_fips.STCOU ) )
    states = list(map(lambda val: _abbrev_us_state[ val.split(',')[-1].strip( ) ], df_fips.NAME))
    counties = list(map(lambda val: val.split(',')[0].strip( ), df_fips.NAME))
    fips_countystate_dict = dict(map(lambda f_c_s: ( f_c_s[0], { 'county' : f_c_s[1], 'state' : f_c_s[2] } ),
                                     zip(fips,counties,states)))
    cs_fips_dict = dict(map(lambda f_c_s: ( ( f_c_s[1], f_c_s[2] ), f_c_s[0] ),
                            zip(fips,counties,states)))
    #
    ## now get the CBSA's which are actual MSIDs
    def _is_actual_msa( cbsa ):
        df_sub = df[ df.CBSA == cbsa ].reset_index( )
        name = titlecase.titlecase( df_sub[ 'LSAD' ][ 0 ] )
        return name == 'Metropolitan Statistical Area'
    all_msas = set(filter(_is_actual_msa, set(df.CBSA)))
    #
    ## now get all the info on the MSA
    def get_info_msa( msa ):
        data_msa = { 'msa' : msa }
        df_sub = df[ df.CBSA == msa ].reset_index( )
        #
        ## 2019 population estimate
        popest_2019 = df_sub.POPESTIMATE2019.max( )
        data_msa[ 'pop est 2019' ] = popest_2019
        #
        ## secret saucing that came from https://stackoverflow.com/questions/22551403/python-pandas-filtering-out-nan-from-a-data-selection-of-a-column-of-strings
        fips_inside = set(
            map(lambda val: '%05d' % val, df_sub.dropna( subset=['STCOU'] ).reset_index( ).STCOU ) )
        name = df_sub.NAME[0].strip( )
        #
        ## now perform 
        data_msa[ 'fips' ] = fips_inside
        #
        state = ''
        if len( name.split(',') ) != 1: state = name.split(',')[-1].strip( )
        data_msa[ 'state' ] = state
        regionName = name.split(',')[0].strip().split('-')[0].strip()
        prefix = ''.join(regionName.split()).lower( ).replace('.','').split('/')[0].strip()
        data_msa[ 'RNAME' ] = regionName
        data_msa[ 'prefix' ] = prefix
        regionName = '%s Metro Area' % regionName
        data_msa[ 'region name' ] = regionName
        #
        return data_msa
    all_data_msas_pre = list(filter(None, map(get_info_msa, all_msas)) )
    #
    ## now find all the msas that have the same RNAME
    cnt = Counter(list(map(lambda entry: entry['RNAME'], all_data_msas_pre)))
    msas_to_check = set(filter(lambda rname: cnt[rname] > 1, cnt ))
    all_data_msas_post = list(filter(lambda entry: entry['RNAME'] != msas_to_check, all_data_msas_pre))
    for msa in msas_to_check:
        #
        ## don't rename the largest metro area
        msas_here = sorted(filter(lambda entry: entry['RNAME'] == msa, all_data_msas_pre ),
                           key = lambda entry: entry[ 'pop est 2019' ] )[::-1]
        all_data_msas_post.append( msas_here[0] )
        for data_msa in msas_here[1:]:
            data_msa[ 'RNAME' ] = '%s %s' % ( data_msa[ 'RNAME' ], data_msa[ 'state' ] )
            data_msa[ 'region name' ] = '%s Metro Area' % data_msa[ 'RNAME' ]
            data_msa[ 'prefix' ] = '_'.join( data_msa[ 'RNAME' ].split()).lower( )
            all_data_msas_post.append( data_msa )
    all_data_msas = sorted(all_data_msas_post, key = lambda entry: entry[ 'pop est 2019' ] )
    pickle.dump( all_data_msas, gzip.open( os.path.join(
        resourceDir, 'msa_2019.pkl.gz' ), 'wb' ) )
    return all_data_msas

def merge_msas( regionName, prefix, msaids, all_data_msas ):
    all_msaids = set( map(lambda entry: entry['msa'],
                          filter(lambda entry: 'status' not in entry, all_data_msas)))
    assert( len( set( msaids ) - set( all_msaids ) ) == 0 )
    assert( len( set( msaids ) ) == len( msaids ) )
    #
    ## now merge these regions
    all_data_msas_post = list(filter(lambda entry: entry['msa'] not in msaids,
                                     all_data_msas.copy( ) ) )
    #
    ## use the msa of the largest pop one
    #
    ## first sort
    data_msas_here = sorted(filter(lambda entry: entry['msa'] in msaids, all_data_msas ),
                            key = lambda entry: entry[ 'pop est 2019' ] )[::-1]
    #
    ## now perform appropriate merging
    data_msa_merge = data_msas_here[0]
    data_msa_merge[ 'pop est 2019' ] = sum(map(lambda entry: entry[ 'pop est 2019' ], data_msas_here))
    data_msa_merge[ 'fips' ] = set(chain.from_iterable(map(lambda entry: list(entry['fips']), data_msas_here )))
    data_msa_merge[ 'RNAME' ] = regionName
    data_msa_merge[ 'status' ] = 'MERGED'
    data_msa_merge[ 'region name' ] = regionName
    data_msa_merge[ 'prefix' ] = prefix
    data_msa_merge[ 'state' ] = '-'.join(sorted(set(map(lambda entry: entry['state'], data_msas_here))))
    all_data_msas_post.append( data_msa_merge )
    return sorted( all_data_msas_post, key = lambda entry: entry[ 'pop est 2019' ] )

def create_and_store_msas_and_fips_2019( ):
    if os.path.isfile( os.path.join( resourceDir, 'msa_2019_dict.pkl.gz' ) ):
        return pickle.load( gzip.open( os.path.join(
            resourceDir, 'msa_2019_dict.pkl.gz' ), 'rb' ) )
    #
    from engine.core import get_county_state
    all_data_msas = create_msa_2019( )
    logging.info( 'NYC fips: %s (%d).' % ( sorted( all_data_msas[-1]['fips'] ), len( all_data_msas[-1]['fips'] ) ) )
    if os.path.isfile( os.path.join( resourceDir, 'msa_2019_post.pkl.gz' ) ):
        all_data_msas_post = pickle.load( gzip.open( os.path.join( resourceDir, 'msa_2019_post.pkl.gz' ), 'rb' ) )
    else:
        #
        ## SF, San Jose, Napa MSAs -> Bay Area
        all_data_msas_post = merge_msas( 'Bay Area', 'bayarea', { 41860, 41940, 34900 }, all_data_msas )
        #
        ## New York to NYC
        all_data_msas_post = merge_msas( 'NYC Metro Area', 'nyc', { 35620 }, all_data_msas_post )
        #
        ## Washington to DC
        all_data_msas_post = merge_msas( 'DC Metro Area', 'dc', { 47900 }, all_data_msas_post )
        #
        ## Los Angeles, Riverside, Oxnard -> Los Angeles
        ## from wikipedia entry: https://en.wikipedia.org/wiki/Greater_Los_Angeles
        all_data_msas_post = merge_msas( 'LA Metro Area', 'losangeles', { 31080, 40140, 37100 }, all_data_msas_post )
        #
        ## now dump out
        pickle.dump( all_data_msas_post, gzip.open( os.path.join(
            resourceDir, 'msa_2019_post.pkl.gz' ), 'wb' ) )
    #
    ## now create a data structure of dictionaries with prefixes
    msas_dict = { }
    for entry in all_data_msas_post:
        prefix = entry[ 'prefix' ]
        regionName = entry[ 'region name' ]
        fips = entry[ 'fips' ].copy( )
        #
        ## now put in the entire population
        population = entry[ 'pop est 2019' ]
        msas_dict[ prefix ] = {
            'prefix' : prefix, 'region name' : regionName,
            'fips' : fips,
            'population' : population }
    logging.info( 'NYC fips: %s (%d).' % ( sorted( msas_dict['nyc']['fips'] ), len( msas_dict['nyc']['fips'] ) ) )
    pickle.dump( msas_dict, gzip.open( os.path.join(
        resourceDir, 'msa_2019_dict.pkl.gz' ), 'wb' ) )
    return msas_dict            
    
def load_msas_data( ):
    return pickle.load( gzip.open( os.path.join(
        resourceDir, 'msa_2019_dict.pkl.gz' ), 'rb' ) )
