import os, sys, numpy, titlecase, time
import subprocess, tempfile, shutil, datetime
import pathos.multiprocessing as multiprocessing
from itertools import chain
from multiprocessing import Value, Manager
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LogNorm, to_rgba
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from distutils.spawn import find_executable
#
from engine import mainDir, gis, core, autocrop_image, get_string_commas_num

def my_colorbar( mappable, ax, **kwargs ):
    """
    secret saucing (explanation is incomprehensible) from https://joseph-long.com/writing/colorbars/
    """
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = fig.colorbar(mappable, cax=cax, **kwargs)
    return cbar

def create_and_draw_basemap( ax, bbox, resolution = 'i' ):
    min_lng, min_lat, max_lng, max_lat = bbox
    lng_center = 0.5 * ( min_lng + max_lng )
    lat_center = 0.5 * ( min_lat + max_lat )
    lng_delta = 1.05 * ( max_lng - min_lng ) * 0.5
    lat_delta = 1.05 * ( max_lat - min_lat ) * 0.5
    m = Basemap(
        projection = 'stere', lon_0 = lng_center, lat_0 = lat_center, lat_ts = lat_center,
        llcrnrlat = lat_center - lat_delta, urcrnrlat = lat_center + lat_delta,
        llcrnrlon = lng_center - lng_delta, urcrnrlon = lng_center + lng_delta,
        resolution = resolution, area_thresh = 1.0, ellps = 'WGS84', ax = ax )
    m.drawparallels(numpy.arange(min_lat, max_lat, lat_delta / 1.5 ), labels = [1,0,0,1] )
    m.drawmeridians(numpy.arange(min_lng, max_lng, lng_delta / 1.5 ), labels = [1,0,0,1] )
    #
    ## create a "black" with alpha = 0.4
    try:
        cblack = list( to_rgba( 'black' ) )
        cblack[-1] = 0.4
        m.drawcoastlines( linewidth = 2, color = cblack )
    except: pass
    #
    ## create a "blue" with alpha = 0.3, and is the first blue color when plotting
    cblue = list( to_rgba( '#1f77b4' ) )
    cblue[-1] = 0.3
    m.drawrivers( linewidth = 5, color = cblue )
    m.fillcontinents( lake_color = cblue, color = 'white' )
    return m

def display_fips_geom( fips_data ):
    import pylab
    assert( 'bbox' in fips_data and 'points' in fips_data )
    fig, ax = pylab.subplots( )
    bbox = fips_data[ 'bbox' ]
    m = create_and_draw_basemap( ax, bbox, resolution = 'h' )
    fc = list( to_rgba( '#1f77b4' ) )
    fc[-1] = 0.25
    for shape in fips_data[ 'points' ]:
        x, y = m( shape[:,0], shape[:,1] )
        poly = Polygon(
            numpy.array([ x, y ]).T, closed = True,
            edgecolor = 'k', linewidth = 2.0, linestyle = 'dashed',
            facecolor = tuple(fc), alpha = 1.0 )
        ax.add_patch( poly )
    pylab.show( )

def display_fips( collection_of_fips ):
    import pylab
    fig, ax = pylab.subplots( )
    bdict = core.get_boundary_dict( collection_of_fips )
    bbox = core.calculate_total_bbox( chain.from_iterable( bdict.values( ) ) )
    bdict = core.get_boundary_dict( collection_of_fips )
    m = create_and_draw_basemap( ax, bbox, resolution = 'h' )
    fc = list( to_rgba( '#1f77b4' ) )
    fc[-1] = 0.25
    for fips in sorted( bdict ):
        for shape in bdict[ fips ]:
            x, y = m( shape[:,0], shape[:,1] )
            poly = Polygon(
                numpy.array([ x, y ]).T, closed = True,
                edgecolor = 'k', linewidth = 2.0, linestyle = 'dashed',
                facecolor = tuple(fc), alpha = 1.0 )
            ax.add_patch( poly )
            x_cent = x.mean( )
            y_cent = y.mean( )
            ax.text( x_cent, y_cent, fips, fontsize = 10, fontweight = 'bold', color = 'red' )
    pylab.show( )

