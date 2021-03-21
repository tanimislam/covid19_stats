import os, sys, numpy, titlecase, time, pandas, zipfile, mutagen.mp4
import subprocess, tempfile, shutil, datetime, logging, copy
import pathos.multiprocessing as multiprocessing
from itertools import chain
from multiprocessing import Value, Manager
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from matplotlib.axes import Axes
from matplotlib.patches import Polygon
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LogNorm, Normalize, to_rgba
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from mpl_toolkits.axes_grid1 import make_axes_locatable
from distutils.spawn import find_executable
from nprstuff.core import autocrop_image
#
from covid19_stats.engine import gis, core, get_string_commas_num

def my_colorbar( mappable, ax, **kwargs ):
    """
    secret saucing (explanation is incomprehensible) from https://joseph-long.com/writing/colorbars. I do not understand how it works the way it does, but it does! I shamelessly copy the method description from the :py:meth:`colorbar method <matplotlib.pyplot.colorbar>`. I have also updated this thing to `this website <https://stackoverflow.com/questions/30030328/correct-placement-of-colorbar-relative-to-geo-axes-cartopy>`_ that now works on :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`.

    :param mappable: a :py:class:`ScalarMappable <matplotlib.cm.ScalarMappable>` described by this colorbar.
    :param ax: the parent :py:class:`Axes <matplotlib.axes.Axes>` from whose space a new colorbar axes will be stolen.
    :returns: the underlying :py:class:`Colorbar <matplotlib.colorbar.Colorbar>`.
    :rtype: :py:class:`Colorbar <matplotlib.colorbar.Colorbar>`
    """
    fig = ax.figure
    divider = make_axes_locatable( ax )
    cax = divider.append_axes("right", size="5%", pad=0.05, axes_class = Axes )
    cbar = fig.colorbar(mappable, cax=cax, **kwargs)
    return cbar

def create_and_draw_fromfig(
    fig, bbox, river_linewidth = 5, river_alpha = 0.3,
    coast_linewidth = 2, coast_alpha = 0.4, drawGrid = True, mult_bounds_lat = 1.05,
    mult_bounds_lng = 1.05, rows = 1, cols = 1, num = 1 ):
    """
    This creates an :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`, with lots of physical geographic features, and optional (but turned on by default) latitude and longitude gridding, of a region specified by a bounding box. This uses `stereographic projection`_. For example, here is the :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` displaying the CONUS_.
    
    .. _viz_create_and_draw_fromfig_conus:

    .. figure:: /_static/viz/viz_create_and_draw_fromfig_conus.png
       :width: 100%
       :align: left

       Demonstrations of this functionality, which underlies (or overlays?) the geographical features for visualizing COVID-19 cases and deaths.

    Here are the arguments.

    :param fig: the :py:class:`Figure <matplotlib.figure.Figure>` onto which to create a :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` containing geographic features. Last three arguments -- ``rows``, ``cols``, and ``num`` -- describe the relative placement of the created :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`. See :py:meth:`add_subplot <matplotlib.figure.Figure.add_subplot>` for those three arguments' meanings.
    :param tuple bbox: a four-element :py:class:`tuple`. Elements in order are *minimum* longitude, *minimum* latitude, *maximum* longitude, and *maximum* latitude.
    :param int river_linewidth: the width, in pixels, of river geographical features.
    :param float river_alpha: the color alpha of river geographical features.
    :param int coast_linewidth: the width, in pixels, of the coast lines.
    :param float coast_alpha: the color alpha of coast lines.
    :param bool drawGrid: if ``True``, then overlay the latitude and longitude grid lines. Otherwise do not. Default is ``True``.
    :param float mult_bounds_lat: often times, especially with geographic regions that cover a significant area of the earth, we need to put a multiplier :math:`> 1` on the *latitudinal* extent of the plot, so that *all* features can be seen. By default this value is 1.05, but it must be :math:`\ge 1`.
    :param float mult_bounds_lng: often times, especially with geographic regions that cover a significant area of the earth, we need to put a multiplier :math:`> 1` on the *longitudinal* extent of the plot, so that *all* features can be seen. By default this value is 1.05, but it must be :math:`\ge 1`.
    :param int rows: the number of rows for axes in the :py:class:`Figure <matplotlib.figure.Figure>` grid. Must be :math:`\ge 1`, and by default is 1.
    :param int cols: the number of columns for axes in the :py:class:`Figure <matplotlib.figure.Figure>` grid. Must be :math:`\ge 1`, and by default is 1.
    :param int num: the plot number of the :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` in this :py:class:`Figure <matplotlib.figure.Figure>` grid. Must be :math:`\ge 1` and :math:`\le`\ ``rows`` times ``columns``. Its default is 1. Look at :py:meth:`add_subplot <matplotlib.figure.Figure.add_subplot>` for its  meaning.
    :rtype: :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`

    .. _`stereographic projection`: https://en.wikipedia.org/wiki/Stereographic_projection
    """
    assert( mult_bounds_lat >= 1.0 )
    assert( mult_bounds_lng >= 1.0 )
    assert( rows >= 1 )
    assert( cols >= 1 )
    assert( num >= 1 )
    assert( num <= rows * cols )
    #
    min_lng, min_lat, max_lng, max_lat = bbox
    lng_center = 0.5 * ( min_lng + max_lng )
    lat_center = 0.5 * ( min_lat + max_lat )
    lng_delta = mult_bounds_lng * ( max_lng - min_lng ) * 0.5
    lat_delta = mult_bounds_lat * ( max_lat - min_lat ) * 0.5
    #
    ax = fig.add_subplot(
        rows, cols, num, projection = ccrs.Stereographic(
            central_latitude = lat_center, central_longitude = lng_center ) )
    #
    ## now set the extent
    ax.set_extent( (
        lng_center - lng_delta, lng_center + lng_delta,
        lat_center - lat_delta, lat_center + lat_delta ) )
    #
    ## draw the grid lines if selected
    if drawGrid: ax.gridlines( draw_labels = True )
    #
    ## coastlines, linewidth = coast_linewidth, alpha = coast_alpha, is black
    ax.coastlines(
        linewidth = coast_linewidth,
        color = numpy.array([ 0.0, 0.0, 0.0, coast_alpha ]) )
    #
    ## rivers with linewidth = river_linewidth, alpha = river_alpha
    riverf = cfeature.NaturalEarthFeature(
        'physical', 'rivers_lake_centerlines', cfeature.auto_scaler,
        edgecolor = numpy.concatenate([ cfeature.COLORS['water'], [ river_alpha, ] ] ),
        facecolor='never', linewidth = river_linewidth )
    ax.add_feature( riverf )
    #
    ## lakes with alpha = river_alpha
    lakef = cfeature.NaturalEarthFeature(
        'physical', 'lakes', cfeature.auto_scaler,
        edgecolor = 'face',
        facecolor = numpy.concatenate([ cfeature.COLORS['water'], [ river_alpha, ] ]) )
    ax.add_feature( lakef )
    return ax

