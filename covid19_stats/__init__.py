__author__ = 'Tanim Islam'
__email__ = 'tanim.islam@gmail.com'

import sys, os, logging, datetime, numpy
from itertools import chain

_mainDir = os.path.dirname( os.path.abspath( __file__ ) )
#
## resources directory and covid-19 git submodule 
resourceDir = os.path.join( _mainDir, 'resources' )
covid19ResDir = os.path.join( _mainDir, 'covid-19-data' )
#
## must both exist
assert(all(map(lambda dirname: os.path.isdir( dirname ), ( resourceDir, covid19ResDir ) ) ) )

from covid19_stats.engine import gis

class COVID19Database( object ):
    """
    This class implements a Singleton_ with static access methods to US GIS data and COVID-19 data.

    .. _Singleton: https://en.wikipedia.org/wiki/Singleton_pattern
    """

    class __COVID19Database( object ):

        def get_stat_line( self, line ):
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
            try: death_cumulative = int( line_split[-1] )
            except: death_cumulative = 0
            return {
                'date' : datetime.datetime.strptime(
                    dstring, '%Y-%m-%d' ).date( ),
                'county' : county_name,
                'state' : state_name,
                'fips' : fips,
                'cumulative cases' : cases_cumulative,
                'cumulative death' : death_cumulative }

        def create_nyc_custom_fips( self, bdict ):
            """
            create a custom FIPS dataset for NYC alone, FIPS #00001
            """
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
            bbox = gis.calculate_total_bbox( newshapes ) # bbox
            geom_nyc = { 'bbox' : bbox, 'points' : newshapes }
            return geom_nyc
        
        def __init__( self ):

            #
            ## all COVID-19 data
            self.all_counties_nytimes_covid19_data = list(
                filter(None,
                       map(self.get_stat_line,
                           list(
                               map(lambda line: line.strip(), filter(
                                lambda line: len( line.strip( ) ) != 0,
                                open( os.path.join( covid19ResDir, "us-counties.csv" ), "r" ).readlines())))[1:])))
    
            #
            ## FIPS data for county shapes 2018
            self.fips_data_2018 = gis.create_and_store_fips_2018( )
            
            #
            ## now population data for fips found from MSAs
            self.fips_popdict_2019 = gis.create_fips_popmap_2019( )
            
            #
            ## FIPS data for county adjacency 2018
            self.fips_adj_2018 = gis.construct_adjacency( self.fips_data_2018 )
            
            #
            ## CENSUS dictionary of FIPS to COUNTY/STATE
            self.fips_countystate_dict, self.cs_fips_dict = gis.create_and_store_fips_counties_2019( )
            self.data_msas_2019 = gis.create_and_store_msas_and_fips_2019( )
            self.fips_msas_2019 = dict(chain.from_iterable(
                map(lambda entry: map(lambda fips: ( fips, entry['prefix'] ), entry['fips']), 
                    self.data_msas_2019.values( ) ) ) )

            #
            ## these are the FIPS missing, highlighting NYC
            ## include FIPS = 00001 EXCEPT for fips_adj_2018
            ## SHOULD WE ALSO DELETE THE FIVE BOROUGHS FIPS??
            def _get_boundary_dict( fips_collection ):
                boundary_dict = dict(map(lambda fips: (
                    fips, self.fips_data_2018[ fips ][ 'points' ] ), fips_collection ) )
                return boundary_dict
                
            _fips_missing_2019 = set( self.fips_msas_2019 ) - set(
                map(lambda entry: entry['fips'], self.all_counties_nytimes_covid19_data ) )
            _fips_five_boroughs = _fips_missing_2019 & self.data_msas_2019['nyc']['fips']
            #
            nyc_fips = '00001'
            self.fips_data_2018[ nyc_fips ] = self.create_nyc_custom_fips(
                _get_boundary_dict( _fips_five_boroughs ) )
            ## DELETE
            for fips in _fips_five_boroughs: self.fips_data_2018.pop( fips )
            #
            self.fips_countystate_dict[ nyc_fips ] = { 'county' : 'New York City', 'state' : 'New York' }
            #
            self.cs_fips_dict[ ( 'New York City', 'New York' ) ] = nyc_fips
            ## DELETE FIRST THEN SECOND
            for cs_found in map(lambda fips: self.fips_countystate_dict[ fips ], _fips_five_boroughs ):
                tup = ( cs_found[ 'county' ], cs_found[ 'state' ] )
                self.cs_fips_dict.pop( tup )
            for fips in _fips_five_boroughs: self.fips_countystate_dict.pop( fips )
            #
            ## AND DELETE??
            oldfips = self.data_msas_2019[ 'nyc' ][ 'fips' ].copy( )
            self.data_msas_2019[ 'nyc' ][ 'fips' ] = set(list( oldfips ) + [ nyc_fips ] ) - _fips_five_boroughs
            #
            self.fips_msas_2019[ nyc_fips ] = 'nyc'
            ## DELETE
            for fips in _fips_five_boroughs: self.fips_msas_2019.pop( fips )

            #
            ## now do the same thing for the five boroughs
            ## remove data for 5 boroughs, replace with fake NYC FIPS
            _fips_popdict_remove = set( _fips_five_boroughs ) & set( self.fips_popdict_2019 )
            logging.debug( 'REMOVING THESE FIPS: %s.' % _fips_popdict_remove )
            _pop_five_boroughs = sum(map(lambda fips: self.fips_popdict_2019[ fips ],
                                         _fips_popdict_remove ) )
            for fips in _fips_popdict_remove:
                if fips in self.fips_popdict_2019: self.fips_popdict_2019.pop( fips )
            self.fips_popdict_2019[ nyc_fips ] = _pop_five_boroughs
            
            #
            ## now data by states and by CONUS (continental US)
            ## will refactor so that later on it will live in engine.gis
            ## however, because right now because of NYC definition,
            ## and violence done to LOTS of GIS data, move it here AFTER violence
            _conus_states = set( map(lambda elem: elem['state'], self.fips_countystate_dict.values( ) ) ) - set([
                'Alaska', 'Hawaii', 'Puerto Rico' ] )
            self.data_conus = {
                'RNAME' : 'CONUS',
                'region name' : 'CONUS',
                'prefix' : 'conus',
                'fips' : list(filter(lambda fips: self.fips_countystate_dict[ fips ][ 'state' ] in 
                                     _conus_states, self.fips_countystate_dict)) }
            self.data_conus['population'] = sum(list(map(
                lambda fips: self.fips_popdict_2019[fips],
                set( self.fips_popdict_2019 ) & set( self.data_conus['fips'] ) ) ) )
            #
            ## now do data for all states
            self.data_states = dict(map(lambda state: (
                '_'.join( state.lower( ).split()), {
                    'RNAME' : state,
                    'region name' : state,
                    'prefix' : '_'.join( state.lower().split()),
                    'fips' : list(filter(lambda fips: self.fips_countystate_dict[ fips ][ 'state' ] == state,
                                         self.fips_countystate_dict)) } ), _conus_states ) )
            for prefix in sorted( self.data_states ):
                self.data_states[ prefix ][ 'population' ] = sum(list(map(
                    lambda fips: self.fips_popdict_2019[ fips ],
                    set( self.fips_popdict_2019 ) & set( self.data_states[ prefix ][ 'fips' ] ) ) ) )
            self.mapping_state_rname_conus = dict(map(lambda rname: (
                self.data_states[ rname ][ 'region name' ], rname ), self.data_states ) )

            #
            ## data for non-CONUS states and territories
            self.data_nonconus_states_territories = dict(
                map(lambda state:
                    ( '_'.join( state.lower( ).split()), {
                    'RNAME' : state,
                    'region name' : state,
                    'prefix' : '_'.join( state.lower().split()),
                        'fips' : list(filter(lambda fips: self.fips_countystate_dict[ fips ][ 'state' ] == state,
                                             self.fips_countystate_dict)) } ),
                    ( 'Alaska', 'Hawaii', 'Puerto Rico' ) ) )
            for prefix in sorted( self.data_nonconus_states_territories ):
                self.data_nonconus_states_territories[ prefix ][ 'population' ] = sum(
                    list(map(lambda fips: self.fips_popdict_2019[ fips ],
                             set( self.fips_popdict_2019 ) &
                             set( self.data_nonconus_states_territories[ prefix ][ 'fips' ] ) ) ) )
            self.mapping_state_rname_nonconus = dict(
                map(lambda rname: ( self.data_nonconus_states_territories[ rname ][ 'region name' ], rname ),
                    self.data_nonconus_states_territories ) )

    #
    ## hidden singleton instance
    __instance = None

    @classmethod
    def _getInstance( cls ):
        if COVID19Database.__instance == None:
            COVID19Database.__instance = COVID19Database.__COVID19Database( )
        return COVID19Database.__instance

    @classmethod
    def fips_data_2018( cls ):
        inst = COVID19Database._getInstance( )
        return inst.fips_data_2018

    @classmethod
    def fips_adj_2018( cls ):
        inst = COVID19Database._getInstance( )
        return inst.fips_adj_2018

    @classmethod
    def fips_countystate_dict( cls ):
        inst = COVID19Database._getInstance( )
        return inst.fips_countystate_dict

    @classmethod
    def fips_msas_2019( cls ):
        inst = COVID19Database._getInstance( )
        return inst.fips_msas_2019

    @classmethod
    def data_msas_2019( cls ):
        inst = COVID19Database._getInstance( )
        return inst.data_msas_2019
        
    @classmethod
    def all_counties_nytimes_covid19_data( cls ):
        inst = COVID19Database._getInstance( )
        return inst.all_counties_nytimes_covid19_data

    @classmethod
    def data_conus( cls ):
        inst = COVID19Database._getInstance( )
        return inst.data_conus

    @classmethod
    def mapping_state_rname_conus( cls ):
        inst = COVID19Database._getInstance( )
        return inst.mapping_state_rname_conus

    @classmethod
    def mapping_state_rname_nonconus( cls ):
        inst = COVID19Database._getInstance( )
        return inst.mapping_state_rname_nonconus

    @classmethod
    def data_states( cls ):
        inst = COVID19Database._getInstance( )
        return inst.data_states
        
    @classmethod
    def data_nonconus_states_territories( cls ):
        inst = COVID19Database._getInstance( )        
        return inst.data_nonconus_states_territories
    
