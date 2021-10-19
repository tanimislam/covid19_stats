import os, sys, numpy, glob, tabulate, logging, requests, json
import datetime, pandas, titlecase, networkx, time
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
from covid19_stats.engine import gis, get_string_commas_num

def get_boundary_dict( fips_collection ):
    """
    Returns a :py:class:`dict` of `FIPS code`_ to the collection of geographic areas for that county. The geographic data comes from :py:meth:`fips_data_2019 <covid19_stats.COVID19Database.fips_data_2019>`.
    
    :param set fips_collection: the :py:class:`set` of `FIPS code`_\ s of counties or US territorial units for which to get geographic information.
    :returns: a :py:class:`dict`. The key is the `FIPS code`_ of a county or territorial unit, and the value is the :py:class:`list` of geographic regions for that county or unit.
    :rtype: dict

    .. _`FIPS code`: https://en.wikipedia.org/wiki/FIPS_county_code
    """
    fips_data_2019 = COVID19Database.fips_data_2019( )
    boundary_dict = dict(map(lambda fips: (
        fips, fips_data_2019[ fips ][ 'points' ] ), fips_collection ) )
    return boundary_dict

def get_mp4_album_name( inc_data ):
    """
    This method operates on MP4_ movie output from command line tools that produce COVID-19 case and death summary movies -- such as :ref:`covid19_create_movie_or_summary`, :ref:`covid19_state_summary`, or :ref:`covid19_movie_updates` -- or methods that create MP4_ files -- such as :py:meth:`create_summary_cases_or_deaths_movie_frombeginning <covid19_stats.engine.viz.create_summary_cases_or_deaths_movie_frombeginning>` or :py:meth:`create_summary_movie_frombeginning <covid19_stats.engine.viz.create_summary_movie_frombeginning>`.

    It determines whether the geographic region is classified as a ``STATE``, ``CONUS``, ``METROPOLITAN STATISTICAL AREA``, or ``CUSTOM REGION``. It is used in four CLI functionalities:

    * :ref:`movie mode functionality for covid19_create_movie_or_summary <movie_mode>`.
    * :ref:`movie cases death mode functionality for covid19_create_movie_or_summary <movie_cases_deaths_mode>`.
    * :ref:`movie mode functionality for covid19_state_summary <movie_mode_state>`.
    * :ref:`movie cases death mode functionality for covid19_state_summary <movie_cases_deaths_mode_state>`.

    :param dict inc_data: the :py:class:`dict` that *contains* geographic data on the identified region. See :ref:`St. Louis data <stlouis_msa_example_data>` for an example of an MSA_ geographic data :py:class:`dict`. See :ref:`Rhode Island data <rhode_island_state_example_data>` for an example of a US state or territory. See :ref:`CONUS data <conus_example_data>` for the CONUS_.
       
       .. code-block:: python

          {'prefix': 'providence',
           'region name': 'Providence Metro Area',
           'fips': {'25005', '44001', '44003', '44005', '44007', '44009'},
           'population': 1624578}

    :returns: If the ``prefix`` is one of the MSA_\ s, ``METROPOLITAN STATISTICAL AREA``. If its ``prefix`` is identified as a state, then ``STATE``. If its prefix is ``conus``, then ``CONUS``.
    :rtype: str

    .. _MP4: https://en.wikipedia.org/wiki/MPEG-4_Part_14
    .. _providence: https://en.wikipedia.org/wiki/Providence,_Rhode_Island
    """
    data_states_territories_names = set( COVID19Database.data_states( ) ) | set(
        COVID19Database.data_nonconus_states_territories())
    data_msas_names = set( COVID19Database.data_msas_2019( ) )
    if inc_data['prefix'] in data_states_territories_names:
        return 'STATE'
    if inc_data['prefix'].lower( ) == 'conus':
        return 'CONUS'
    if inc_data['prefix'] in data_msas_names:
        return 'METROPOLITAN STATISTICAL AREA'
    return 'CUSTOM REGION'

#
## now stuff associated with the fips : county/state mapping
def get_county_state( fips ):
    """
    :param str fips: the `FIPS code`_ of the county or territorial unit.
    :returns: a :py:class:`dict` of ``county`` and ``state``.
    :rtype: dict
    """
    fips_countystate_dict = COVID19Database.fips_countystate_dict( )
    if fips not in fips_countystate_dict: return None
    return fips_countystate_dict[ fips ]