def display_fips_geom( fips_data, fig, **kwargs ):
    """
    Demonstrative plot, returning a :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`, of a FIPS data collection. For example, for the NYC Metro Area, this is,

    .. _viz_display_fips_geom_nyc:

    .. figure:: /_static/viz/viz_display_fips_geom_nyc.png
       :width: 100%
       :align: left

       Demonstration of this method showing the counties in the NYC Metro Area. One can extract the patches in this object to manually change the colors of these county polygons.
       
    Here are the arguments.

    :param dict fips_data: the :py:class:`dict` of FIPS geographic data. This has keys of ``prefix``, ``fips``, and ``population``. Look at :ref:`the St. Louis FIPS region data <stlouis_msa_example_data>` for its structure.
    :param fig: the :py:class:`Figure <matplotlib.figure.Figure>` onto which to draw this :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`.
    :rtype: :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`
    """
    bdict = core.get_boundary_dict( fips_data[ 'fips' ] )
    bbox = gis.calculate_total_bbox( chain.from_iterable( bdict.values( ) ) )
    ax = create_and_draw_fromfig( fig, bbox, **kwargs )
    fc = list( to_rgba( '#1f77b4' ) )
    fc[-1] = 0.25
    for fips in bdict:
        for shape in bdict[ fips ]:
            poly = Polygon(
                shape, closed = True,
                edgecolor = 'k', linewidth = 2.0, linestyle = 'dashed',
                facecolor = tuple(fc), alpha = 1.0, transform = ccrs.PlateCarree( ) )
            ax.add_patch( poly )
    return ax