def display_msa( msaname, doShow = False ):
    import pylab
    if doShow:
        fig, ax = pylab.subplots( )
    else:
        fig = Figure( )
        ax = fig.add_subplot(111)
    fig.set_size_inches([18,18])
    #
    data_msa = core.get_msa_data( msaname )
    bdict = core.get_boundary_dict( data_msa[ 'fips' ] )
    bbox = core.calculate_total_bbox( chain.from_iterable( bdict.values( ) ) )
    m = create_and_draw_basemap( ax, bbox, resolution = 'h' )
    fc = list( to_rgba( '#1f77b4' ) )
    fc[-1] = 0.25
    for fips in sorted( bdict ):
        for shape in bdict[ fips ]:
            x, y = m( shape[:,0], shape[:,1] )
            poly = Polygon(
                numpy.array([ x, y ]).T, closed = True,
                edgecolor = 'k', linewidth = 2.0, linestyle = 'dashed',
                facecolor = tuple(fc), alpha = 1.0 )
            ax.add_patch( poly )
            x_cent = x.mean( )
            y_cent = y.mean( )
            ax.text( x_cent, y_cent, fips, fontsize = 10, fontweight = 'bold', color = 'red' )
    #
    ## now info on this MSA
    ax.text( 0.01, 0.98, 'COUNTIES IN %s.' % data_msa[ 'region name' ], fontsize = 20, fontweight = 'bold',
            transform = ax.transAxes, horizontalalignment = 'left', verticalalignment = 'top' )
    if not doShow:
        canvas = FigureCanvasAgg( fig )
        canvas.print_figure( 'msa_%s_counties.png' % msaname, bbox_inches = 'tight' )
        autocrop_image.autocrop_image( 'msa_%s_counties.png' % msaname )
    else: pylab.show( )
    
def plot_cases_bycounty(
    inc_data, regionName, ax, days_from_beginning = 0,
    maxnum_colorbar = 5000.0, doTitle = True, cases_plot_artists = { } ):
    assert( days_from_beginning >= 0 )
    assert( days_from_beginning <= inc_data[ 'last day' ] )
    assert( maxnum_colorbar > 1 )
    #
    ## NOW CREATE BASEMAP HIGH REZ
    if 'isBaseMapped' not in cases_plot_artists:
        m = create_and_draw_basemap( ax, inc_data[ 'bbox' ], resolution = 'h' )
        cases_plot_artists[ 'isBaseMapped' ] = m
        cases_plot_artists[ 'sm' ] = ScalarMappable( norm = LogNorm( 1.0, maxnum_colorbar ), cmap = 'jet' )
    #
    ## draw boundaries if not defined
    boundaries = inc_data['boundaries']
    df_dfm = inc_data['df'][ inc_data['df']['days_from_beginning'] == days_from_beginning ].copy( )
    sm = cases_plot_artists[ 'sm' ]
    for fips in sorted( boundaries ):
        num_cases = df_dfm['cases_%s' % fips].max( )
        fc = sm.to_rgba( num_cases )
        if num_cases == 0: fc = ( 1.0, 1.0, 1.0, 0.0 )
        if 'cases_polys_%s' % fips not in cases_plot_artists:
            cases_plot_artists.setdefault( 'cases_polys_%s' % fips, [] )
            for shape in boundaries[ fips ]:
                x, y = m( shape[:,0], shape[:,1] )
                poly = Polygon(
                    numpy.array([ x, y ]).T, closed = True,
                    edgecolor = 'k', linewidth = 1.0, linestyle = 'dashed',
                    facecolor = fc, alpha = 0.4 )
                ax.add_patch( poly )
                cases_plot_artists[ 'cases_polys_%s' % fips ].append( poly )
        else:
            for poly in cases_plot_artists[ 'cases_polys_%s' % fips ]:
                poly.set_facecolor( fc )
                poly.set_alpha( 0.4 )
    
    #
    ## now add the colorbar associated with sm
    #cb = fig.colorbar( sm, ax = ax, alpha = 0.8 )
    if 'cb' not in cases_plot_artists:        
        cb = my_colorbar( sm, ax, alpha = 0.8 )
        cb.set_label( 'number of cases', fontsize = 18, fontweight = 'bold' )
        cases_plot_artists[ 'cb' ] = cb
    #
    ## now put in the legend in upper left corner, fontsize = 14, weight = bold
    ## following info: date, days after beginning, number of cases
    date_s = df_dfm.date.max().strftime( '%d %B %Y' )
    num_cases = df_dfm.cases.max( )
    if 'cases_text' not in cases_plot_artists:
        txt = ax.text(
            0.01, 0.02, '\n'.join([
                '%s' % date_s,
                '%d days from 1st case' % days_from_beginning,
                '%s cumulative cases' % get_string_commas_num( num_cases ) ]),
            color = ( 0.0, 0.0, 0.0, 0.8 ),
            fontsize = 18, fontweight = 'bold', transform = ax.transAxes,
            horizontalalignment = 'left', verticalalignment = 'bottom' )
        cases_plot_artists[ 'cases_text' ] = txt
    else:
        cases_plot_artists[ 'cases_text' ].set_text('\n'.join([
            '%s' % date_s,
            '%d days from 1st case' % days_from_beginning,
            '%s cumulative cases' % get_string_commas_num( num_cases ) ] ) )
            
    if doTitle:
        ax.set_title( '\n'.join([
            'Cumulative number of COVID-19 cases',
            'in %s after %d / %d days from start' % ( regionName, days_from_beginning, inc_data[ 'last day'] ) ] ),
                    fontsize = 18, fontweight = 'bold' )