def get_fips_msa( county, state ):
    """
    Given a county and state of a county or territorial unit, returns its `FIPS code`_ and the data structure on the MSA_ in which this county lies.

    :param str county: county name.
    :param str state: state name.
    :returns: a two-element :py:class:`tuple`. First element is the county or territorial unit `FIPS code`_. Second element is the geographical information on the MSA_ (see :ref:`St. Louis data <stlouis_msa_example_data>` for example).
    :rtype: tuple
    """
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
    """
    :param str msaname: the identifier name for the MSA_, which must be one of the keys in the :py:class:`dict` that :py:meth:`data_msas_2019 <covid19_stats.COVID19Database.data_msas_2019>` returns.
    :returns: the MSA_ geographical information (see :ref:`St. Louis data <stlouis_msa_example_data>` for example).
    :rtype: dict
    """
    data_msas_2019 = COVID19Database.data_msas_2019( )
    assert( msaname in data_msas_2019 )
    return data_msas_2019[ msaname ].copy( )
    

def get_data_fips( fips ):
    """
    Given a county identified by its `FIPS code`_, Returns the COVID-19 cumulative cases and deaths record of a single county or territorial unit identified by its `FIPS code`_. Takes the data from the cumulative cases and deaths record of the NY Times COVID-19 database (see :py:meth:`all_counties_nytimes_covid19_data <covid19_stats.COVID19Database.all_counties_nytimes_covid19_data>`).

    :param str fips: the `FIPS code`_ of the county or territorial unit.
    :returns: a two-element :py:class:`tuple`. First element is the ``fips``, and the second is the :py:class:`DataFrame <pandas.DataFrame>` representing the cumulative COVID-19 cases and deaths *ordered* by earliest to latest date. This :py:class:`DataFrame <pandas.DataFrame>` has three columns: ``date`` is the :py:class:`date <datetime.date>` of recorded incidence in that county, ``cases_<fips>`` is the cumulative COVID-19 cases on that :py:class:`date <datetime.date>`, and ``deaths_<fips>`` is the cumulative COVID-19 deaths on that :py:class:`date <datetime.date>`. Here, ``<fips>`` is the FIPS code of that county.
    :rtype: tuple
    """
    all_counties_nytimes_covid19_data_df = COVID19Database.all_counties_nytimes_covid19_data( )
    df_data_by_date = all_counties_nytimes_covid19_data_df[ all_counties_nytimes_covid19_data_df.fips == fips ].copy( ).sort_values( 'date' ).reset_index( )
    df_data_by_date['cases_%s' % fips ] = numpy.array( df_data_by_date['cumulative cases'], dtype=int )
    df_data_by_date['deaths_%s' % fips ] = numpy.array( df_data_by_date['cumulative death'], dtype=int )
    df_data_by_date.pop( 'cumulative cases' )
    df_data_by_date.pop( 'cumulative death' )
    df_data_by_date.pop( 'county' )
    df_data_by_date.pop( 'state' )
    df_data_by_date.pop( 'fips' )
    df_data_by_date.pop( 'index' )
    return fips, df_data_by_date
    
    #date_list = list( df_data_by_date.date )
    #county_list = list( df_data_by_date.county )
    #state_list = list( df_data_by_date.state )
    #cases_list = list( df_data_by_date['cumulative cases'] )
    #death_list = list( df_data_by_date['cumulative death'] )
    #
    #return list(map(lambda tup: {
    #    'date' : tup[0], 'county' : tup[1], 'state' : tup[2], 'fips' : fips, 'cumulative cases' : tup[3],
    #    'cumulative death' : tup[4] }, zip( date_list, county_list, state_list, cases_list, death_list ) ) )
    #data_by_date = sorted(filter(lambda entry: entry['fips'] == fips,
    #                             all_counties_nytimes_covid19_data ),
    #                      key = lambda entry: entry['date'] )
    #return data_by_date