def display_fips( collection_of_fips, fig, **kwargs ):
    """
    Method that is very similar to :py:meth:`display_fips_geom <covid19_stats.engine.viz.display_fips_geom>`, except this *also* displays the FIPS code of each county. For example, for `Rhode Island`_, this is.
    
    .. _viz_display_fips_rhodeisland:

    .. figure:: /_static/viz/viz_display_fips_rhodeisland.png
       :width: 100%
       :align: left

       Demonstration of this method showing the counties in `Rhode Island`_. The FIPS code of each county is shown in red. One can extract the patches in this object to manually change the colors of these county polygons.

    Here are the arguments.

    :param collection_of_fips: can be a :py:class:`list`, :py:class:`set`, or other iterable of FIPS codes to visualize and label.
    :param fig: the :py:class:`Figure <matplotlib.figure.Figure>` onto which to draw this :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`.
    :rtype: :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`

    .. _`Rhode Island`: https://en.wikipedia.org/wiki/Rhode_Island
    """
    bdict = core.get_boundary_dict( collection_of_fips )
    bbox = gis.calculate_total_bbox( chain.from_iterable( bdict.values( ) ) )
    ax = create_and_draw_fromfig( fig, bbox, **kwargs )
    fc = list( to_rgba( '#1f77b4' ) )
    fc[-1] = 0.25
    for fips in sorted( bdict ):
        for shape in bdict[ fips ]:
            poly = Polygon(
                shape, closed = True,
                edgecolor = 'k', linewidth = 2.0, linestyle = 'dashed',
                facecolor = tuple( fc ), alpha = 1.0, transform = ccrs.PlateCarree( ) )
            ax.add_patch( poly )
            lng_cent = shape[:,0].mean( )
            lat_cent = shape[:,1].mean( )
            ax.text(
                lng_cent, lat_cent, fips, fontsize = 10, fontweight = 'bold', color = 'red',
                transform = ccrs.PlateCarree( ) )
    return ax    