def plot_deaths_bycounty(
    inc_data, regionName, ax, days_from_beginning = 0,
    maxnum_colorbar = 5000.0, doTitle = True, death_plot_artists = { } ):
    assert( days_from_beginning >= 0 )
    assert( days_from_beginning <= inc_data[ 'last day' ] )
    assert( maxnum_colorbar > 1 )
    #
    ## NOW CREATE BASEMAPS
    if 'isBaseMapped' not in death_plot_artists:
        m = create_and_draw_basemap( ax, inc_data[ 'bbox' ], resolution = 'h' )
        death_plot_artists[ 'isBaseMapped' ] = m
        death_plot_artists[ 'sm' ] = ScalarMappable( norm = LogNorm( 1.0, maxnum_colorbar ), cmap = 'jet' )
    boundaries = inc_data['boundaries']
    df_dfm = inc_data['df'][ inc_data['df']['days_from_beginning'] == days_from_beginning ].copy( )
    sm = death_plot_artists[ 'sm' ]
    for fips in sorted( boundaries ):
        num_deaths = df_dfm['deaths_%s' % fips].max( )
        fc = sm.to_rgba( num_deaths )
        if num_deaths == 0: fc = ( 1.0, 1.0, 1.0, 0.0 )
        if 'death_polys_%s' % fips not in death_plot_artists:
            death_plot_artists.setdefault( 'death_polys_%s' % fips, [ ] )
            for shape in boundaries[ fips ]:
                x, y = m( shape[:,0], shape[:,1] )
                poly = Polygon(
                    numpy.array([ x, y ]).T, closed = True,
                    edgecolor = 'k', linewidth = 1.0, linestyle = 'dashed',
                    facecolor = fc, alpha = 0.4 )
                ax.add_patch( poly )
                death_plot_artists[ 'death_polys_%s' % fips ].append( poly )
        else:
            for poly in death_plot_artists[ 'death_polys_%s' % fips ]:
                poly.set_facecolor( fc )
                poly.set_alpha( 0.4 )
    #
    ## now add the colorbar associated with sm
    if 'cb' not in death_plot_artists:
        cb = my_colorbar( sm, ax, alpha = 0.8 )
        cb.set_label( 'number of deaths', fontsize = 18, fontweight = 'bold' )
        death_plot_artists[ 'cb' ] = cb
    #
    ## now put in the legend in upper left corner, fontsize = 14, weight = bold
    ## following info: date, days after beginning, number of cases
    date_s = df_dfm.date.max().strftime( '%d %B %Y' )
    num_deaths = df_dfm.death.max( )
    if 'death_text' not in death_plot_artists:
        txt = ax.text(
            0.01, 0.02, '\n'.join([
                '%s' % date_s,
                '%d days from 1st case' % days_from_beginning,
                '%s cumulative deaths' % get_string_commas_num( num_deaths ) ]),
            color = ( 0.0, 0.0, 0.0, 0.8 ),
            fontsize = 18, fontweight = 'bold', transform = ax.transAxes,
            horizontalalignment = 'left', verticalalignment = 'bottom' )
        death_plot_artists[ 'death_text' ] = txt
    else:
        death_plot_artists[ 'death_text' ].set_text('\n'.join([
             '%s' % date_s,
                '%d days from 1st case' % days_from_beginning,
                '%s cumulative deaths' % get_string_commas_num( num_deaths ) ] ) )
    if doTitle:
        ax.set_title( '\n'.join([
            'Cumulative number of COVID-19 deaths',
            'in %s after %d / %d days from start' % ( regionName, days_from_beginning, inc_data[ 'last day' ] ) ] ),
                    fontsize = 18, fontweight = 'bold' )