def get_incident_data( data = None, multiprocess = True ):
    """
    Given geographical information on a region, will return COVID-19 cumulative statistics on all the counties or territorial units of that structure. Best to show by example.

    For example, for the ``bayearea`` MSA_, the output incident data structure for 26 February 2021 lives in :download:`core_incident_data_bayarea.pkl.gz </_static/core/core_incident_data_bayarea.pkl.gz>`. This structure is a :py:class:`dict` with the following keys and values.

    * ``bbox`` is a 4-element :py:class:`tuple` of the region bounding box: minimum lat/lng, and maximum lat/lng.
    * ``boundaries`` is a :py:class:`dict` of boundary information. Each key is the `FIPS code`_, and its value is a :py:class:`list` of boundary lat/lngs for that county or territorial unit. Look at :download:`gis_calculate_total_bbox_sacramento.pkl.gz </_static/gis/gis_calculate_total_bbox_sacramento.pkl.gz>` for an example of this data structure.
    * ``last day`` is the number of days (from first COVID-19 incident) in this incident data set.
    * ``df`` is the :py:class:`DataFrame <pandas.DataFrame>` that contains COVID-19 cumulative case and death data for all counties or territorial units in that region.
    * ``df_1day`` is the :py:class:`DataFrame <pandas.DataFrame>` that contains the 1-day averaged COVID-19 *new* case and death data for all counties or territorial units in that region.
    * ``df_7day`` is the :py:class:`DataFrame <pandas.DataFrame>` that contains the 7-day averaged COVID-19 *new* case and death data for all counties or territorial units in that region.
    * ``prefix`` is the :py:class:`string <str>` inherited from the input ``prefix`` key in the ``data`` :py:class:`dict`.
    * ``region name`` is the :py:class:`string <str>` inherited from the input ``region name`` key in the ``data`` :py:class:`dict`.
    * ``population`` is the :py:class:`int` inherited from the input ``population`` key in the ``data`` :py:class:`dict`.
    * ``fips`` is the :py:class:`set` inherited from the input ``fips`` key in the ``data`` :py:class:`dict`.

    This :py:class:`Pandas DataFrame <pandas.DataFrame>`, located under the ``df`` key, has the following columns ordered by first to last incident date.

    * ``days_from_beginning`` is the day relative to the first incident. It starts at 0 and ends at ``last day``.
    * ``date`` contains the :py:class:`date <datetime.date>` of the incident day, from first to last.
    * ``cases`` are the cumulative COVID-19 cases for the whole region from first to last incident date.
    * ``death`` are the cumulative COVID-19 deaths for the whole region from first to last incident date.
    * ``cases_<NUM>`` are the cumulative COVID-19 cases for a given county or territorial unit in the region (<NUM> is its `FIPS code`_) from first to last incident date.
    * ``deaths_<NUM>`` are the cumulative COVID-19 deaths for a given county or territorial unit in the region (<NUM> is its `FIPS code`_) from first to last incident date.
    
    :param dict data: Optional argument, but if specified is the geographical information of a region. By default is the ``bayarea`` MSA_. See :ref:`St. Louis data <stlouis_msa_example_data>` for an example of an MSA_. See :ref:`Rhode Island data <rhode_island_state_example_data>` for an example of a US state or territory. See :ref:`CONUS data <conus_example_data>` for the CONUS_.
    :param bool multiprocess: if ``True``, then use multiprocessing to get the incident data information, otherwise do not. Default is ``True``.
    :returns: the :py:class:`dict` described above, see :download:`core_incident_data_bayarea.pkl.gz </_static/core/core_incident_data_bayarea.pkl.gz>`.
    :rtype: dict
    """
    if data is None: data = get_msa_data( 'bayarea' )
    prefix = data[ 'prefix' ]
    regionName = data[ 'region name' ]
    fips_collection = set( data['fips'] )
    #
    ## now this creates a dictionary of incidents and deaths per county
    ## make process a LITTLE more efficient, because get_incident_data on CONUS is SLOW....
    time0 = time.time( )
    if multiprocess:
        with Pool( processes = cpu_count( ) ) as pool:
            dict_df_all_fips = dict(pool.map(
                get_data_fips, set( fips_collection ) ) )
    else:
        dict_df_all_fips = dict(map(
            get_data_fips, set( fips_collection ) ) )
    logging.info( 'took %0.3f seconds to get all date-sorted raw incident data for %s.' % (
        time.time( ) - time0, regionName ) )

    #
    ## now get UNION of dates
    all_dates = set(chain.from_iterable(map(lambda fips: list( dict_df_all_fips[ fips ].date ), dict_df_all_fips ) ) )
    max_date = max( all_dates )
    #
    ## assert that max date for EACH dataframe is the max_date
    max_all_date = set(map(lambda fips: dict_df_all_fips[ fips ].date.max( ), dict_df_all_fips ) )
    assert( len( max_all_date ) == 1 )
    assert( max( max_all_date ) == max_date )
    #
    ## now for each of those FIPS, append stuff pad so that dates are SAME for each FIPS. If missing, assumed cumulative cases and deaths ZERO
    for fips in dict_df_all_fips:
        dates_rem = set( all_dates - set( dict_df_all_fips[ fips ].date ) )
        if len( dates_rem ) == 0: continue
        data_to_append = pandas.DataFrame( {
            'date' : sorted( dates_rem ),
            'cases_%s' % fips : [ 0 ] * len( dates_rem ),
            'deaths_%s' % fips : [ 0 ] * len( dates_rem ) } )
        df_new = dict_df_all_fips[ fips ].copy( ).append( data_to_append ).sort_values( 'date' ).reset_index( )
        dict_df_all_fips[ fips ] = df_new
    #
    ## Now get ONE of the dates (all dates are now the same)
    dates_in_order = list( dict_df_all_fips[ min( dict_df_all_fips ) ].date )
    for fips in dict_df_all_fips:
        dict_df_all_fips[ fips ].pop( 'date' )
    dict_to_make_into_df = { 'date' : dates_in_order }
    #
    ## now the cumulative COVID-19 cases and deaths for each region
    for fips in sorted( dict_df_all_fips ):
        dict_to_make_into_df[ 'cases_%s' % fips ] = numpy.array(
            dict_df_all_fips[ fips ][ 'cases_%s' % fips ], dtype=int )
        dict_to_make_into_df[ 'deaths_%s' % fips ] = numpy.array(
            dict_df_all_fips[ fips ][ 'deaths_%s' % fips ], dtype=int )
    #
    ## now the first iteration of creating the cases_deaths_region_bydate DataFrame
    df_cases_deaths_region = pandas.DataFrame( dict_to_make_into_df ).reset_index( )
    #
    ## now cumulative cases and deaths
    ## welcome to goofy Pandas DataFrames hell!
    cases_names = sorted(map(lambda fips: 'cases_%s' % fips, dict_df_all_fips ) )
    deaths_names= sorted(map(lambda fips: 'deaths_%s' % fips, dict_df_all_fips ) )
    df_cases_deaths_region[ 'cases' ] = numpy.array(
        df_cases_deaths_region[ pandas.Index( cases_names ) ].sum(axis = 1 ), dtype = int )
    df_cases_deaths_region[ 'death' ] = numpy.array(
        df_cases_deaths_region[ pandas.Index( deaths_names )].sum(axis = 1 ), dtype = int )
    #
    ## now the days_from_beginning column
    df_cases_deaths_region[ 'days_from_beginning' ] = list(
        map(lambda mydate: ( mydate - df_cases_deaths_region.date.min( ) ).days, 
            df_cases_deaths_region.date ) )

    #
    ## now do the SAME things, but for the 7-day averaged new cases and deaths.
    ## in this case, the days_from_beginning starts from 7, and the ``date`` starts from day 7 (not day 0).
    num_days  = len( numpy.array(df_cases_deaths_region.cases ) )
    days_7day = numpy.array( list(range( 7, num_days ) ), dtype=int )
    days_1day = numpy.array( list(range( 1, num_days ) ), dtype=int )
    def get_newcases_avg( fips, num_days = 7 ):
        assert( num_days >= 1 )
        cases_cumul = numpy.array( df_cases_deaths_region[ 'cases_%s' % fips ], dtype = int )
        return ( cases_cumul[num_days:] - cases_cumul[:-num_days] ) * 1.0 / num_days
    def get_newdeaths_avg( fips, num_days = 7 ):
        assert( num_days >= 1 )
        deaths_cumul = numpy.array( df_cases_deaths_region[ 'deaths_%s' % fips ], dtype = int )
        return ( deaths_cumul[num_days:] - deaths_cumul[:-num_days] ) * 1.0 / num_days
    #
    ## 7 day average
    df_cases_deaths_region_7day = pandas.DataFrame(
        dict(chain.from_iterable([
            map(lambda fips: (
                'cases_%s_7day_new' % fips, get_newcases_avg( fips, num_days = 7 ) ),
                dict_df_all_fips ),
            map(lambda fips: (
                'deaths_%s_7day_new' % fips, get_newdeaths_avg( fips, num_days = 7 ) ),
                dict_df_all_fips ) ]) ) )
    cases_names_7day = sorted(map(lambda fips: 'cases_%s_7day_new' % fips, dict_df_all_fips ) )
    deaths_names_7day= sorted(map(lambda fips: 'deaths_%s_7day_new'% fips, dict_df_all_fips ) )
    df_cases_deaths_region_7day[ 'cases_new' ] = numpy.array(
        df_cases_deaths_region_7day[ pandas.Index( cases_names_7day ) ].sum( axis = 1 ), dtype = float )
    df_cases_deaths_region_7day[ 'death_new' ] = numpy.array(
        df_cases_deaths_region_7day[ pandas.Index( deaths_names_7day )].sum( axis = 1 ), dtype = float )
    df_cases_deaths_region_7day[ 'days_from_beginning' ] = days_7day
    df_cases_deaths_region_7day[ 'date' ] = list( df_cases_deaths_region.date )[7:]
    #
    ## 1 day average
    df_cases_deaths_region_1day = pandas.DataFrame(
        dict(chain.from_iterable([
            map(lambda fips: (
                'cases_%s_1day_new' % fips, get_newcases_avg( fips, num_days = 1 ) ),
                dict_df_all_fips ),
            map(lambda fips: (
                'deaths_%s_1day_new' % fips, get_newdeaths_avg( fips, num_days = 1 ) ),
                dict_df_all_fips ) ]) ) )
    cases_names_1day = sorted(map(lambda fips: 'cases_%s_1day_new' % fips, dict_df_all_fips ) )
    deaths_names_1day= sorted(map(lambda fips: 'deaths_%s_1day_new'% fips, dict_df_all_fips ) )
    df_cases_deaths_region_1day[ 'cases_new' ] = numpy.array(
        df_cases_deaths_region_1day[ pandas.Index( cases_names_1day ) ].sum( axis = 1 ), dtype = float )
    df_cases_deaths_region_1day[ 'death_new' ] = numpy.array(
        df_cases_deaths_region_1day[ pandas.Index( deaths_names_1day )].sum( axis = 1 ), dtype = float )
    df_cases_deaths_region_1day[ 'days_from_beginning' ] = days_1day
    df_cases_deaths_region_1day[ 'date' ] = list( df_cases_deaths_region.date )[1:]
            
    #
    ## now calculate the bounding box of this collection of fips data
    boundary_dict = get_boundary_dict( fips_collection )
    total_bbox = gis.calculate_total_bbox( chain.from_iterable(
        boundary_dict.values( ) ) )
    
    #
    ## return
    incident_data = {
        'df' : df_cases_deaths_region, 'bbox' : total_bbox, 'boundaries' : boundary_dict,
        'df_7day' : df_cases_deaths_region_7day, 'df_1day' : df_cases_deaths_region_1day,
        'last day' : df_cases_deaths_region.days_from_beginning.max( ),
        'prefix' : data[ 'prefix' ],
        'region name' : data[ 'region name' ],
        'fips' : data[ 'fips' ],
        'population' : data[ 'population' ] }
    return incident_data

