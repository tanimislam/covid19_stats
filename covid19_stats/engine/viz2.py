import os, sys, numpy, titlecase, time, pandas, zipfile, mutagen.mp4
import subprocess, tempfile, shutil, datetime, logging
import pathos.multiprocessing as multiprocessing
from itertools import chain
from multiprocessing import Value, Manager
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LogNorm, to_rgba, Normalize
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from distutils.spawn import find_executable
from nprstuff.core import autocrop_image
#
from covid19_stats.engine import core, get_string_commas_num, get_string_commas_num_float, find_plausible_maxnum
from covid19_stats.engine.viz import (
    my_colorbar, create_and_draw_fromfig,
    display_fips_geom, display_msa )
    
def plot_cases_or_deaths_rate_bycounty(
    inc_data, fig, type_disp = 'cases', days_from_beginning = 7,
    doTitle = True, plot_artists = { },
    poly_line_width = 1.0, legend_text_scaling = 1.0, doSmarter = False,
    rows = 1, cols = 1, num = 1 ):
    """
    This method is similar to :py:meth:`plot_cases_or_deaths_bycounty <covid19_stats.engine.viz.plot_cases_or_deaths_bycounty>` in the :py:mod:`viz <covid19_stats.engine.viz>` module. This displays the status of *seven-day averaged* COVID-19 new cases/day or deaths/days given an incidident data :py:class:`dict`, ``inc_data``. It displays the status of *seven-day averaged* COVID-19 new cases/day or deaths/day, a specific number of days from the beginning, coloring the counties in that region according to the legend maximum, and places the resulting :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` at a specific location in a :py:class:`Figure <matplotlib.figure.Figure>` grid of :py:class:`Axes <matplotlib.axes.Axes>` or :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`.

    Instead of returning a :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`, this initializes a :py:class:`dict` of matplotlib objects, ``plot_artists``. In this way, subsequent plots, e.g. for different days after the beginnning, do not have to perform the relatively costly operation of recreating the :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` and fully painting in the :py:class:`Polygon <matplotlib.patches.Polygon>` patches; instead, these :py:class:`Polygon <matplotlib.patches.Polygon>` patches are re-colored and necessary :py:class:`Text <matplotlib.text.Text>` artists' strings are changed.

    .. _plot_artists_dict_discussion_viz2:

    This :py:class:`dict`, ``plot_artists``, has the following keys, identical to those in :py:meth:`plot_cases_or_deaths_bycounty <covid19_stats.engine.viz.plot_cases_or_deaths_bycounty>`,

    * ``axes``: when initialized, the :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` that consists of all counties, with COVID-19 cases or deaths, to display.
    * ``sm``: the :py:class:`ScalarMappable <matplotlib.cm.ScalarMappable>` describing the coloration by value for each county.

    Furthermore, it is easier to show rather than tell. :numref:`viz2_plot_cases_or_deaths_rate_bycounty_nyc` depicts both *seven-day averaged* COVID-19 new cases/day and deaths/day for the NYC metro area, 150 days after this metro's first COVID-19 incident.

    .. _viz2_plot_cases_or_deaths_rate_bycounty_nyc:

    .. figure:: /_static/viz2/viz2_plot_cases_or_deaths_rate_bycounty_nyc.png
       :width: 100%
       :align: left

       On the left, is the *seven-day averaged* COVID-19 new cases/day, and on the right, is the COVID-19 new deaths/day, for the NYC metro area, 150 days after its first COVID-19 incident. The color limits for cases (left) is :math:`10^4` cases/day, while the color limits for death (right) is :math:`1.7\\times 10^3` deaths/day. We have chosen to display the titles over both plots. Color scaling is logarithmic.

    :numref:`viz2_plot_cases_or_deaths_rate_bycounty_conus` depicts both *seven day averaged* COVID-19 new cases/day and deaths/day for the CONUS_, 150 days after its first COVID-19 incident.

    
    .. _viz2_plot_cases_or_deaths_rate_bycounty_conus:

    .. figure:: /_static/viz2/viz2_plot_cases_or_deaths_rate_bycounty_conus.png
       :width: 100%
       :align: left

       On the left, is the *seven-day averaged* COVID-19 new cases/day, and on the right, is the COVID-19 new deaths/day, for the CONUS_, 150 days after its first COVID-19 incident. The color limits for cases (left) is :math:`3.2\\times 10^4` cases/day, while the color limits for death (right) is :math:`1.7\\times 10^3` deaths/day. We have chosen to display the titles over both plots. Color scaling is logarithmic.

    Here are the arguments.
    
    :param dict inc_data: the data for incidence of COVID-19 cases and deaths for a given geographical region. See :py:meth:`get_incident_data <covid19_stats.engine.core.get_incident_data>` for the format of the output data.
    :param fig: the :py:class:`Figure <matplotlib.figure.Figure>` onto which to create a :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` (stored into the ``plot_artists`` :py:class:`dict`) containing geographic features. Last three arguments -- ``rows``, ``cols``, and ``num`` -- describe the relative placement of the created :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`. See :py:meth:`add_subplot <matplotlib.figure.Figure.add_subplot>` for those three arguments' meanings.
    :param str type_disp: if ``cases``, then show cumulative COVID-19 cases. If ``deaths``, then show cumulative COVID-19 deaths. Can only be ``cases`` or ``deaths``.
    :param int days_from_beginning: days after first incident of COVID-19 in this region. Must be :math:`\ge 7`, due to the seven-day rolling average.
    :param bool doTitle: if ``True``, then display the title over the plot. Default is ``True``.
    :param dict plot_artists: this contains the essential plotting objects for quicker re-display when plotting different days. Look at :ref:`this description <plot_artists_dict_discussion_viz2>`.
    :param float poly_line_width: the line width of the counties to draw in the plot.
    :param float legend_text_scaling: sometimes the text annotations showing the date, number of incident days, and cumulative deaths or cases is *too large*. This is a multiplier on that text's font size. Default is 1.0, but must be :math:`> 0`.
    :param bool doSmarter: if ``False``, then make a plot tailored for small regions (relative to the size of the earth), such as states or MSA_\ s. If ``True``, then make a plot tailored for large regions such as the CONUS_. Default is ``False``.
    :param int rows: the number of rows for axes in the :py:class:`Figure <matplotlib.figure.Figure>` grid. Must be :math:`\ge 1`, and by default is 1.
    :param int cols: the number of columns for axes in the :py:class:`Figure <matplotlib.figure.Figure>` grid. Must be :math:`\ge 1`, and by default is 1.
    :param int num: the plot number of the :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` in this :py:class:`Figure <matplotlib.figure.Figure>` grid. Must be :math:`\ge 1` and :math:`\le`\ ``rows`` times ``columns``. Its default is 1. Look at :py:meth:`add_subplot <matplotlib.figure.Figure.add_subplot>` for its  meaning.

    .. _CONUS: https://en.wikipedia.org/wiki/Contiguous_United_States
    """
    cases_dict = { 'cases' : 'cases_new', 'deaths' : 'death_new' }
    assert( type_disp in cases_dict )
    assert( days_from_beginning >= inc_data['df_7day']['days_from_beginning'].min( ) )
    assert( days_from_beginning <= inc_data['df_7day']['days_from_beginning'].max( ) )
    assert( legend_text_scaling > 0 )
    key = cases_dict[ type_disp ]
    regionName = inc_data[ 'region name' ]
    #
    ## NOW CREATE BASEMAP HIGH REZ
    ## LAZY LOADING
    boundaries = inc_data['boundaries']
    if 'axes' not in plot_artists:
        if not doSmarter:
            ax = create_and_draw_fromfig( fig, inc_data[ 'bbox' ], rows = rows, cols = cols, num = num )
        else: ax = create_and_draw_fromfig(
            fig, inc_data[ 'bbox' ],
            river_linewidth = 1.0, river_alpha = 0.15,
            coast_linewidth = 1.0, coast_alpha = 0.25, mult_bounds_lat = 1.25,
            rows = rows, cols = cols, num = num )
        maxnum_7day_rate = max(
            list(map(lambda fips: inc_data[ 'df_7day' ][ '%s_%s_7day_new' % ( type_disp, fips ) ].max( ), inc_data[ 'fips' ] ) ) )
        maxnum_colorbar = find_plausible_maxnum( maxnum_7day_rate )
        plot_artists[ 'axes' ] = ax
        plot_artists[ 'sm' ] = ScalarMappable( norm = LogNorm( 0.1, maxnum_colorbar ), cmap = 'CMRmap_r' )
    #
    ## draw boundaries if not defined
    df_dfm = inc_data['df_7day'][ inc_data['df_7day']['days_from_beginning'] == days_from_beginning ].copy( )
    sm = plot_artists[ 'sm' ]
    ax = plot_artists[ 'axes' ]
    for fips in sorted( boundaries ):
        nums = max(0, df_dfm['%s_%s_7day_new' % ( type_disp, fips )].max( ) )
        if nums == 0: fc = ( 1.0, 1.0, 1.0, 0.0 )
        else: fc = sm.to_rgba( nums )
        art_key = '%s_polys_%s' % ( key, fips )
        if art_key not in plot_artists:
            plot_artists.setdefault( art_key, [ ] )
            for shape in boundaries[ fips ]:
                poly = Polygon(
                    shape, closed = True,
                    linewidth = poly_line_width, linestyle = 'dashed',
                    facecolor = fc, alpha = 0.4, transform = ccrs.PlateCarree( ) )
                ax.add_patch( poly )
                plot_artists[ art_key ].append( poly )
        else:
            for poly in plot_artists[ art_key ]:
                poly.set_facecolor( fc )
                poly.set_alpha( 0.4 )
    
    #
    ## now add the colorbar associated with sm
    if 'cb' not in plot_artists:        
        cb = my_colorbar( sm, ax, alpha = 0.8 )
        cb.set_label( 'number of new %s/day' % type_disp, fontsize = 18, fontweight = 'bold' )
        plot_artists[ 'cb' ] = cb
    #
    ## now put in the legend in upper left corner, fontsize = 14, weight = bold
    ## following info: date, days after beginning, number of cases
    date_s = df_dfm.date.max().strftime( '%d %B %Y' )
    num_tot = df_dfm[ key ].max( )
    if '%s_text' % key not in plot_artists:
        txt = ax.text(
            0.01, 0.02, '\n'.join([
                '%s' % date_s,
                '%d days from 1st case' % days_from_beginning,
                '%s 7 day average new: %s' % ( type_disp, get_string_commas_num_float( num_tot ) ) ]),
            color = ( 0.0, 0.0, 0.0, 0.8 ),
            fontsize = int( 18 * legend_text_scaling ),
            fontweight = 'bold', transform = ax.transAxes,
            horizontalalignment = 'left', verticalalignment = 'bottom' )
        plot_artists[ '%s_text' % key ] = txt
    else:
        plot_artists[ '%s_text' % key ].set_text('\n'.join([
            '%s' % date_s,
            '%d days from 1st case' % days_from_beginning,
            '%s 7 day average new: %s' % ( type_disp, get_string_commas_num_float( num_tot ) ) ] ) )
            
    if doTitle:
        ax.set_title( '\n'.join([
            '7 day average new number of COVID-19 %s' % type_disp,
            'in %s after %d / %d days from start' % (
                regionName, days_from_beginning, inc_data[ 'last day'] ) ] ),
                     fontsize = 18, fontweight = 'bold' )