def plot_cases_deaths_region( inc_data, regionName, ax, days_from_beginning = 0, doTitle = True ):
    assert( days_from_beginning >= 0 )
    assert( days_from_beginning <= inc_data[ 'last day' ] )
    df_cases_deaths_region = inc_data[ 'df' ]
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
    ax.lines[0].set_label( 'cases: %d / %d' % ( num_cases, num_cases_tot ) )
    ax.lines[1].set_label( 'death: %d / %d' % ( num_death, num_death_tot ) )
    #
    ax.set_xlim(0.0, inc_data[ 'last day' ] )
    ax.set_ylim(1.0, 1.15 * df_cases_deaths_region.cases.max( ) )
    ax.set_aspect( inc_data[ 'last day' ] / numpy.log10( 1.15 * df_cases_deaths_region.cases.max( ) ) )
    ax.set_xlabel(
        'Days from First COVID-19 CASE (%s)' %
        first_date.strftime( '%d-%m-%Y' ),
        fontsize = 18, fontweight = 'bold' )
    ax.set_ylabel( 'Cumulative Number of Cases/Deaths', fontsize = 12, fontweight = 'bold' )
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

def create_plots_daysfrombeginning( inc_data, regionName, prefix, days_from_beginning = [ 0 ],
                                   dirname = os.getcwd( ), maxnum_colorbar = 5000 ):
    if any(filter(lambda day: day < 0, days_from_beginning ) ):
        print( 'error days_from_beginning = %s.' % days_from_beginning )
    assert( os.path.isdir( dirname ) )
    #assert(all(filter(lambda day: day >= 0, days_from_beginning ) ) )
    #assert(all(filter(lambda day: day <= inc_data[ 'last day' ], days_from_beginning ) ) )
    assert( maxnum_colorbar > 1 )
    fig = Figure( )
    ax_deaths = fig.add_subplot(111)
    #
    ## first plot, get correct width multiplication
    sorted_days = sorted( set( days_from_beginning ) )
    first_day = min( days_from_beginning )
    plot_deaths_bycounty(
        inc_data, regionName, ax_deaths,
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar,
        death_plot_artists = { } )
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
    ax_deaths = fig.add_subplot(222)
    ax_cases = fig.add_subplot(224)
    ax_cd = fig.add_subplot(223)
    #
    ## now plots
    death_plot_artists = { }
    cases_plot_artists = { }
    plot_deaths_bycounty(
        inc_data, regionName, ax_deaths,
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar,
        death_plot_artists = death_plot_artists )
    plot_cases_bycounty(
        inc_data, regionName, ax_cases,
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar,
        cases_plot_artists = cases_plot_artists )
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
        'Most County Cases: %d' % cases_max,
        '%s, %s' % ( cs['county'], cs['state'] ),
        'Showing Day %d / %d' % ( first_day, inc_data[ 'last day' ] ) ]),
                fontsize = 24, fontweight = 'bold', transform = ax_leg.transAxes,
                horizontalalignment = 'left', verticalalignment = 'top' )
    canvas = FigureCanvasAgg( fig )
    fname = os.path.join( dirname, 'covid19_%s_%s.%04d.png' % (
        prefix, last_date.strftime('%d%m%Y'), first_day ) )
    canvas.print_figure( fname, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( fname, fixEven = True )
    fnames.append( fname )
    #
    ## now do for the remaining days
    for day in sorted_days[1:]:
        plot_deaths_bycounty(
            inc_data, regionName, ax_deaths,
            days_from_beginning = day, doTitle = False,
            maxnum_colorbar = maxnum_colorbar,
            death_plot_artists = death_plot_artists )
        plot_cases_bycounty(
            inc_data, regionName, ax_cases,
            days_from_beginning = day, doTitle = False,
            maxnum_colorbar = maxnum_colorbar,
            cases_plot_artists = cases_plot_artists )
        plot_cases_deaths_region(
            inc_data, regionName, ax_cd,
            days_from_beginning = day, doTitle = False )
        ax_leg_txt.set_text( '\n'.join([
            regionName,
            'First COVID-19 CASE: %s' % first_date.strftime( '%d-%m-%Y' ),
            'Latest COVID-19 CASE: %s' % last_date.strftime( '%d-%m-%Y' ),
            'Most County Cases: %d' % cases_max,
            '%s, %s' % ( cs['county'], cs['state'] ),
            'Showing Day %d / %d' % ( day, inc_data[ 'last day' ] ) ]) )
        canvas = FigureCanvasAgg( fig )
        fname = os.path.join( dirname, 'covid19_%s_%s.%04d.png' % (
            prefix, last_date.strftime('%d%m%Y'), day ) )
        canvas.print_figure( fname, bbox_inches = 'tight' )
        autocrop_image.autocrop_image( fname, fixEven = True )
        fnames.append( fname )
    return fnames

def create_summary_movie_frombeginning(
    data = core.get_msa_data( 'bayarea' ),
    maxnum_colorbar = 5000.0 ):
    #
    ## barf out if cannot find ffmpeg
    ffmpeg_exec = find_executable( 'ffmpeg' )
    if ffmpeg_exec is None:
        raise ValueError("Error, ffmpeg could not be found." )
    #
    ## create directory
    dirname = tempfile.mkdtemp( suffix = 'covid19' )
    #
    prefix = data[ 'prefix' ]
    regionName = data[ 'region name' ]
    counties_and_states = list( map( core.get_county_state, data[ 'fips' ] ) )
    inc_data = core.get_incident_data( data )
    #
    all_days_from_begin = list(range(inc_data['last day'] + 1 ) )
    def myfunc( input_tuple ):
        days_collection, time00 = input_tuple
        fnames = create_plots_daysfrombeginning(
            inc_data, regionName, dirname = dirname,
            days_from_beginning = days_collection, prefix = prefix,
            maxnum_colorbar = maxnum_colorbar )
        print( 'took %0.3f seconds to process %d of %d days.' % (
            time.time( ) - time00,
            len( fnames ), len( all_days_from_begin ) ) )
        return fnames
    #
    ## first make all the plots
    time0 = time.time( )
    with multiprocessing.Pool( processes = multiprocessing.cpu_count( ) ) as pool:
        numprocs = multiprocessing.cpu_count( )
        input_tuples = list(zip(map(lambda idx: all_days_from_begin[idx::numprocs], range(numprocs)),
                                [ time0 ] * numprocs ) )
        for tup in input_tuples:
            days_collection, _ = tup
            if any(filter(lambda day: day < 0, days_collection ) ):
                print( 'error days collection: %s.' % days_collection )
        allfiles = sorted(chain.from_iterable( pool.map( myfunc, input_tuples ) ) )
    print( 'took %0.3f seconds to process all %d days.' % (
        time.time( ) - time0, len( all_days_from_begin ) ) )
    #
    ## now make the movie
    allfiles_prefixes = set(map(
        lambda fname: '.'.join(os.path.basename( fname ).split('.')[:-2]), allfiles))
    assert( len( allfiles_prefixes ) == 1 )
    movie_prefix = max( allfiles_prefixes )
    movie_name = '%s.mp4' % movie_prefix # movie goes into directory where exec launched
    allfile_name = os.path.join( dirname, '%s.%%04d.png' % movie_prefix )
    #
    ## thank instructions from https://hamelot.io/visualization/using-ffmpeg-to-convert-a-set-of-images-into-a-video/
    ## make MP4 movie, 5 fps, quality = 25
    proc = subprocess.Popen([ ffmpeg_exec, '-y', '-r', '5', '-f', 'image2', '-i', allfile_name,
                             '-vcodec', 'libx264', '-crf', '25', '-pix_fmt', 'yuv420p',
                             movie_name ], stdout = subprocess.PIPE,
                            stderr = subprocess.STDOUT )
    stdout_val, stderr_val = proc.communicate( )
    #
    ## now later remove those images and then remove the directory
    list(map(lambda fname: os.remove( fname ), allfiles ) )
    shutil.rmtree( dirname )
    return movie_name

def get_summary_demo_data( data, maxnum_colorbar = 5000.0 ):
    prefix = data[ 'prefix' ]
    regionName = data[ 'region name' ]
    counties_and_states = list( map( core.get_county_state, data[ 'fips' ] ) )
    inc_data = core.get_incident_data( data )
    df_cases_deaths_region = inc_data[ 'df' ]
    #
    first_date = min( df_cases_deaths_region.date )
    last_date = max( df_cases_deaths_region.date )
    #
    ## pickle this pandas data
    last_date_str = last_date.strftime('%d%m%Y' )
    df_cases_deaths_region.to_pickle(
        'covid19_%s_%s.pkl.gz' % ( prefix, last_date_str ) )
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
    file_prefix = 'covid19_%s_cds_%s' % ( prefix, last_date_str )
    canvas.print_figure( '%s.pdf' % file_prefix, bbox_inches = 'tight' )
    canvas.print_figure( '%s.png' % file_prefix, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( '%s.png' % file_prefix )
    try: autocrop_image.autocrop_image_pdf( '%s.pdf' % file_prefix )
    except: pass
    #
    ## now create figures CASES
    fig1 = Figure( )
    ax1 = fig1.add_subplot(111)
    fig1.set_size_inches([ 12.0, 12.0 ])
    plot_cases_bycounty(
        inc_data, regionName, ax1, days_from_beginning = inc_data[ 'last day' ],
        maxnum_colorbar = maxnum_colorbar, doTitle = True )
    canvas = FigureCanvasAgg( fig1 )
    file_prefix = 'covid19_%s_cases_%s' % ( prefix, last_date_str )
    canvas.print_figure( '%s.pdf' % file_prefix, bbox_inches = 'tight' )
    canvas.print_figure( '%s.png' % file_prefix, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( '%s.png' % file_prefix )
    try: autocrop_image.autocrop_image_pdf( '%s.pdf' % file_prefix )
    except: pass
    #
    ## now create figures DEATHS
    fig2 = Figure( )
    ax1 = fig2.add_subplot(111)
    fig2.set_size_inches([ 12.0, 12.0 ])
    plot_deaths_bycounty(
        inc_data, regionName, ax1, days_from_beginning = inc_data[ 'last day' ],
        maxnum_colorbar = maxnum_colorbar, doTitle = True )
    canvas = FigureCanvasAgg( fig2 )
    file_prefix = 'covid19_%s_death_%s' % ( prefix, last_date_str )
    canvas.print_figure( '%s.pdf' % file_prefix, bbox_inches = 'tight' )
    canvas.print_figure( '%s.png' % file_prefix, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( '%s.png' % file_prefix )
    try: autocrop_image.autocrop_image_pdf( '%s.pdf' % file_prefix )
    except: pass