def get_max_cases_county( inc_data ):
    """
    Convenience method that returns a :py:class:`dict` of the `FIPS code`_, county, state, and cases for the county or territorial unit, for the county in a region that has the *worst* number of COVID-19 cases.

    :param dict inc_data: the incident data structure for a region. See :py:meth:`get_incident_data <covid19_stats.engine.core.get_incident_data>` for what this output looks like.
    :returns: a :py:class:`dict` of summary information on the *worst-perfoming* county in the region, COVID-19 case wise. For :download:`core_incident_data_bayarea.pkl.gz </_static/core/core_incident_data_bayarea.pkl.gz>`, this is,

       .. code-block:: python

          {'fips': '06085',
           'cases': 94366,
           'county': 'Santa Clara County',
           'state': 'California'}

    :rtype: dict
    """
    df = inc_data['df']
    fips_max, case_max = max(map(lambda key: ( key.split('_')[-1].strip( ), df[key].max( ) ),
                                 filter(lambda key: key.startswith('cases_'), df)),
                             key = lambda tup: tup[-1] )
    cs_max = get_county_state( fips_max )
    return { 'fips' : fips_max, 'cases' : case_max, 'county' : cs_max[ 'county'],
            'state' : cs_max[ 'state' ] }

def get_maximum_cases( inc_data ):
    """
    Convenience method that returns a two-element :py:class:`tuple` of the `FIPS code`_ and number of COVID-19 cases, for the *worst-performing* county, case-wise.

    :param dict inc_data: the incident data structure for a region. See :py:meth:`get_incident_data <covid19_stats.engine.core.get_incident_data>` for what this output looks like.
    :returns: the two-element :py:class:`tuple` of `FIPS code`_ and cumulative number of COVID-19 cases. For :download:`core_incident_data_bayarea.pkl.gz </_static/core/core_incident_data_bayarea.pkl.gz>`, this is,

       .. code-block:: python

          ('06085', 94366)

    :rtype: tuple
    """
    df = inc_data[ 'df' ]
    max_case_tup = max(map(lambda key: (
        key.replace('cases_', '').strip( ),
        df[key].max( ) ), filter(lambda key: key.startswith('cases_'), df ) ),
                       key = lambda tup: tup[1] )
    return max_case_tup