def plot_cases_deaths_rate_region(
    inc_data, ax, days_from_beginning = 7,
    doTitle = True, legend_text_scaling = 1.0, aspect_ratio_mult = 1.0 ):
    """
    This method is similar to :py:meth:`plot_cases_deaths_region <covid19_stats.engine.viz.plot_cases_deaths_region>` in the :py:mod:`viz <covid19_stats.engine.viz>` module. Plots trend lines of *seven day averaged* COVID-19 new cases/day *and* new deaths/day for a region. It is easier to show rather than tell. :numref:`viz2_plot_cases_deaths_rate_region_nyc` depicts trend lines of COVID-19 new cases/day and deaths/day for the NYC metro area, 150 days after this metro's first COVID-19 incident.

    .. _viz2_plot_cases_deaths_rate_region_nyc:

    .. figure:: /_static/viz2/viz2_plot_cases_deaths_rate_region_nyc.png
       :width: 100%
       :align: left

       Plot of *seven day averaged* COVID-19 new cases/day and deaths/day for the NYC metro area, 150 days after its first incident. Plot scaling is logarithmic, and dots accentuate the state of the new cases/day and deaths/day 150 days after first incident. We have chosen to display the title. The lower-alpha and more jagged lines depict the *one-day averaged* new cases/day and deaths/day.

    Here are the arguments.
    
    :param dict inc_data: the data for incidence of COVID-19 cases and deaths for a given geographical region. See :py:meth:`get_incident_data <covid19_stats.engine.core.get_incident_data>` for the format of the output data.
    :param ax: the :py:class:`Axes <matplotlib.axes.Axes>` onto which to make this plot.
    :param int days_from_beginning: days after first incident of COVID-19 in this region. Must be :math:`\ge 7` because of the seven day average.
    :param bool doTitle: if ``True``, then display the title over the plot. Default is ``True``.
    :param float legend_text_scaling: sometimes the legend text for the cumulative COVID-19 cases and deaths is *too large*. This is a multiplier on that text's font size. Default is 1.0, but must be :math:`> 0`.
    :param float aspect_ratio_mult: in the quad plots created in :py:meth:`create_plots_rate_daysfrombeginning <covid19_stats.engine.viz2.create_plots_rate_daysfrombeginning>` or in :py:meth:`create_summary_rate_movie_frombeginning <covid19_stats.engine.viz2.create_summary_rate_movie_frombeginning>`, without modification the :py:class:`Axes <matplotlib.axes.Axes>` may look too squashed and inconsistent with the three other :py:class:`Axes <matplotlib.axes.Axes>` or :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`. This acts as a multiplier on the aspect ratio so that this :py:class:`Axes <matplotlib.axes.Axes>` does not look out of place. Default is 1.0, but must be :math:`> 0`.
    """
    assert( 'region name' in inc_data )
    assert( days_from_beginning >= 7 )
    assert( days_from_beginning <= inc_data[ 'last day' ] )
    assert( legend_text_scaling > 0 )
    assert( aspect_ratio_mult > 0 )
    regionName = inc_data[ 'region name' ]
    df_cases_deaths_7day_region = pandas.DataFrame({
        'date' : inc_data[ 'df_7day' ].date,
        'cases_new' : inc_data[ 'df_7day' ].cases_new,
        'death_new' : inc_data[ 'df_7day' ].death_new,
        'days_from_beginning' : inc_data[ 'df_7day' ].days_from_beginning } )
    df_cases_deaths_1day_region = pandas.DataFrame({
        'date' : inc_data[ 'df_1day' ].date,
        'cases_new' : inc_data[ 'df_1day' ].cases_new,
        'death_new' : inc_data[ 'df_1day' ].death_new,
        'days_from_beginning' : inc_data[ 'df_1day' ].days_from_beginning } )
    df_cases_deaths_1day_region = df_cases_deaths_1day_region[
        df_cases_deaths_1day_region.date >= df_cases_deaths_7day_region.date.min( ) ]
    ax.clear( ) # first clear everything in this axes
    #
    first_date = min( df_cases_deaths_7day_region.date )
    last_date = max( df_cases_deaths_7day_region.date )
    #
    df_cases_deaths_regions_7days_bef = df_cases_deaths_7day_region[
        df_cases_deaths_7day_region.days_from_beginning <= days_from_beginning ].copy( )
    df_cases_deaths_regions_7days_aft = df_cases_deaths_7day_region[
        df_cases_deaths_7day_region.days_from_beginning >= days_from_beginning ].copy( )
    df_cases_deaths_regions_1days_bef = df_cases_deaths_1day_region[
        df_cases_deaths_1day_region.days_from_beginning <= days_from_beginning ].copy( )
    #
    ## before, full solid color plot
    df_cases_deaths_regions_7days_bef.plot(
         'days_from_beginning', 'cases_new', linewidth = 4.5,
        ax = ax, logy = True, grid = True, color = 'C0' )
    df_cases_deaths_regions_7days_bef.plot(
         'days_from_beginning', 'death_new', linewidth = 4.5,
        ax = ax, logy = True, grid = True, color = 'C1' )
    #
    ## before, alpha = 0.3 solid color plot 1 day average
    df_cases_deaths_regions_1days_bef.plot(
        'days_from_beginning', 'cases_new', linewidth = 4.5,
        ax = ax, logy = True, grid = True, alpha = 0.3, color = 'C0' )
    df_cases_deaths_regions_1days_bef.plot(
        'days_from_beginning', 'death_new', linewidth = 4.5,
        ax = ax, logy = True, grid = True, alpha = 0.3, color = 'C1' )
    #
    ## after, alpha = 0.5
    df_cases_deaths_regions_7days_aft.plot(
         'days_from_beginning', 'cases_new', linewidth = 4.5,
        ax = ax, logy = True, grid = True, alpha = 0.5, color = 'C0' )
    df_cases_deaths_regions_7days_aft.plot(
         'days_from_beginning', 'death_new', linewidth = 4.5,
        ax = ax, logy = True, grid = True, alpha = 0.5, color = 'C1' )
    #
    ##
    df_dfm = df_cases_deaths_7day_region[
        df_cases_deaths_7day_region.days_from_beginning == days_from_beginning ]
    num_cases_new = df_dfm.cases_new.max( )
    num_death_new = df_dfm.death_new.max( )
    num_cases_new_max = df_cases_deaths_7day_region.cases_new.max( )
    num_death_new_max = df_cases_deaths_7day_region.death_new.max( )
    #
    ## now just do colors
    ax.lines[2].set_label( None )
    ax.lines[3].set_label( None )
    ax.lines[4].set_label( None )
    ax.lines[5].set_label( None )
    leg = ax.legend( )
    ax.scatter([ days_from_beginning ], [ num_cases_new ], s = 100, color = 'C0' )
    ax.scatter([ days_from_beginning ], [ num_death_new ], s = 100, color = 'C1' )
    ax.lines[0].set_label( '\n'.join([
        'new cases/day: %s' % get_string_commas_num_float( num_cases_new ),
        '%s (max)' % get_string_commas_num_float( num_cases_new_max ) ] ) )
    ax.lines[1].set_label( '\n'.join([
        'new death/day: %s' % get_string_commas_num_float( num_death_new ),
        '%s (max)' % get_string_commas_num_float( num_death_new_max ) ] ) )
    #
    ax.set_xlim(7.0, inc_data[ 'last day' ] )
    ax.set_ylim(1.0, 1.15 * df_cases_deaths_7day_region.cases_new.max( ) )
    ax.set_aspect( ( inc_data[ 'last day' ] - 7.0 ) /
                  numpy.log10( 1.15 * df_cases_deaths_7day_region.cases_new.max( ) ) *
                  aspect_ratio_mult )
    ax.set_xlabel(
        'Days from First COVID-19 CASE (%s)' %
        first_date.strftime( '%d-%m-%Y' ),
        fontsize = 18, fontweight = 'bold' )
    ax.set_ylabel( '7 Day Avg. New Cases/Deaths', fontsize = 18, fontweight = 'bold' )
    if doTitle:
        ax.set_title( '\n'.join(
            [
                '%s Trend in COVID-19 New Cases/Day' % titlecase.titlecase( regionName ),
                'through %d / %d days from beginning' % ( days_from_beginning, inc_data[ 'last day' ] )
            ]), fontsize = 18, fontweight = 'bold' )
    #
    ## text on last day
    ax.text( 0.02, 0.75, '\n'.join([
        'last day: %s' % last_date.strftime('%d-%m-%Y'),
        '%d days after first case' % inc_data[ 'last day' ] ]),
            transform = ax.transAxes, fontsize = 18, fontweight = 'bold',
            horizontalalignment = 'left', verticalalignment = 'center', color = 'purple' )
                                   
    ## tick labels size 20, bold
    for tick in ax.xaxis.get_major_ticks( ) + ax.yaxis.get_major_ticks( ):
        tick.label.set_fontsize( 14 )
        tick.label.set_fontweight( 'bold' )
    #
    ## legend size 24, bold
    leg = ax.legend( )
    for txt in leg.texts:
        txt.set_fontsize( int( 18 * legend_text_scaling ) )
        txt.set_fontweight( 'bold' )

