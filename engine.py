import os, sys, numpy, glob, pylab, tabulate, datetime, pandas, titlecase
import defaults, engine_geo
from itertools import chain
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

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
            open( os.path.join( "covid-19-data", "us-counties.csv" ), "r" ).readlines())))[1:])))

all_counties_state = list(map(
    lambda entry: { 'county' : entry[0], 'state' : entry[1] },
    set(map(lambda entry: ( entry['county'], entry['state'] ), all_counties_nytimes_covid19_data ) ) ) )

fips_data_2018 = engine_geo.load_fips_data( )

fips_countystate_dict = dict(map(lambda f_c_s: ( f_c_s[0], {
    'county' : f_c_s[1], 'state' : f_c_s[2] } ), set(
        map(_get_fips_county_state, all_counties_nytimes_covid19_data ) ) ) )

def get_county_state( fips ):
    if fips not in fips_countystate_dict: return None
    return fips_countystate_dict[ fips ]

data_msas_2019 = engine_geo.load_msas_data( )


def get_data_county( county_name, state = 'California' ):
  data_by_date = sorted(filter(lambda entry: county_name in entry['county'] and
                               entry['state'] == state, all_counties_nytimes_covid19_data ),
                        key = lambda entry: entry['date'] )
  return data_by_date

def get_incident_data( data = defaults.bay_area_data ):
    prefix = data[ 'prefix' ]
    regionName = data[ 'region name' ]
    counties_and_states = data[ 'counties' ]
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
    ## now get fips data for counties in this collection
    fips_collection = set(map(lambda entry: entry['fips'], all_data_region))
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
    boundary_dict = dict(map(lambda fips: ( fips, fips_data_2018[ fips ][ 'points' ] ), fips_collection ) )
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

def get_maximum_cases( inc_data ):
    df = inc_data[ 'df' ]
    max_case_tup = max(map(lambda key: (
        key.replace('cases_', '').strip( ),
        df[key].max( ) ), filter(lambda key: key.startswith('cases_'), df ) ),
                       key = lambda tup: tup[1] )
    return max_case_tup

def get_summary_demo_data( data = defaults.bay_area_data, doShow = True ):
    prefix = data[ 'prefix' ]
    regionName = data[ 'region name' ]
    counties_and_states = data[ 'counties' ]
    inc_data = get_incident_data( data )
    df_cases_deaths_region = inc_data[ 'df' ]
    #
    first_date = min( df_cases_deaths_region.date )
    last_date = max( df_cases_deaths_region.date )
    #
    ## pickle this pandas data
    cur_date_str = datetime.datetime.now( ).date( ).strftime('%d%m%Y' )
    df_cases_deaths_region.to_pickle(
        'covid19_%s_%s.pkl.gz' % ( prefix, cur_date_str ) )
    #
    ## now make a plot, logarithmic
    fig, ax = pylab.subplots( )
    fig.set_size_inches([ 12.0, 9.6 ])
    df_cases_deaths_region.plot(
        'days_from_beginning', 'cases', linewidth = 4.5,
        ax = ax, logy = True, grid = True )
    df_cases_deaths_region.plot(
        'days_from_beginning', 'death', linewidth = 4.5,
        ax = ax, logy = True, grid = True )
    ax.set_ylim( 1.0, 1.05 * df_cases_deaths_region.cases.max( ) )
    ax.set_xlim( 0, df_cases_deaths_region.days_from_beginning.max( ) )
    ax.set_xlabel(
        'Days from First COVID-19 CASE (%s)' %
        first_date.strftime( '%d-%m-%Y' ),
        fontsize = 24, fontweight = 'bold' )
    ax.set_ylabel( 'Cumulative Number of Cases/Deaths', fontsize = 24, fontweight = 'bold' )
    ax.set_title( '\n'.join(
        [
         '%s Trend in COVID-19' % titlecase.titlecase( regionName ),
         'from %s through %s' % (
        first_date.strftime( '%d-%m-%Y' ),
        last_date.strftime( '%d-%m-%Y' ) ) ]),
                 fontsize = 24, fontweight = 'bold' )
    #
    ## tick labels size 20, bold
    for tick in ax.xaxis.get_major_ticks( ) + ax.yaxis.get_major_ticks( ):
        tick.label.set_fontsize( 20 )
        tick.label.set_fontweight( 'bold' )
    #
    ## legend size 24, bold
    leg = ax.legend( )
    for txt in leg.texts:
        txt.set_fontsize( 24 )
        txt.set_fontweight( 'bold' )
    #
    ## save figures
    fig.savefig(  'covid19_%s_%s.pdf' % ( prefix, cur_date_str ), bbox_inches = 'tight' )
    fig.savefig(  'covid19_%s_%s.png' % ( prefix, cur_date_str ), bbox_inches = 'tight' )
    #
    ## now SHOW!
    if doShow: pylab.show( )