def display_msa( msaname, fig, doShow = False, **kwargs ):
    """
    Convenience method that visualizes and labels, by FIPS code, the counties in a `Metropolitan Statistical Area <msa_>`_. It can optionally save the output to a file, ``msa_<msaname>_counties.png``. Here is an example of the NYC Metro Area.

    .. _viz_display_msa_nyc:

    .. figure:: /_static/viz/viz_display_msa_nyc.png
       :width: 100%
       :align: left

       Display of the NYC Metro Area, with extra annotations beyond what :py:meth:`display_fips <covid19_stats.engine.viz.display_fips>` can do.

    Here are the arguments.

    :param str msaname: the identifying name for the `MSA <msa_>`_, for example ``nyc``.
    :param fig: the :py:class:`Figure <matplotlib.figure.Figure>` onto which to draw this :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`.
    :param bool doShow: if ``False``, then just display the figure. If ``True``, also save to a file, ``msa_<msaname>_counties.png``. Default is ``False``.
    :rtype: :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`

    .. _msa: https://en.wikipedia.org/wiki/Metropolitan_statistical_area
    """
    fig.set_size_inches([18,18])
    #
    data_msa = core.get_msa_data( msaname )
    bdict = core.get_boundary_dict( data_msa[ 'fips' ] )
    bbox = gis.calculate_total_bbox( chain.from_iterable( bdict.values( ) ) )
    ax = create_and_draw_fromfig( fig, bbox , **kwargs)
    fc = list( to_rgba( '#1f77b4' ) )
    fc[-1] = 0.25
    for fips in sorted( bdict ):
        for shape in bdict[ fips ]:
            poly = Polygon(
                shape, closed = True,
                edgecolor = 'k', linewidth = 2.0, linestyle = 'dashed',
                facecolor = tuple(fc), alpha = 1.0, transform = ccrs.PlateCarree( ) )
            ax.add_patch( poly )
            lng_cent = shape[:,0].mean( )
            lat_cent = shape[:,1].mean( )
            ax.text(
                lng_cent, lat_cent, fips, fontsize = 10, fontweight = 'bold', color = 'red',
                transform = ccrs.PlateCarree( ) )
    #
    ## now info on this MSA
    ax.text( 0.01, 0.98, 'COUNTIES IN %s.' % data_msa[ 'region name' ], fontsize = 20, fontweight = 'bold',
            transform = ax.transAxes, horizontalalignment = 'left', verticalalignment = 'top' )
    if not doShow: return ax
    #
    canvas = FigureCanvasAgg( fig )
    canvas.print_figure( 'msa_%s_counties.png' % msaname, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( 'msa_%s_counties.png' % msaname )
    return ax

def plot_cases_or_deaths_bycounty(
    inc_data, regionName, fig, type_disp = 'cases', days_from_beginning = 0,
    maxnum_colorbar = 5000.0, doTitle = True, plot_artists = { },
    poly_line_width = 1.0, doSmarter = False, rows = 1, cols = 1, num = 1 ):
    """
    The lower-level function that displays the status of COVID-19 cases or deaths given an incidident data :py:class:`dict`, ``inc_data``. It displays the status of cumulative COVID-19 cases or deaths, a specific number of days from the beginning, coloring the counties in that region according to the legend maximum, and places the resulting :py:class:`GeoAxes <cartopy.mpl.GeoAxes>` at a specific location in a :py:class:`Figure <matplotlib.figure.Figure>` grid of :py:class:`Axes <matplotlib.axes.Axes>` or :py:class:`GeoAxes <cartopy.mpl.GeoAxes>.

    Instead of returning a :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`, this initializes a :py:class:`dict` of matplotlib objects, ``plot_artists``. In this way, subsequent plots, e.g. for different days after the beginnning, do not have to perform the relatively costly operation of recreating the :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` and fully painting in the :py:class:`Polygon <matplotlib.patches.Polygon>` patches; instead, these :py:class:`Polygon <matplotlib.patches.Polygon>` patches are re-colored and necessary :py:class:`Text <matplotlib.text.Text>` artists' strings are changed.

    .. _plot_artists_dict_discussion:

    This :py:class:`dict`, ``plot_artists``, has the following keys,

    * ``axes``: when initialized, the :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` that consists of all counties, with COVID-19 cases or deaths, to display.
    * ``sm``: the :py:class:`ScalarMappable <matplotlib.cm.ScalarMappable>` describing the coloration by value for each county.

    Furthermore, it is easier to show rather than tell. :numref:`viz_plot_cases_or_deaths_bycounty_nyc` depicts both cumulative COVID-19 cases and deaths for the NYC metro area, 150 days after this metro's first COVID-19 incident.

    .. _viz_plot_cases_or_deaths_bycounty_nyc:

    .. figure:: /_static/viz/viz_plot_cases_or_deaths_bycounty_nyc.png
       :width: 100%
       :align: left

       On the left, is the COVID-19 cumulative cases, and on the right, is the COVID-19 cumulative deaths, for the NYC metro area, 150 days after its first COVID-19 incident. The color limits for cases (left) is :math:`1.7\\times 10^6`, while the color limits for death (right) is :math:`5.6\\times 10^4`. We have chosen to display the titles over both plots. Color scaling is logarithmic.

    Here are the arguments.
    
    :param dict inc_data: the data for incidence of COVID-19 cases and deaths for a given geographical region. See :py:meth:`get_incident_data <covid19_stats.engine.core.get_incident_data>` for the format of the output data.
    :param str regionName: the name of the region to display in title plots. For example, in :numref:`viz_plot_cases_or_deaths_bycounty_nyc`, this is ``NYC Metro Area``.
    :param fig: the :py:class:`Figure <matplotlib.figure.Figure>` onto which to create a :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` (stored into the ``plot_artists`` :py:class:`dict`) containing geographic features. Last three arguments -- ``rows``, ``cols``, and ``num`` -- describe the relative placement of the created :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>`. See :py:meth:`add_subplot <matplotlib.figure.Figure.add_subplot>` for those three arguments' meanings.
    :param str type_disp: if ``cases``, then show cumulative COVID-19 cases. If ``deaths``, then show cumulative COVID-19 deaths. Can only be ``cases`` or ``deaths``.
    :param int days_from_beginning: days after first incident of COVID-19 in this region. Must be :math:`\ge 0`.
    :param float maxnum_colorbar: the coloring limits for the plot. Must be :math:`\ge 1`.
    :param bool doTitle: if ``True``, then display the title over the plot. Default is ``True``.
    :param dict plot_artists: this contains the essential plotting objects for quicker re-display when plotting different days. Look at :ref:`this description <plot_artists_dict_discussion>`.
    :param float poly_line_width: the line width of the counties to draw in the plot.
    :param bool doSmarter: if ``False``, then make a plot tailored for small regions (relative to the size of the earth), such as states or MSA_\ s. If ``True``, then make a plot tailored for large regions such as the CONUS_. Default is ``False``.
    :param int rows: the number of rows for axes in the :py:class:`Figure <matplotlib.figure.Figure>` grid. Must be :math:`\ge 1`, and by default is 1.
    :param int cols: the number of columns for axes in the :py:class:`Figure <matplotlib.figure.Figure>` grid. Must be :math:`\ge 1`, and by default is 1.
    :param int num: the plot number of the :py:class:`GeoAxes <cartopy.mpl.geoaxes.GeoAxes>` in this :py:class:`Figure <matplotlib.figure.Figure>` grid. Must be :math:`\ge 1` and :math:`\le`\ ``rows`` times ``columns``. Its default is 1. Look at :py:meth:`add_subplot <matplotlib.figure.Figure.add_subplot>` for its  meaning.
    
    .. _MSA: https://en.wikipedia.org/wiki/Metropolitan_statistical_area
    .. _CONUS: https://en.wikipedia.org/wiki/Contiguous_United_States
    """
    cases_dict = { 'cases' : 'cases', 'deaths' : 'death' }
    assert( type_disp in cases_dict )
    assert( days_from_beginning >= 0 )
    assert( days_from_beginning <= inc_data[ 'last day' ] )
    assert( maxnum_colorbar > 1 )
    key = cases_dict[ type_disp ]
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
        plot_artists[ 'axes' ] = ax
        plot_artists[ 'sm' ] = ScalarMappable( norm = LogNorm( 1.0, maxnum_colorbar ), cmap = 'jet' )
    #
    ## after initialization
    df_dfm = inc_data['df'][ inc_data['df']['days_from_beginning'] == days_from_beginning ].copy( )
    ax = plot_artists[ 'axes' ]
    sm = plot_artists[ 'sm' ]
    for fips in sorted( boundaries ):
        nums = df_dfm['%s_%s' % ( type_disp, fips )].max( )
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
        cb.set_label( 'number of %s' % type_disp, fontsize = 18, fontweight = 'bold' )
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
                '%s cumulative %s' % ( type_disp, get_string_commas_num( num_tot ) ) ]),
            color = ( 0.0, 0.0, 0.0, 0.8 ),
            fontsize = 18, fontweight = 'bold', transform = ax.transAxes,
            horizontalalignment = 'left', verticalalignment = 'bottom' )
        plot_artists[ '%s_text' % key ] = txt
    else:
        plot_artists[ '%s_text' % key ].set_text('\n'.join([
            '%s' % date_s,
            '%d days from 1st case' % days_from_beginning,
            '%s cumulative %s' % ( type_disp, get_string_commas_num( num_tot ) ) ] ) )
            
    if doTitle:
        ax.set_title( '\n'.join([
            'Cumulative number of COVID-19 %s' % type_disp,
            'in %s after %d / %d days from start' % ( regionName, days_from_beginning, inc_data[ 'last day'] ) ] ),
                    fontsize = 18, fontweight = 'bold' )
        