def create_plots_rate_daysfrombeginning(
    inc_data, days_from_beginning = [ 7 ], dirname = os.getcwd( ) ):
    """
    This method is similar to :py:meth:`create_plots_daysfrombeginning <covid19_stats.engine.viz.create_plots_daysfrombeginning>` in the :py:mod:`viz <covid19_stats.engine.viz>` module. Creates a collection of quad PNG_ images (see :numref:`movie_mode_region_rate`) representing state of *seven day averaged* COVID-19 new cases/day and deaths/day for a geographical region. Like :ref:`movie mode <movie_mode_region_rate>` in :ref:`covid19_region_summary_rate`, the four quadrants are,

    * ``upper left`` is the summary information for the geographical region.
    * ``lower left`` is the running tally of *seven-day averaged* new cases/day and deaths/day, by day from first incident.
    * ``upper right`` is the *logarithmic* coloration of new deaths/day, by day from first incident.
    * ``lower right`` is the *logarithmic* coloration of new cases/day, by day from first incident.

    :py:meth:`create_summary_rate_movie_frombeginning <covid19_stats.engine.viz2.create_summary_rate_movie_frombeginning>` uses this functionality in a multiprocessing fashion to create MP4_ movie files for geographical regions. It is easier to show rather than tell. :numref:`viz2_create_plots_rate_daysfrombeginning_nyc` is a quad plot of COVID-19 new cases/day and deaths/day for the NYC metro area, 150 days after this metro's first COVID-19 incident, that is created by this function.

    .. _viz2_create_plots_rate_daysfrombeginning_nyc:
    
    .. figure:: /_static/viz2/covid19_7day_nyc_LATEST.0143.png
       :width: 100%
       :align: left

       Quad plot of *seven day averaged* COVID-19 new cases/day and deaths/day for the NYC metro area, 150 days after its first incident. The name of the file is ``covid19_nyc_LATEST.0143.png`` (150 days minus 7 days), so that FFmpeg_ can easily create movies; frames must start from *all zeros* in the file name, so day 7 would be ``0000``.

    The collection of PNG_ images that this method creates are auto-cropped and, where needed, *resized* so that their widths and heights are even numbers. FFmpeg_, run through :py:meth:`create_summary_rate_movie_frombeginning <covid19_stats.engine.viz2.create_summary_rate_movie_frombeginning>`, cannot create an MP4_ from PNG_\ s unless the images' widths and heights are divisible by 2.

    :param dict inc_data: the data for incidence of COVID-19 cases and deaths for a given geographical region. See :py:meth:`get_incident_data <covid19_stats.engine.core.get_incident_data>` for the format of the output data.
    :param list days_from_beginning: the :py:class:`list` of days to create quad PNG_ images. Must be nonempty, and every element must be :math:`\ge 0`. Default is ``[ 0, ]``.
    :param str dirname: the directory into which to save the quad PNG_ images. The default is the current working directory.
    :returns: the :py:class:`list` of filenames of PNG_ quad images that this method creates, into ``dirname``. For example, in the method invocation shown in :numref:`viz2_create_plots_rate_daysfrombeginning_nyc`, ``days_from_beginning = [ 150, ]``, and the list this method returns is ``[ '<dirname>/covid19_nyc_LATEST.0143.png', ]``.
    :rtype: list

    .. _PNG: https://en.wikipedia.org/wiki/Portable_Network_Graphics
    .. _MP4: https://en.wikipedia.org/wiki/MPEG-4_Part_14
    .. _FFmpeg: https://en.wikipedia.org/wiki/FFmpeg
    """
    assert( 'region name' in inc_data )
    assert( 'prefix' in inc_data )
    assert( os.path.isdir( dirname ) )
    regionName = inc_data[ 'region name' ]
    prefix = inc_data[ 'prefix' ]
    doSmarter = False
    if prefix == 'conus': doSmarter = True
    fig = Figure( )
    #
    ## first plot, get correct width multiplication
    sorted_days = sorted( filter(lambda day: day >= 7, set( days_from_beginning ) ) )
    first_day = min( days_from_beginning )
    plot_artists = { }
    plot_cases_or_deaths_rate_bycounty(
        inc_data, fig, type_disp = 'deaths',
        days_from_beginning = first_day, doTitle = False,
        plot_artists = plot_artists, doSmarter = doSmarter )
    ax_deaths = plot_artists[ 'axes' ]
    ratio_width_height = ax_deaths.get_xlim( )[1] / ax_deaths.get_ylim( )[1]
    height_units = 2.0
    width_units = 1 + ratio_width_height
    #
    ## get collection of filenames to return
    fnames = [ ]
    #
    ## now create a figure of correct size, just trialing and erroring it
    fig = Figure( )
    fig.set_size_inches([ 18.0 * width_units / height_units, 18.0 * 0.8 ] )
    ax_cd = fig.add_subplot(223)
    #
    ## now plots
    death_plot_artists = { }
    cases_plot_artists = { }
    plot_cases_or_deaths_rate_bycounty(
        inc_data, fig, type_disp = 'deaths',
        days_from_beginning = first_day, doTitle = False,
        legend_text_scaling = 0.5,
        plot_artists = death_plot_artists, doSmarter = doSmarter,
        rows = 2, cols = 2, num = 2 )
    plot_cases_or_deaths_rate_bycounty(
        inc_data, fig, type_disp = 'cases',
        days_from_beginning = first_day, doTitle = False,
        legend_text_scaling = 0.5,
        plot_artists = cases_plot_artists, doSmarter = doSmarter,
        rows = 2, cols = 2, num = 4 )
    plot_cases_deaths_rate_region(
        inc_data, ax_cd, days_from_beginning = first_day, doTitle = False,
        legend_text_scaling = 0.5,
        aspect_ratio_mult = 0.8 * height_units / width_units ) # so not so square
    #
    ## legend plot
    df_cases_deaths_7day_region = inc_data[ 'df_7day' ]
    first_date = min( df_cases_deaths_7day_region.date )
    last_date = max( df_cases_deaths_7day_region.date )
    max_fips_cases_rate = max(
        map(lambda fips: (
            fips, df_cases_deaths_7day_region[ 'cases_%s_7day_new' % fips ].max( ) ),
            inc_data['fips'] ),
        key = lambda fips_case: fips_case[1] )
    fips_max, cases_rate_max = max_fips_cases_rate
    cs = core.get_county_state( fips_max )
    ax_leg = fig.add_subplot(221)
    ax_leg.set_aspect( ratio_width_height )
    ax_leg.axis('off')
    ax_leg_txt = ax_leg.text(-0.1, 1.0, '\n'.join([
        regionName,
        'First COVID-19 CASE: %s' % first_date.strftime( '%d-%m-%Y' ),
        'Latest COVID-19 CASE: %s' % last_date.strftime( '%d-%m-%Y' ),
        'Most County Cases/Day: %s' % get_string_commas_num_float( cases_rate_max ),
        '%s, %s' % ( cs['county'], cs['state'] ),
        'Showing Day %d / %d' % ( first_day, inc_data[ 'last day' ] ) ]),
                fontsize = 24, fontweight = 'bold', transform = ax_leg.transAxes,
                horizontalalignment = 'left', verticalalignment = 'top' )
    canvas = FigureCanvasAgg( fig )
    fname = os.path.join( dirname, 'covid19_7day_%s_LATEST.%04d.png' % (
        prefix, first_day - 7 ) )
    canvas.print_figure( fname, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( fname, fixEven = True )
    fnames.append( fname )
    #
    ## now do for the remaining days
    for day in sorted_days[1:]:
        plot_cases_or_deaths_rate_bycounty(
            inc_data, fig, type_disp = 'deaths',
            days_from_beginning = day, doTitle = False,
            plot_artists = death_plot_artists,
            rows = 2, cols = 2, num = 2 )
        plot_cases_or_deaths_rate_bycounty(
            inc_data, fig, type_disp = 'cases',
            days_from_beginning = day, doTitle = False,
            plot_artists = cases_plot_artists,
            rows = 2, cols = 2, num = 4 )
        plot_cases_deaths_rate_region(
            inc_data, ax_cd,
            days_from_beginning = day, doTitle = False,
            legend_text_scaling = 0.5,
            aspect_ratio_mult = 0.8 * height_units / width_units ) # so not so square
        ax_leg_txt.set_text( '\n'.join([
            regionName,
            'First COVID-19 CASE: %s' % first_date.strftime( '%d-%m-%Y' ),
            'Latest COVID-19 CASE: %s' % last_date.strftime( '%d-%m-%Y' ),
            'Most County Cases/Day: %s' % get_string_commas_num_float( cases_rate_max ),
            '%s, %s' % ( cs['county'], cs['state'] ),
            'Showing Day %d / %d' % ( day, inc_data[ 'last day' ] ) ]) )
        canvas = FigureCanvasAgg( fig )
        fname = os.path.join( dirname, 'covid19_7day_%s_LATEST.%04d.png' % (
            prefix, day - 7 ) )
        canvas.print_figure( fname, bbox_inches = 'tight' )
        autocrop_image.autocrop_image( fname, fixEven = True )
        fnames.append( fname )
    return fnames

def create_summary_cases_or_deaths_rate_movie_frombeginning(
    inc_data, type_disp = 'cases', dirname = os.getcwd( ), save_imgfiles = False ):
    """
    This method is similar to :py:meth:`create_summary_cases_or_deaths_movie_frombeginning <covid19_stats.engine.viz.create_summary_cases_or_deaths_movie_frombeginning>` in the :py:mod:`viz <covid19_stats.engine.viz>` module. This is the back-end method for :ref:`movie cases deaths mode <movie_cases_deaths_mode_region_rate>` for :ref:`covid19_region_summary_rate`. This creates an MP4_ movie file of *seven-day averaged* COVID-19 new cases/day *or* deaths/day, with identifying metadata, for a given geographical region. :numref:`viz2_create_summary_cases_or_deaths_rate_movie_frombeginning_table` shows the *resulting* MP4_ movie files, of cumulative COVID-19 cases and deaths, for the NYC metro area (top row), and the state of Virginia_ (bottom row).

    .. _viz2_create_summary_cases_or_deaths_rate_movie_frombeginning_table:

    .. list-table:: Latest *seven-day averaged* COVID-19 new cases/day, and deaths/day, for the NYC metro area and Virginia_
       :widths: auto

       * - |covid19_7day_nyc_cases|
         - |covid19_7day_nyc_deaths|
       * - NYC metro area, latest movie of COVID-19 new cases/day
         - NYC metro area, latest movie of COVID-19 new deaths/day
       * - |covid19_7day_virginia_cases|
         - |covid19_7day_virginia_deaths|
       * - Virginia_, latest movie of COVID-19 new cases/day
         - Virginia_, latest movie of COVID-19 new deaths/day

    Here are the arguments,

    :param dict inc_data: the data for incidence of COVID-19 cases and deaths for a given geographical region. See :py:meth:`get_incident_data <covid19_stats.engine.core.get_incident_data>` for the format of the output data.
    :param type_disp: if ``cases``, then show cumulative COVID-19 cases. If ``deaths``, then show cumulative COVID-19 deaths. Can only be ``cases`` or ``deaths``.
    :param str dirname: the directory into which to save the MP4_ movie file, and optionally a `zip archive`_ of the PNG_ image files used to create the MP4_ movie. The default is the current working directory.
    :param bool save_imgfiles: if ``True``, then will create a `zip archive`_ of the PNG_ image files used to create the MP4_ movie. Its full name is ``<dirname>/covid19_7day_<prefix>_<type_disp>_LATEST_imagefiles.zip``. ``<dirname>`` is the directory to save the MP4_ file, ``<prefix>`` is the region name prefix (for example ``nyc`` for the NYC metro area) located in ``inc_data['prefix']``, and ``<type_disp>`` is either ``cases`` or ``death``. The default is ``False``.
    :returns: the base name of the MP4_ movie file it creates. For example, if ``inc_data['prefix']`` is ``nyc`` and ``type_disp`` is ``cases``, this method returns ``covid19_7day_nyc_cases_LATEST.mp4``. This method also saves the MP4_ file as ``<dirname>/covid19_7day_nyc_cases_LATEST.mp4``, where ``<dirname>`` is the directory to save the MP4_ file.
    :rtype: str

    .. |covid19_7day_nyc_cases| raw:: html
       
       <video controls width="100%">
       <source src="https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_7day_nyc_cases_LATEST.mp4">
       </video>

    .. |covid19_7day_nyc_deaths| raw:: html
       
       <video controls width="100%">
       <source src="https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_7day_nyc_deaths_LATEST.mp4">
       </video>

    .. |covid19_7day_virginia_cases| raw:: html
       
       <video controls width="100%">
       <source src="https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_7day_virginia_cases_LATEST.mp4">
       </video>

    .. |covid19_7day_virginia_deaths| raw:: html
       
       <video controls width="100%">
       <source src="https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_7day_virginia_deaths_LATEST.mp4">
       </video>

    .. _Virginia: https://en.wikipedia.org/wiki/Virginia
    .. _`zip archive`: https://en.wikipedia.org/wiki/ZIP_(file_format)
    """
    assert( type_disp in ( 'cases', 'deaths' ) )
    assert( os.path.isdir( dirname ) )
    #
    ## barf out if cannot find ffmpeg
    ffmpeg_exec = find_executable( 'ffmpeg' )
    if ffmpeg_exec is None:
        raise ValueError("Error, ffmpeg could not be found." )
    #
    ## create directory
    tmp_dirname = tempfile.mkdtemp( suffix = 'covid19' )
    #
    prefix = inc_data[ 'prefix' ]
    regionName = inc_data[ 'region name' ]
    last_date = max( inc_data['df_7day'].date )
    #
    all_days_from_begin = list(range(7, inc_data['last day'] + 1 ) )
    numprocs = multiprocessing.cpu_count( )
    if prefix != 'conus': input_status = { 'doSmarter' : False }
    else: input_status = { 'doSmarter' : True }
    def myfunc( input_tuple ):
        days_collection, i_status = input_tuple
        time00 = i_status[ 'time00' ]
        doSmarter = i_status[ 'doSmarter' ]
        procno = i_status[ 'procno' ]
        numprocs = i_status[ 'numprocs' ]
        days_coll_sorted = sorted( days_collection )
        fig = Figure( )
        fig.set_size_inches([24,18])
        ax = fig.add_subplot(111)
        plot_artists = { }
        fnames = [ ]
        for day in sorted( set( days_collection ) ):
            plot_cases_or_deaths_rate_bycounty(
                inc_data, fig, type_disp = type_disp, days_from_beginning = day,
                doSmarter = doSmarter, plot_artists = plot_artists )
            canvas = FigureCanvasAgg( fig )
            fname = os.path.join( tmp_dirname, 'covid19_7day_%s_%s_LATEST.%04d.png' % (
                prefix, type_disp, day - 7 ) )
            canvas.print_figure( fname, bbox_inches = 'tight' )
            autocrop_image.autocrop_image( fname, fixEven = True )
            fnames.append( fname )
        logging.info( 'took %0.3f seconds to process all %d days owned by process %d / %d.' % (
            time.time( ) - time00, len( fnames ), procno, numprocs ) )
        return fnames

    input_status[ 'time00' ] = time.time( )
    with multiprocessing.Pool( processes = numprocs ) as pool:
        input_tuples = list(zip(map(lambda idx: all_days_from_begin[idx::numprocs], range(numprocs)),
                                map(lambda idx: {
                                    'time00' : input_status[ 'time00' ],
                                    'doSmarter' : input_status[ 'doSmarter' ],
                                    'procno' : idx + 1,
                                    'numprocs' : numprocs }, range(numprocs))))
        for tup in input_tuples:
            days_collection, i_status = tup
            if any(filter(lambda day: day < 0, days_collection ) ):
                logging.info( 'error days collection: %s.' % days_collection )
        allfiles = sorted(chain.from_iterable( pool.map(
            myfunc, input_tuples ) ) )
    logging.info( 'took %0.3f seconds to process all %d days.' % (
        time.time( ) - input_status[ 'time00' ], len( all_days_from_begin ) ) )
    #
    ## now make the movie
    allfiles_prefixes = set(map(
        lambda fname: '.'.join(os.path.basename( fname ).split('.')[:-2]), allfiles))
    assert( len( allfiles_prefixes ) == 1 )
    movie_prefix = max( allfiles_prefixes )
    movie_name = os.path.abspath( os.path.join( dirname, '%s.mp4' % movie_prefix ) )
    allfile_name = os.path.join( tmp_dirname, '%s.%%04d.png' % movie_prefix )
    #
    ## thank instructions from https://hamelot.io/visualization/using-ffmpeg-to-convert-a-set-of-images-into-a-video/
    ## make MP4 movie, 5 fps, quality = 25
    stdout_val = subprocess.check_output([
        ffmpeg_exec, '-y', '-r', '5', '-f', 'image2', '-i', allfile_name,
        '-vcodec', 'libx264', '-crf', '25', '-pix_fmt', 'yuv420p',
        movie_name ], stderr = subprocess.STDOUT )
    #
    ## if saving the image files
    if save_imgfiles:
        with zipfile.ZipFile( os.path.join( dirname, '%s_imagefiles.zip' % movie_prefix ), mode = 'w',
                             compression = zipfile.ZIP_DEFLATED, compresslevel = 9 ) as zf:
            for fname in allfiles: zf.write( fname, arcname = os.path.join(
                '%s_imagefiles' % movie_prefix, os.path.basename( fname ) ) )
    #
    ## now later remove those images and then remove the directory
    list(map(lambda fname: os.remove( fname ), allfiles ) )
    shutil.rmtree( tmp_dirname )
    #
    ## store metadata
    mp4tags = mutagen.mp4.MP4( movie_name )
    mp4tags['\xa9nam'] = [ '%s, %s 7 day new, %s' % ( prefix, type_disp.upper( ), last_date.strftime('%d-%m-%Y') ) ]
    mp4tags['\xa9alb'] = [ core.get_mp4_album_name( inc_data ), ]
    mp4tags['\xa9ART'] = [ 'Tanim Islam' ]
    mp4tags['\xa9day'] = [ last_date.strftime('%d-%m-%Y') ]
    mp4tags.save( )
    os.chmod( movie_name, 0o644 )
    return os.path.basename( movie_name ) # for now return basename        

def create_summary_rate_movie_frombeginning(
    inc_data, dirname = os.getcwd( ), save_imgfiles = False ):
    """
    This method is similar to :py:meth:`create_summary_rate_movie_frombeginning <covid19_stats.engine.viz.create_summary_rate_movie_frombeginning>` in the :py:mod:`viz <covid19_stats.engine.viz>` module. This is the back-end method for :ref:`movie mode <movie_mode_region_rate>` for :ref:`covid19_region_summary_rate`. This creates an MP4_ quad movie file of both *seven day averaged* COVID-19 new cases/day and deaths/day for a geographical region, and *optionally* a `zip archive`_ of PNG_ images used to create the MP4_ file. This uses :py:meth:`create_plots_rate_daysfrombeginning <covid19_stats.engine.viz2.create_plots_rate_daysfrombeginning>` in a multiprocessing fashion, to create sub-collections of PNG_ quad images, and then collate them into an MP4_ file using FFmpeg_. :numref:`viz2_create_summary_rate_movie_frombeginning_table` shows the *resulting* MP4_ movie files, of *seven day averged* COVID-19 new cases/day and deaths/day, for the NYC metro area and the state of Virginia_.

    .. _viz2_create_summary_rate_movie_frombeginning_table:

    .. list-table:: Latest quad movies of COVID-19 for the NYC metro area and Virginia_
       :widths: auto

       * - |covid19_7day_nyc_quad|
         - |covid19_7day_virginia_quad|
       * - NYC metro area, latest quad movie of COVID-19 new cases/day and deaths/day
         - Virginia_, latest quad movie of COVID-19 new cases/day and deaths/day

    Here are the arguments,

    :param dict inc_data: the data for incidence of COVID-19 cases and deaths for a given geographical region. See :py:meth:`get_incident_data <covid19_stats.engine.core.get_incident_data>` for the format of the output data.
    :param str dirname: the directory into which to save the MP4_ movie file, and optionally a `zip archive`_ of the PNG_ image files used to create the MP4_ movie. The default is the current working directory.
    :param bool save_imgfiles: if ``True``, then will create a `zip archive`_ of the PNG_ image files used to create the MP4_ movie. Its full name is ``<dirname>/covid19_7day_<prefix>_LATEST_imagefiles.zip``. ``<dirname>`` is the directory to save the MP4_ file, and ``<prefix>`` is the region name prefix (for example ``nyc`` for the NYC metro area) located in ``inc_data['prefix']``. The default is ``False``.
    :returns: the base name of the MP4_ movie file it creates. For example, if ``inc_data['prefix']`` is ``nyc``, this method returns ``covid19_7day_nyc_LATEST.mp4``. This method also saves the MP4_ file as ``<dirname>/covid19_7day_nyc_LATEST.mp4``, where ``<dirname>`` is the directory to save the MP4_ file.
    :rtype: str

    .. |covid19_7day_nyc_quad| raw:: html
       
       <video controls width="100%">
       <source src="https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_7day_nyc_LATEST.mp4">
       </video>

    .. |covid19_7day_virginia_quad| raw:: html
       
       <video controls width="100%">
       <source src="https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_7day_virginia_LATEST.mp4">
       </video>
    """
    #
    ## make sure dirname is a directory
    assert( os.path.isdir( dirname ) )
    #
    ## barf out if cannot find ffmpeg
    ffmpeg_exec = find_executable( 'ffmpeg' )
    if ffmpeg_exec is None:
        raise ValueError("Error, ffmpeg could not be found." )
    #
    ## create directory
    tmp_dirname = tempfile.mkdtemp( suffix = 'covid19' )
    #
    last_date = max( inc_data['df_7day'].date )
    prefix = inc_data[ 'prefix' ]
    regionName = inc_data[ 'region name' ]
    #
    all_days_from_begin = list(range(7, inc_data['last day'] + 1 ) )
    numprocs = multiprocessing.cpu_count( )
    if prefix != 'conus': input_status = { 'doSmarter' : False }
    else: input_status = { 'doSmarter' : True }
    def myfunc( input_tuple ):
        days_collection, i_status = input_tuple
        time00 = i_status[ 'time00' ]
        doSmarter = i_status[ 'doSmarter' ]
        procno = i_status[ 'procno' ]
        numprocs = i_status[ 'numprocs' ]
        fnames = create_plots_rate_daysfrombeginning(
            inc_data, dirname = tmp_dirname,
            days_from_beginning = days_collection )
        logging.info( 'took %0.3f seconds to process all %d days owned by process %d / %d.' % (
            time.time( ) - time00, len( fnames ), procno, numprocs ) )
        return fnames
    #
    ## first make all the plots
    input_status[ 'time00' ] = time.time( )
    with multiprocessing.Pool( processes = numprocs ) as pool:
        input_tuples = list(zip(map(lambda idx: all_days_from_begin[idx::numprocs], range(numprocs)),
                                map(lambda idx: {
                                    'time00' : input_status[ 'time00' ],
                                    'doSmarter' : input_status[ 'doSmarter' ],
                                    'procno' : idx + 1,
                                    'numprocs' : numprocs }, range(numprocs))))
        for tup in input_tuples:
            days_collection, _ = tup
            if any(filter(lambda day: day < 0, days_collection ) ):
                logging.info( 'error days collection: %s.' % days_collection )
        allfiles = sorted(chain.from_iterable( pool.map( myfunc, input_tuples ) ) )
    logging.info( 'took %0.3f seconds to process all %d days.' % (
        time.time( ) - input_status['time00'], len( all_days_from_begin ) ) )
    #
    ## now make the movie
    allfiles_prefixes = set(map(
        lambda fname: '.'.join(os.path.basename( fname ).split('.')[:-2]), allfiles))
    assert( len( allfiles_prefixes ) == 1 )
    movie_prefix = max( allfiles_prefixes )
    movie_name = os.path.abspath( os.path.join( dirname, '%s.mp4' % movie_prefix ) )
    allfile_name = os.path.join( tmp_dirname, '%s.%%04d.png' % movie_prefix )
    #
    ## thank instructions from https://hamelot.io/visualization/using-ffmpeg-to-convert-a-set-of-images-into-a-video/
    ## make MP4 movie, 5 fps, quality = 25
    stdout_val = subprocess.check_output([
        ffmpeg_exec, '-y', '-r', '5', '-f', 'image2', '-i', allfile_name,
        '-vcodec', 'libx264', '-crf', '25', '-pix_fmt', 'yuv420p',
        movie_name ], stderr = subprocess.STDOUT )
    #
    ## if saving the image files
    if save_imgfiles:
        with zipfile.ZipFile( os.path.join( dirname, '%s_imagefiles.zip' % movie_prefix ), mode = 'w',
                             compression = zipfile.ZIP_DEFLATED, compresslevel = 9 ) as zf:
            for fname in allfiles: zf.write( fname, arcname = os.path.join(
                '%s_imagefiles' % movie_prefix, os.path.basename( fname ) ) )
    #
    ## now later remove those images and then remove the directory
    list(map(lambda fname: os.remove( fname ), allfiles ) )
    shutil.rmtree( tmp_dirname )
    #
    ## store metadata
    mp4tags = mutagen.mp4.MP4( movie_name )
    mp4tags['\xa9nam'] = [ '%s, ALL 7 day new, %s' % ( prefix, last_date.strftime('%d-%m-%Y') ) ]
    mp4tags['\xa9alb'] = [ core.get_mp4_album_name( inc_data ), ]
    mp4tags['\xa9ART'] = [ 'Tanim Islam' ]
    mp4tags['\xa9day'] = [ last_date.strftime('%d-%m-%Y') ]
    mp4tags.save( )
    os.chmod( movie_name, 0o644 )    
    return os.path.basename( movie_name )

def get_summary_demo_rate_data(
    inc_data, dirname = os.getcwd( ), store_data = True ):
    """
    This method is similar to :py:meth:`get_summary_demo_data <covid19_stats.engine.viz.get_summary_demo_data>` in the :py:mod:`viz <covid19_stats.engine.viz>` module. This is the back-end method for :ref:`show mode <show_mode_region_rate>` for :ref:`covid19_region_summary_rate`. This creates *six* or *eight* files for a given geographical region. Given an input ``inc_data`` :py:class:`dict`, it produces six files by default. Here ``prefix`` is the value of ``inc_data['prefix']`` (for example ``nyc`` for the NYC metro area).

    * ``covid19_7day_<prefix>_cases_LATEST.pdf`` and ``covid19_7day_<prefix>_cases_LATEST.png``: a PDF_ and PNG_ plot of the *latest* *seven day averaged* COVID-19 new cases/day for the geographical region.
    
    * ``covid19_7day_<prefix>_death_LATEST.pdf`` and ``covid19_7day_<prefix>_death_LATEST.png``: a PDF_ and PNG_ plot of the *latest* *seven day averaged* COVID-19 new deaths/day for the geographical region.

    * ``covid19_7day_<prefix>_cds_LATEST.pdf`` and ``covid19_7day_<prefix>_cds_LATEST.png``: a PDF_ and PNG_ plot of the *latest* *seven day averaged* COVID-19 new cases/day and deaths/day trend lines for the geographical region.

    Optionally, one can choose to dump out two serialized :py:class:`Pandas DataFrames <pandas.DataFrame>` of the new COVID-19 cases/day and deaths/day, total and per county.

    * ``covid19_7day_<prefix>_LATEST.pkl.gz`` is the *seven day averaged* serialized :py:class:`Pandas DataFrame <pandas.DataFrame>` for the region. This runs from the seventh day after first incident to the last day. An example for the NYC metro area is :download:`covid19_7day_nyc_LATEST.pkl.gz </_static/viz2/covid19_7day_nyc_LATEST.pkl.gz>`.

    * ``covid19_7day_<prefix>_LATEST.pkl.gz`` is the *one day averaged* serialized :py:class:`Pandas DataFrame <pandas.DataFrame>` for the region. This runs from the first day after the first incident to the last day. An example for the NYC metro area is :download:`covid19_1day_nyc_LATEST.pkl.gz </_static/viz2/covid19_1day_nyc_LATEST.pkl.gz>`.

    :numref:`viz2_get_summary_demo_rate_data_nyc` displays the *latest* output for the NYC metro area.

    .. _viz2_get_summary_demo_rate_data_nyc:

    .. list-table:: Latest plots of cumulative COVID-19 cases, deaths, and trend lines for the NYC metro area
       :widths: auto

       * - |covid19_7day_nyc_cases_latest|
         - |covid19_7day_nyc_death_latest|
         - |covid19_7day_nyc_cds_latest|
       * - NYC metro area, plot of latest COVID-19 new cases/day
         - NYC metro area, plot of latest COVID-19 new deaths/day
         - NYC metro area, plot of latest trend lines of COVID-19 new cases/day and deaths/day

    .. |covid19_7day_nyc_cases_latest| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_7day_nyc_cases_LATEST.png
       :width: 100%
       :align: middle
       
    .. |covid19_7day_nyc_death_latest| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_7day_nyc_death_LATEST.png
       :width: 100%
       :align: middle

    .. |covid19_7day_nyc_cds_latest| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_7day_nyc_cds_LATEST.png
       :width: 100%
       :align: middle

    Here are the arguments.

    :param dict inc_data: the data for incidence of COVID-19 cases and deaths for a given geographical region. See :py:meth:`get_incident_data <covid19_stats.engine.core.get_incident_data>` for the format of the output data.
    :param str dirname: the directory into which to save the six or seven files. The default is the current working directory.
    :param bool store_data: if ``True``, then create two serialized :py:class:`Pandas DataFrames <pandas.DataFrame>` of the COVID-19 cases and deaths, total and per county, up to the latest incident. Default is ``True``.

    .. _PDF: https://en.wikipedia.org/wiki/PDF
    """
    #
    ## now is dirname a directory
    assert( os.path.isdir( dirname ) )
    doSmarter = False
    if inc_data[ 'prefix' ] == 'conus': doSmarter = True
    prefix = inc_data[ 'prefix' ]
    regionName = inc_data[ 'region name' ]
    df_cases_deaths_7day_region = inc_data[ 'df_7day' ]
    df_cases_deaths_1day_region = inc_data[ 'df_1day' ]
    #
    first_date = min( df_cases_deaths_7day_region.date )
    last_date = max( df_cases_deaths_7day_region.date )
    #
    ## pickle this pandas data
    last_date_str = last_date.strftime('%d%m%Y' )
    if store_data:
        df_cases_deaths_7day_region.to_pickle(
            os.path.join( dirname, 'covid19_7day_%s_LATEST.pkl.gz' % prefix ) )
        df_cases_deaths_1day_region.to_pickle(
            os.path.join( dirname, 'covid19_1day_%s_LATEST.pkl.gz' % prefix ) )
        
    def create_plot_cds( ):
        #
        ## now make a plot, logarithmic
        fig = Figure( )
        ax = fig.add_subplot(111)
        fig.set_size_inches([ 12.0, 9.6 ])
        num_cases_new = df_cases_deaths_7day_region.cases_new.max( )
        num_death_new = df_cases_deaths_7day_region.death_new.max( )
        df_cases_deaths_1day_region_copy = df_cases_deaths_1day_region[
            df_cases_deaths_1day_region.date >= df_cases_deaths_7day_region.date.min( ) ].copy( )
        df_cases_deaths_7day_region.plot(
            'days_from_beginning', 'cases_new', linewidth = 4.5,
            ax = ax, logy = True, grid = True, color = 'C0' )
        df_cases_deaths_7day_region.plot(
            'days_from_beginning', 'death_new', linewidth = 4.5,
            ax = ax, logy = True, grid = True, color = 'C1' )
        df_cases_deaths_1day_region_copy.plot(
            'days_from_beginning', 'cases_new', linewidth = 4.5,
            ax = ax, logy = True, grid = True, color = 'C0', alpha = 0.3 )
        df_cases_deaths_1day_region_copy.plot(
            'days_from_beginning', 'death_new', linewidth = 4.5,
            ax = ax, logy = True, grid = True, color = 'C1', alpha = 0.3 )
        ax.lines[0].set_label( 'new cases/day (%s max)' % get_string_commas_num_float( num_cases_new ) )
        ax.lines[1].set_label( 'new death/day (%s max)' % get_string_commas_num_float( num_death_new ) )
        ax.lines[2].set_label( None )
        ax.lines[3].set_label( None )
        ax.set_ylim( 1.0, 1.05 * num_cases_new )
        ax.set_xlim( 7, df_cases_deaths_7day_region.days_from_beginning.max( ) )
        ax.set_xlabel(
            'Days from First COVID-19 CASE (%s)' %
            first_date.strftime( '%d-%m-%Y' ),
            fontsize = 24, fontweight = 'bold' )
        ax.set_ylabel( '7 Day Avg. Cases/Deaths', fontsize = 24, fontweight = 'bold' )
        ax.set_title( '\n'.join(
            [
             '%s Trend in COVID-19 New Cases/Days' % titlecase.titlecase( regionName ),
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
        canvas = FigureCanvasAgg( fig )
        file_prefix = 'covid19_7day_%s_cds_LATEST' % prefix
        pngfile = os.path.abspath( os.path.join( dirname, '%s.png' % file_prefix ) )
        pdffile = os.path.abspath( os.path.join( dirname, '%s.pdf' % file_prefix ) )
        canvas.print_figure( pngfile, bbox_inches = 'tight' )
        canvas.print_figure( pdffile, bbox_inches = 'tight' )
        autocrop_image.autocrop_image( pngfile )
        try: autocrop_image.autocrop_image_pdf( '%s.pdf' % file_prefix )
        except: pass
    #
    ## now create figures CASES and DEATHS
    def make_plot_and_save( case ):
        prefix_dict = { 'cases' : 'cases', 'deaths' : 'death' }
        assert( case in prefix_dict )
        file_prefix = 'covid19_7day_%s_%s_LATEST' % ( prefix, prefix_dict[ case ] )
        fig_mine = Figure( )
        fig_mine.set_size_inches([ 12.0, 12.0 ])
        plot_cases_or_deaths_rate_bycounty(
            inc_data, fig_mine, type_disp = case,
            days_from_beginning = inc_data[ 'last day' ],
            doTitle = True, doSmarter = doSmarter )
        canvas = FigureCanvasAgg( fig_mine )
        pngfile = os.path.abspath( os.path.join( dirname, '%s.png' % file_prefix ) )
        pdffile = os.path.abspath( os.path.join( dirname, '%s.pdf' % file_prefix ) )
        canvas.print_figure( pngfile, bbox_inches = 'tight' )
        canvas.print_figure( pdffile, bbox_inches = 'tight' )
        autocrop_image.autocrop_image( pngfile )
        try: autocrop_image.autocrop_image_pdf( pdffile )
        except: pass

    #
    ## do three plots in parallel!
    with multiprocessing.Pool( processes = 3 ) as pool:
        jobs = [
            pool.apply_async( create_plot_cds, ( ) ),
            pool.apply_async( make_plot_and_save, ( 'cases', ) ),
            pool.apply_async( make_plot_and_save, ( 'deaths', ) ) ]
        _ = list(map(lambda job: job.get( ), jobs ) )

