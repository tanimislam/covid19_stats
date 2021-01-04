import os, sys, numpy, mutagen.mp4, datetime, json, requests
from itertools import chain
from covid19_stats.engine import core

def _find_valid_png_files( init_png_files, prefixes = [ 'cds', 'cases', 'death' ] ):
    assert(all(map(os.path.isfile, init_png_files)))
    assert( len(list(map(os.path.basename, init_png_files))) ==
           len(set(map(os.path.basename, init_png_files))))
    def _is_valid_png_file( fname ):
        bname = os.path.basename( fname )
        if not bname.startswith( 'covid19_' ): return False
        if not bname.endswith( '_LATEST.png' ): return False
        if not any(map(lambda pfx: '_%s_' % pfx in bname, prefixes)): return False
        return True
    valid_png_files = set(filter(_is_valid_png_file, init_png_files))
    return valid_png_files

def _find_valid_mp4_files( init_mp4_files ):
    assert(all(map(os.path.isfile, init_mp4_files)))
    assert(len(list(map(os.path.basename, init_mp4_files))) ==
           len(set(map(os.path.basename, init_mp4_files))))
    def _is_valid_mp4_file( fname ):
        bname = os.path.basename( fname )
        if not bname.startswith( 'covid19_' ): return False
        if not bname.endswith( '_LATEST.mp4' ): return False
        return True
    valid_mp4_files = set(filter(_is_valid_mp4_file, init_mp4_files))
    return valid_mp4_files

def _get_status_mp4_file( mp4_file ):
    mp4tags = mutagen.mp4.MP4( mp4_file )
    region, display_type, date_s = map(lambda tok: tok.strip(), mp4tags[ '\xa9nam' ][ 0 ].split(','))
    date_p = datetime.datetime.strptime( date_s, '%d-%m-%Y' ).date( )
    region_type = mp4tags[ '\xa9alb' ][ 0 ]
    date_pub = datetime.datetime.strptime( mp4tags[ '\xa9day' ][ 0 ], '%d-%m-%Y' ).date( )
    assert( date_pub == date_p )
    return { 'region' : region, 'display type' : display_type, 'region type' : region_type,
            'date published' : date_p }

def _get_status_png_file( png_file ):
    bname = os.path.basename( png_file )
    bname_strip = bname.replace('.png', '' ).strip( )
    region = bname_strip.split('_')[1].strip( )
    display_dict = { 'cases' : 'CASES', 'death' : 'DEATHS', 'cds' : 'ALL' }
    display_key = bname_strip.split('_')[2].strip( ).lower( )
    assert( display_key in display_dict )
    return { 'region' : region, 'display type' : display_dict[ display_key ] }

def _get_dictionary_init( init_mp4_files ):
    valid_mp4_files = _find_valid_mp4_files( init_mp4_files )
    alldict_mp4_files = dict(map(lambda fname: ( fname, _get_status_mp4_file( fname ) ), valid_mp4_files ) )
    #
    ## now check that the fields do not clobber each other
    list_of_mp4_statuses = list(map(lambda entry: tuple(sorted(entry.items(), key = lambda tup: tup[0])), alldict_mp4_files.values()))
    set_of_mp4_statuses = set(map(lambda entry: tuple(sorted(entry.items(), key = lambda tup: tup[0])), alldict_mp4_files.values()))
    assert( len( list_of_mp4_statuses ) == len( set_of_mp4_statuses ) )
    #
    ## check that ALL dates are equal to each other
    alldates = set(map(lambda entry: entry[ 'date published' ], alldict_mp4_files.values()))
    assert( len(alldates ) == 1 )
    #
    ## now fill out the tree
    data_dict = { 'date published' : min(alldates), 'filemap' : { } }
    for fname in alldict_mp4_files:
        entry = alldict_mp4_files[ fname ]
        region_type = entry[ 'region type' ]
        if region_type not in data_dict:
            data_dict.setdefault( region_type, { } )
        region = entry[ 'region' ]
        if region not in data_dict[ region_type ]:
            data_dict[ region_type ].setdefault( region, { } )
        display_type = entry[ 'display type' ]
        if display_type not in data_dict[ region_type ][ region ]:
            data_dict[ region_type ][ region ][ display_type ] = { 'mp4' : os.path.basename( fname ) }
            data_dict[ 'filemap' ][ os.path.basename( fname ) ] = fname
    return data_dict

def _add_dictionary_pngs( data_dict, init_png_files ):
    valid_png_files = _find_valid_png_files( init_png_files )
    alldict_png_files = dict(map(lambda fname: ( fname, _get_status_png_file( fname ) ), valid_png_files ) )
    data_dict_new = data_dict.copy( )
    region_type_dict = dict(chain.from_iterable(map(lambda region_type:
                                                    map(lambda region: ( region, region_type ), data_dict[ region_type ] ),
                                                    set(data_dict) - set([ 'date published', 'filemap' ]) ) ) )
    #
    ## these PNG files regions MUST match those of the MP4 files
    assert(set( region_type_dict ) == set(map(lambda entry: entry[ 'region' ], alldict_png_files.values())))
    for fname in alldict_png_files:
        region = alldict_png_files[ fname ][ 'region' ]
        display_type = alldict_png_files[ fname ][ 'display type' ]
        region_type = region_type_dict[ region ]
        #
        ## PNG display type MUST be in original (MP4-populated) data_dict
        assert( display_type in data_dict_new[ region_type ][ region ] )
        data_dict_new[ region_type ][ region ][ display_type ][ 'png' ] = os.path.basename( fname )
        data_dict_new[ 'filemap' ][ os.path.basename( fname ) ] = fname
    return data_dict_new

def _add_dictionary_summary_json( data_dict, summary_json_file ):
    assert( os.path.basename( summary_json_file ) == 'covid19_topN_LATEST.json' )
    summary_json_data = json.load( open( summary_json_file, 'r' ) )
    topN = max(summary_json_data, key = lambda entry: entry['RANK'] )[ 'RANK' ]
    data_dict_new = data_dict.copy( )
    data_dict_new[ 'summary data' ] = summary_json_data
    data_dict_new[ 'topN' ] = topN
    return data_dict_new

def create_pushing_dictionary( init_mp4_files, init_png_files, summary_json_file ):
    data_dict = _get_dictionary_init( init_mp4_files )
    data_dict = _add_dictionary_pngs( data_dict, init_png_files )
    data_dict = _add_dictionary_summary_json( data_dict, summary_json_file )
    return data_dict

def post_to_server( covid19_restful_endpoint, data_dict, user_email, password, verify = True ):
    json_data_here = data_dict.copy( )
    filename_list = sorted( data_dict[ 'filemap' ].items( ), key = lambda tup: tup[0] )
    json_data_here.pop( 'filemap' )
    #
    ## now check with server, endpoint must accept GET verb
    response = requests.get( covid19_restful_endpoint, auth = ( user_email, password ), verify = verify )
    if response.status_code != 200: # failure mode
        return "ERROR, passing useremail=%s, password=XXXXX to %s with VERIFY=%s DID NOT WORK." % (
            user_email, covid19_restful_endpoint, verify )
    #
    ## now if it works, POST the content
    big_ass_response = requests.post(
        covid19_restful_endpoint, auth = ( user_email, password ), verify = verify,
        '???' ) # FIXME
