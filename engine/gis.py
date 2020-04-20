import os, sys, numpy, shapefile, pickle
import gzip, pandas, titlecase, logging
import pathos.multiprocessing as multiprocessing
from collections import Counter
from itertools import chain
from engine import mainDir

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
    sf = shapefile.Reader( os.path.join( 'resources', 'cb_2018_us_county_500k.shp' ) )
    fips_2018_data = dict(map(lambda rec_shape: _get_record_shapefile_astup(
        rec_shape[0], rec_shape[1] ), zip( sf.records(), sf.shapes())))
    pickle.dump( fips_2018_data, gzip.open( os.path.join(
        mainDir, 'resources', 'fips_2018_data.pkl.gz' ), 'wb'))

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

def construct_adjacency( fips_data ):
    with multiprocessing.Pool( processes = multiprocessing.cpu_count( ) ) as pool:
        all_adj = dict(map(lambda fips: ( fips, get_fips_adjacency( fips, fips_data ) ), fips_data ) )
        set_of_adjacents = set(chain.from_iterable(
            map(lambda fips: map(lambda fips2: tuple(sorted([ fips, fips2 ])), all_adj[fips]), all_adj)))
        pickle.dump( set_of_adjacents, gzip.open( os.path.join(
            mainDir, 'resources', 'fips_2018_adj.pkl.gz' ), 'wb' ) )

def load_fips_adj( ):
    assert( os.path.exists( os.path.join( 
        mainDir, 'resources', 'fips_2018_adj.pkl.gz' ) ) )
    return pickle.load( gzip.open( os.path.join(
        mainDir, 'resources', 'fips_2018_adj.pkl.gz' ) ) )

def load_fips_data( ):
    assert( os.path.exists( os.path.join(
        mainDir, 'resources', 'fips_2018_data.pkl.gz' ) ) )
    return pickle.load( gzip.open( os.path.join(
        mainDir, 'resources', 'fips_2018_data.pkl.gz' ) ) )

def create_msa_2019( ):
    df = pandas.read_table( os.path.join(
        mainDir, 'resources', 'msa_2019.csv' ), encoding='latin-1', sep=',')
    df.pop('MDIV')
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

    return sorted(all_data_msas_post, key = lambda entry: entry[ 'pop est 2019' ] )

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

def create_and_store_msas_2019( ):
    from engine.core import get_county_state
    all_data_msas = create_msa_2019( )
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
    pickle.dump( all_data_msas, gzip.open( os.path.join(
        mainDir, 'resources', 'msa_2019.pkl.gz' ), 'wb' ) )
    pickle.dump( all_data_msas_post, gzip.open( os.path.join(
        mainDir, 'resources', 'msa_2019_post.pkl.gz' ), 'wb' ) )
    #
    ## now create a data structure of dictionaries with prefixes
    msas_dict = { }
    for entry in all_data_msas_post:
        prefix = entry[ 'prefix' ]
        regionName = entry[ 'region name' ]
        fips = list(filter(lambda fips: get_county_state( fips ) is not None, entry['fips'] ) )
        #
        ## now put in the entire population
        population = entry[ 'pop est 2019' ]
        msas_dict[ prefix ] = {
            'prefix' : prefix, 'region name' : regionName,
            'fips' : fips,
            'population' : population }
    pickle.dump( msas_dict, gzip.open( os.path.join(
        mainDir, 'resources', 'msa_2019_dict.pkl.gz' ), 'wb' ) )
    
def load_msas_data( ):
    return pickle.load( gzip.open( os.path.join(
        mainDir, 'resources', 'msa_2019_dict.pkl.gz' ), 'rb' ) )