def create_readme_from_template(
    mainURL = 'https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies',
    dirname_for_readme_location = os.getcwd( ), verify = True,
    topN_json = None ):
    """
    This recreates the :download:`README.rst </_static/README.rst>` to reflect the latest COVID-19 data, using the Jinja2_ templated :download:`README_template.rst </_static/README_template.rst>`. This is the back-end method to :ref:`covid19_update_readme`.

    :param str mainURL: the URL directory for which to look for a manifest JSON_ file of cumulative COVID-19 cases and deaths for the top population MSA_\ s, ``covid19_topN_LATEST.json``. This manifest file's location is ``<mainURL>/covid19_topN_LATEST.json``. By default, this is https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies.
    :param str dirname_for_readme_location: the location, on disk, where the covid19_stats downloaded repository lives. By default this is the current working directory.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :param str topN_json: optional argument, the location of the manifest JSON_ file on disk. If specified, then this method ignores the online location, ``<mainURL>/covid19_topN_LATEST.json``.

    .. _JSON: https://en.wikipedia.org/wiki/JSON
    .. _Jinja2: https://jinja.palletsprojects.com
    """
    
    assert( os.path.isdir( dirname_for_readme_location ) )
    #response = requests.get( mainURL, verify = verify )
    #if response.status_code != 200:
    #    raise ValueError("Error, could not access %s." % mainURL )
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
            'POP_FORMATTED' : get_string_commas_num( entry[ 'POPULATION' ] ),
            'FIRST_INCIDENT': entry[ 'FIRST INC.' ],
            'NUM_DAYS' : entry[ 'NUM DAYS' ],
            'NUM_CASES_FORMATTED' : get_string_commas_num( entry[ 'NUM CASES' ] ),
            'NUM_DEATHS_FORMATTED': get_string_commas_num( entry[ 'NUM DEATHS' ] ),
            'MAX_CASE_COUNTY_FORMATTED' : get_string_commas_num( entry[ 'MAX CASE COUNTY' ] ),
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
    """
    Takes the :py:class:`list` data of summary COVID-19 death in MSA_\ s, and prints out to `list-tabled reStructuredText <rst_list_table_>`_. An example of this data structure is :download:`core_summary_data.json </_static/core/core_summary_data.json>`.

    :param list summary_data_json: a :py:class:`list` of summary data of COVID-19 cumulative cases and deaths for MSA_\ s as :py:class:`dict` entries. This :py:class:`list` is sorted from largest MSA_ population to smallest. An example output is :download:`core_summary_data.json </_static/core/core_summary_data.json>` and shown :ref:`here <summary_data_example>`.
    """
    def _get_row( entry ):
        return (
            entry[ 'RANK' ],
            entry[ 'PREFIX' ],
            entry[ 'NAME' ],
            get_string_commas_num( entry[ 'POPULATION' ] ),
            entry[ 'FIRST INC.' ],
            entry[ 'NUM DAYS' ],
            get_string_commas_num( entry[ 'NUM CASES' ] ),
            get_string_commas_num( entry[ 'NUM DEATHS' ] ),
            get_string_commas_num( entry[ 'MAX CASE COUNTY' ] ),
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
    """
    Prints summary COVID-19 cumulative cases and deaths of all or selected MSA_\ s to stdout a nice tabulated table, in either a simple format with ``simple``, `Github flavored Markdown <gfm_>`_ with ``github``, `reStructuredText <rst_>`_ with ``rst``, or `list-tabled reStructuredText <rst_list_table_>`_ with ``rst-simple``.

    Otherwise, if one chooses ``json``, then returns a :py:class:`list` of that information.

    This acts as an API back-end to :ref:`summarizing MSAs functionality in covid19_create_movie_or_summary <metro_mode>`. Please see :ref:`demonstration output <demonstration_simple_format>` for what this data looks like on screen.

    :param str form: If one of ``simple``, ``github``, ``rst``, or ``rst-simple``, then prints the table of MSA_ summary COVID-19 data to screen. If one of ``simple``, ``github``, or ``rst``, then uses :py:meth:`tabulate <tabulate.tabulate>` to format the data.

       If ``json``, then returns a :py:class:`list` of summary data of COVID-19 cumulative cases and deaths for all or specified MSA_\ s as :py:class:`dict` entries. This :py:class:`list` is sorted from largest MSA_ population to smallest. An example output is :download:`core_summary_data.json </_static/core/core_summary_data.json>`. Here are the first two entries,

       .. _summary_data_example:

       .. code-block:: python

          [{'RANK': 1,
            'PREFIX': 'nyc',
            'NAME': 'NYC Metro Area',
            'POPULATION': 19216182,
            'FIRST INC.': '01 March 2020',
            'NUM DAYS': 324,
            'NUM CASES': 1390557,
            'NUM DEATHS': 50378,
            'MAX CASE COUNTY': 541846,
            'MAX CASE COUNTY NAME': 'New York City, New York'},
           {'RANK': 2,
            'PREFIX': 'losangeles',
            'NAME': 'LA Metro Area',
            'POPULATION': 18711436,
            'FIRST INC.': '25 January 2020',
            'NUM DAYS': 360,
            'NUM CASES': 1828244,
            'NUM DEATHS': 21240,
            'MAX CASE COUNTY': 1032277,
            'MAX CASE COUNTY NAME': 'Los Angeles County, California'}]

    :param list selected_metros: Optional argument. By default, will print or return information on *all* MSA_\ s. Otherwise specify the :py:class:`list` of MSA_\ s available as keys of the :py:meth:`data_msas_2019 <covid19_stats.COVID19Database.data_msas_2019>` dictionary.

    .. _gfm: https://github.github.com/gfm/#tables-extension-
    .. _rst: https://docutils.sourceforge.io/docs/ref/rst/directives.html#tables
    .. _rst_list_table: https://docutils.sourceforge.io/docs/ref/rst/directives.html#list-table
    .. 
    """
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
            lambda prefix: ( prefix, get_incident_data( data_msas_2019[ prefix ], multiprocess = False ) ),
            data_msas_2019 ) )
    date_last = max(map(lambda inc_data: inc_data['df'].date.max( ), incident_data_dict.values()))

    def _get_row( tup ):
        idx, (data_msa, to_json) = tup
        rank = idx + 1
        prefix = data_msa[ 'prefix' ]
        regionName = data_msa[ 'region name' ]
        population_s = get_string_commas_num( data_msa[ 'population' ] )
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
            get_string_commas_num(num_cases),
            get_string_commas_num(num_death),
            get_string_commas_num(max_case_co),
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
    """
    Finds the *separate* clusters of counties or territorial units that are clustered together. This is used to identify possibly *different* clusters of counties that may be separate from each other. If one does not supply an adjacency :py:class:`dict`, it uses the adjacency dictionary that :py:meth:`fips_adj_2018 <covid19_stats.COVID19Database.fips_adj_2018>` returns. Look at :download:`fips_2019_adj.pkl.gz </_static/gis/fips_2019_adj.pkl.gz>` to see what this dictionary looks like.

    :param list collection_of_fips: the :py:class:`list` of counties or territorial units, each identified by its `FIPS code`_.
    :param dict adj: optionally specified adjacency dictionary. Otherwise it uses the :py:meth:`fips_adj_2018 <covid19_stats.COVID19Database.fips_adj_2018>` returned dictionary. Look at :download:`fips_2019_adj.pkl.gz </_static/gis/fips_2019_adj.pkl.gz>` to see what this dictionary looks like.
    :returns: a :py:class:`list` of counties clustered together. Each cluster is a :py:class:`set` of `FIPS code`_\ s of counties grouped together.
    :rtype: list
    """
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