def plot_cases_deaths_region( inc_data, regionName, ax, days_from_beginning = 0, doTitle = True ):
    assert( days_from_beginning >= 0 )
    assert( days_from_beginning <= inc_data[ 'last day' ] )
    df_cases_deaths_region = pandas.DataFrame({
        'date' : inc_data[ 'df' ].date,
        'cases' : inc_data[ 'df' ].cases,
        'death' : inc_data[ 'df' ].death,
        'days_from_beginning' : inc_data[ 'df' ].days_from_beginning } )
    ax.clear( ) # first clear everything in this axes
    #
    first_date = min( df_cases_deaths_region.date )
    last_date = max( df_cases_deaths_region.date )
    #
    df_cases_deaths_regions_bef = df_cases_deaths_region[
        df_cases_deaths_region.days_from_beginning <= days_from_beginning ].copy( )
    df_cases_deaths_regions_aft = df_cases_deaths_region[
        df_cases_deaths_region.days_from_beginning >= days_from_beginning ].copy( )
    #
    ## before, full solid color plot
    df_cases_deaths_regions_bef.plot(
         'days_from_beginning', 'cases', linewidth = 4.5,
        ax = ax, logy = True, grid = True )
    df_cases_deaths_regions_bef.plot(
         'days_from_beginning', 'death', linewidth = 4.5,
        ax = ax, logy = True, grid = True )
    #
    ## after, alpha = 0.5
    df_cases_deaths_regions_aft.plot(
         'days_from_beginning', 'cases', linewidth = 4.5,
        ax = ax, logy = True, grid = True, alpha = 0.5 )
    df_cases_deaths_regions_aft.plot(
         'days_from_beginning', 'death', linewidth = 4.5,
        ax = ax, logy = True, grid = True, alpha = 0.5 )
    #
    ##
    df_dfm = df_cases_deaths_regions_bef = df_cases_deaths_region[
        df_cases_deaths_region.days_from_beginning == days_from_beginning ]
    num_cases = df_dfm.cases.max( )
    num_death = df_dfm.death.max( )
    num_cases_tot = numpy.array( df_cases_deaths_region.cases )[-1]
    num_death_tot = numpy.array( df_cases_deaths_region.death )[-1]
    #
    ## now just do colors
    color_cases = ax.lines[0].get_color( )
    color_death = ax.lines[1].get_color( )
    ax.lines[2].set_label( None )
    ax.lines[3].set_label( None )
    leg = ax.legend( )
    ax.lines[2].set_color( color_cases )
    ax.lines[3].set_color( color_death )
    ax.scatter([ days_from_beginning ], [ df_dfm.cases.max( ) ], s = 100, color = color_cases )
    ax.scatter([ days_from_beginning ], [ df_dfm.death.max( ) ], s = 100, color = color_death )
    ax.lines[0].set_label( 'cases: %s / %s' % tuple(map(get_string_commas_num, (num_cases, num_cases_tot ) ) ) )
    ax.lines[1].set_label( 'death: %s / %s' % tuple(map(get_string_commas_num, (num_death, num_death_tot ) ) ) )
    #
    ax.set_xlim(0.0, inc_data[ 'last day' ] )
    ax.set_ylim(1.0, 1.15 * df_cases_deaths_region.cases.max( ) )
    ax.set_aspect( inc_data[ 'last day' ] / numpy.log10( 1.15 * df_cases_deaths_region.cases.max( ) ) )
    ax.set_xlabel(
        'Days from First COVID-19 CASE (%s)' %
        first_date.strftime( '%d-%m-%Y' ),
        fontsize = 18, fontweight = 'bold' )
    ax.set_ylabel( 'Cumulative Number of Cases/Deaths', fontsize = 18, fontweight = 'bold' )
    if doTitle:
        ax.set_title( '\n'.join(
            [
                '%s Trend in COVID-19' % titlecase.titlecase( regionName ),
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
        txt.set_fontsize( 18 )
        txt.set_fontweight( 'bold' )

def create_plots_daysfrombeginning(
    inc_data, regionName, prefix, days_from_beginning = [ 0 ],
    dirname = os.getcwd( ), maxnum_colorbar = 5000 ):
    assert( os.path.isdir( dirname ) )
    #assert(all(filter(lambda day: day >= 0, days_from_beginning ) ) )
    #assert(all(filter(lambda day: day <= inc_data[ 'last day' ], days_from_beginning ) ) )
    assert( maxnum_colorbar > 1 )
    doSmarter = False
    if prefix == 'conus': doSmarter = True
    fig = Figure( )
    #
    ## first plot, get correct width multiplication
    sorted_days = sorted( set( days_from_beginning ) )
    first_day = min( days_from_beginning )
    plot_artists = { }
    plot_cases_or_deaths_bycounty(
        inc_data, regionName, fig, type_disp = 'deaths',
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar,
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
    #ax_deaths = fig.add_subplot(222)
    #ax_cases = fig.add_subplot(224)
    ax_cd = fig.add_subplot(223)
    #
    ## now plots
    death_plot_artists = { }
    cases_plot_artists = { }
    plot_cases_or_deaths_bycounty(
        inc_data, regionName, fig, type_disp = 'deaths',
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar,
        plot_artists = death_plot_artists, doSmarter = doSmarter,
        rows = 2, cols = 2, num = 2 )
    plot_cases_or_deaths_bycounty(
        inc_data, regionName, fig, type_disp = 'cases',
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar,
        plot_artists = cases_plot_artists, doSmarter = doSmarter,
        rows = 2, cols = 2, num = 4 )
    plot_cases_deaths_region(
        inc_data, regionName, ax_cd,
        days_from_beginning = first_day, doTitle = False )
    #
    ## legend plot
    df_cases_deaths_region = inc_data[ 'df' ]
    first_date = min( df_cases_deaths_region.date )
    last_date = max( df_cases_deaths_region.date )
    max_fips_cases = max( map(lambda key: (
        key.replace('cases_','').strip( ),
        df_cases_deaths_region[ key ].max( ) ),
       filter(lambda key: key.startswith('cases_'), df_cases_deaths_region)),
      key = lambda fips_case: fips_case[1] )
    fips_max, cases_max = max_fips_cases
    cs = core.get_county_state( fips_max )
    ax_leg = fig.add_subplot(221)
    ax_leg.set_aspect( 1.0 )
    ax_leg.axis('off')
    ax_leg_txt = ax_leg.text(-0.1, 1.0, '\n'.join([
        regionName,
        'First COVID-19 CASE: %s' % first_date.strftime( '%d-%m-%Y' ),
        'Latest COVID-19 CASE: %s' % last_date.strftime( '%d-%m-%Y' ),
        'Most County Cases: %s' % get_string_commas_num( cases_max ),
        '%s, %s' % ( cs['county'], cs['state'] ),
        'Showing Day %d / %d' % ( first_day, inc_data[ 'last day' ] ) ]),
                fontsize = 24, fontweight = 'bold', transform = ax_leg.transAxes,
                horizontalalignment = 'left', verticalalignment = 'top' )
    canvas = FigureCanvasAgg( fig )
    fname = os.path.join( dirname, 'covid19_%s_LATEST.%04d.png' % (
        prefix, first_day ) ) # last_date.strftime('%d%m%Y')
    canvas.print_figure( fname, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( fname, fixEven = True )
    fnames.append( fname )
    #
    ## now do for the remaining days
    for day in sorted_days[1:]:
        plot_cases_or_deaths_bycounty(
            inc_data, regionName, fig, type_disp = 'deaths',
            days_from_beginning = day, doTitle = False,
            maxnum_colorbar = maxnum_colorbar,
            plot_artists = death_plot_artists,
            rows = 2, cols = 2, num = 2 )
        plot_cases_or_deaths_bycounty(
            inc_data, regionName, fig, type_disp = 'cases',
            days_from_beginning = day, doTitle = False,
            maxnum_colorbar = maxnum_colorbar,
            plot_artists = cases_plot_artists,
            rows = 2, cols = 2, num = 4)
        plot_cases_deaths_region(
            inc_data, regionName, ax_cd,
            days_from_beginning = day, doTitle = False )
        ax_leg_txt.set_text( '\n'.join([
            regionName,
            'First COVID-19 CASE: %s' % first_date.strftime( '%d-%m-%Y' ),
            'Latest COVID-19 CASE: %s' % last_date.strftime( '%d-%m-%Y' ),
            'Most County Cases: %s' % get_string_commas_num( cases_max ),
            '%s, %s' % ( cs['county'], cs['state'] ),
            'Showing Day %d / %d' % ( day, inc_data[ 'last day' ] ) ]) )
        canvas = FigureCanvasAgg( fig )
        fname = os.path.join( dirname, 'covid19_%s_LATEST.%04d.png' % (
            prefix, day ) ) # last_date.strftime('%d%m%Y')
        canvas.print_figure( fname, bbox_inches = 'tight' )
        autocrop_image.autocrop_image( fname, fixEven = True )
        fnames.append( fname )
    return fnames

def create_summary_cases_or_deaths_movie_frombeginning(
    inc_data, maxnum_colorbar = 5000.0,
    type_disp = 'cases', dirname = os.getcwd( ), save_imgfiles = False ):
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
    counties_and_states = list( map( core.get_county_state, inc_data[ 'fips' ] ) )
    last_date = max( inc_data['df'].date )
    #
    all_days_from_begin = list(range(inc_data['last day'] + 1 ) )
    numprocs = multiprocessing.cpu_count( )
    if inc_data['prefix'] != 'conus': input_status = { 'doSmarter' : False }
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
        plot_artists = { }
        fnames = [ ]
        for day in sorted( set( days_collection ) ):
            plot_cases_or_deaths_bycounty(
                inc_data, regionName, fig, type_disp = type_disp, days_from_beginning = day,
                doSmarter = doSmarter, plot_artists = plot_artists )
            canvas = FigureCanvasAgg( fig )
            fname = os.path.join( tmp_dirname, 'covid19_%s_%s_LATEST.%04d.png' % (
                prefix, type_disp, day ) ) # last_date.strftime( '%d%m%Y' )
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
    mp4tags['\xa9nam'] = [ '%s, %s, %s' % ( prefix, type_disp.upper( ), last_date.strftime('%d-%m-%Y') ) ]
    mp4tags['\xa9alb'] = [ core.get_mp4_album_name( inc_data ), ]
    mp4tags['\xa9ART'] = [ 'Tanim Islam' ]
    mp4tags['\xa9day'] = [ last_date.strftime('%d-%m-%Y') ]
    mp4tags.save( )
    os.chmod( movie_name, 0o644 )
    return os.path.basename( movie_name ) # for now return basename        

def create_summary_movie_frombeginning(
    inc_data, maxnum_colorbar = 5000.0, dirname = os.getcwd( ) ):
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
    prefix = inc_data[ 'prefix' ]
    regionName = inc_data[ 'region name' ]
    counties_and_states = list( map( core.get_county_state, inc_data[ 'fips' ] ) )
    last_date = max( inc_data['df'].date )
    #
    all_days_from_begin = list(range(inc_data['last day'] + 1 ) )
    def myfunc( input_tuple ):
        days_collection, i_status = input_tuple
        time00 = i_status[ 'time00' ]
        procno = i_status[ 'procno' ]
        numprocs = i_status[ 'numprocs' ]
        fnames = create_plots_daysfrombeginning(
            inc_data, regionName, dirname = tmp_dirname,
            days_from_beginning = days_collection, prefix = prefix,
            maxnum_colorbar = maxnum_colorbar )
        logging.info( 'took %0.3f seconds to process all %d days owned by process %d / %d.' % (
            time.time( ) - time00, len( fnames ), procno, numprocs ) )
        return fnames
    #
    ## first make all the plots
    time0 = time.time( )
    with multiprocessing.Pool( processes = multiprocessing.cpu_count( ) ) as pool:
        numprocs = multiprocessing.cpu_count( )
        input_tuples = list(zip(map(lambda idx: all_days_from_begin[idx::numprocs], range(numprocs)),
                                map(lambda idx: {
                                    'time00' : time0,
                                    'procno' : idx + 1,
                                    'numprocs' : numprocs }, range(numprocs))))
        for tup in input_tuples:
            days_collection, _ = tup
            if any(filter(lambda day: day < 0, days_collection ) ):
                logging.info( 'error days collection: %s.' % days_collection )
        allfiles = sorted(chain.from_iterable( pool.map( myfunc, input_tuples ) ) ) # change to pool.map
    logging.info( 'took %0.3f seconds to process all %d days.' % (
        time.time( ) - time0, len( all_days_from_begin ) ) )
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
    stdout_val = subprocess.check_output(
        [ ffmpeg_exec, '-y', '-r', '5', '-f', 'image2', '-i', allfile_name,
         '-vcodec', 'libx264', '-crf', '25', '-pix_fmt', 'yuv420p',
         movie_name ], stderr = subprocess.STDOUT )
    #
    ## now later remove those images and then remove the directory
    list(map(lambda fname: os.remove( fname ), allfiles ) )
    shutil.rmtree( tmp_dirname )
     #
    ## store metadata
    mp4tags = mutagen.mp4.MP4( movie_name )
    mp4tags['\xa9nam'] = [ '%s, ALL, %s' % ( prefix, last_date.strftime('%d-%m-%Y') ) ]
    mp4tags['\xa9alb'] = [ core.get_mp4_album_name( inc_data ), ]
    mp4tags['\xa9ART'] = [ 'Tanim Islam' ]
    mp4tags['\xa9day'] = [ last_date.strftime('%d-%m-%Y') ]
    mp4tags.save( )
    os.chmod( movie_name, 0o644 )
    return os.path.basename( movie_name )

def get_summary_demo_data(
    inc_data, maxnum_colorbar = 5000.0,
    dirname = os.getcwd( ), store_data = True ):
    #
    ## now is dirname a directory
    assert( os.path.isdir( dirname ) )
    doSmarter = False
    if inc_data[ 'prefix' ] == 'conus': doSmarter = True
    prefix = inc_data[ 'prefix' ]
    regionName = inc_data[ 'region name' ]
    counties_and_states = list( map( core.get_county_state, inc_data[ 'fips' ] ) )
    df_cases_deaths_region = inc_data[ 'df' ]
    #
    first_date = min( df_cases_deaths_region.date )
    last_date = max( df_cases_deaths_region.date )
    #
    ## pickle this pandas data
    last_date_str = last_date.strftime('%d%m%Y' )
    if store_data:
        df_cases_deaths_region.to_pickle(
            os.path.join( dirname, 'covid19_%s_LATEST.pkl.gz' % ( prefix ) ) )

    def create_plot_cds( ):
        #
        ## now make a plot, logarithmic
        fig = Figure( )
        ax = fig.add_subplot(111)
        fig.set_size_inches([ 12.0, 9.6 ])
        num_cases = df_cases_deaths_region.cases.max( )
        num_death = df_cases_deaths_region.death.max( )
        df_cases_deaths_region.plot(
          'days_from_beginning', 'cases', linewidth = 4.5,
          ax = ax, logy = True, grid = True )
        df_cases_deaths_region.plot(
            'days_from_beginning', 'death', linewidth = 4.5,
            ax = ax, logy = True, grid = True )
        ax.lines[0].set_label( 'cases: %s' % get_string_commas_num( num_cases ) )
        ax.lines[1].set_label( 'death: %s' % get_string_commas_num( num_death ) )
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
        canvas = FigureCanvasAgg( fig )
        file_prefix = 'covid19_%s_cds_LATEST' % ( prefix )
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
        file_prefix = 'covid19_%s_%s_LATEST' % ( prefix, prefix_dict[ case ] )
        fig_mine = Figure( )
        fig_mine.set_size_inches([ 12.0, 12.0 ])
        plot_cases_or_deaths_bycounty(
            inc_data, regionName, fig_mine, type_disp = case,
            days_from_beginning = inc_data[ 'last day' ],
            maxnum_colorbar = maxnum_colorbar, doTitle = True,
            doSmarter = doSmarter )
        canvas_mine = FigureCanvasAgg( fig_mine )
        pngfile = os.path.abspath( os.path.join( dirname, '%s.png' % file_prefix ) )
        pdffile = os.path.abspath( os.path.join( dirname, '%s.pdf' % file_prefix ) )
        canvas_mine.print_figure( pngfile, bbox_inches = 'tight' )
        canvas_mine.print_figure( pdffile, bbox_inches = 'tight' )
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
