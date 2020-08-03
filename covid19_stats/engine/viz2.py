import os, sys, numpy, titlecase, time, pandas
import subprocess, tempfile, shutil, datetime, logging
import pathos.multiprocessing as multiprocessing
from itertools import chain
from multiprocessing import Value, Manager
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize, to_rgba
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from distutils.spawn import find_executable
from nprstuff.core import autocrop_image
#
from covid19_stats.engine import gis, core, get_string_commas_num
from covid19_stats.engine.viz import (
    create_and_draw_basemap, create_and_draw_basemap_smarter, my_colorbar,
    determine_corners_center_stereo, display_fips_geom, display_fips, display_msa )

_default_startdate = datetime.datetime.strptime(
    "1 May 2020", '%d %B %Y' ).date( )

def plot_cases_or_deaths_bycounty_linear_fromdate(
    inc_data, regionName, ax, type_disp = 'cases', days_from_beginning = 0, resolution = 'h',
    maxnum_colorbar = 5000.0, doTitle = True, plot_artists = { },
    poly_line_width = 1.0, doSmarter = False,
    startdate = _default_startdate ):
    assert( resolution in ( 'c', 'l', 'i', 'h', 'f' ) )
    assert( type_disp in ( 'cases', 'deaths' ) )
    assert( days_from_beginning >= 0 )
    assert( maxnum_colorbar > 1 )
    #
    ## now check that the days from beginning isn't too far gone
    assert( startdate in set( inc_data['df'].date ) )
    last_timedelta_fromdate = max( inc_data['df'].date ) - startdate
    assert( days_from_beginning <= last_timedelta_fromdate.days )
    timedelta_todate = startdate - min( inc_data['df'].date )
    startdate_days_from_beginning = timedelta_todate.days
    if type_disp == 'cases': key = 'cases'
    elif type_disp == 'deaths': key = 'death'
    #
    ## NOW CREATE BASEMAP HIGH REZ
    ## LAZY LOADING
    if 'isBaseMapped' not in plot_artists:
        if not doSmarter:
            m = create_and_draw_basemap( ax, inc_data[ 'bbox' ], resolution = resolution )
        else: m = create_and_draw_basemap_smarter(
            ax, inc_data[ 'boundaries' ],
            resolution = resolution, river_linewidth = 1.0, river_alpha = 0.15,
            coast_linewidth = 1.0, coast_alpha = 0.25 )
        plot_artists[ 'isBaseMapped' ] = m
        plot_artists[ 'sm' ] = ScalarMappable( norm = Normalize( 0.0, maxnum_colorbar ), cmap = 'jet' )
    #
    ## draw boundaries if not defined
    boundaries = inc_data['boundaries']
    df_dfm = inc_data['df'][ inc_data['df']['days_from_beginning'] == days_from_beginning +
                            startdate_days_from_beginning ].copy( )
    df_dfm_startdate =  inc_data['df'][ inc_data['df']['days_from_beginning'] == 
                                       startdate_days_from_beginning ].copy( )
    sm = plot_artists[ 'sm' ]
    m = plot_artists[ 'isBaseMapped' ]
    for fips in sorted( boundaries ):
        nums = df_dfm['%s_%s' % ( type_disp, fips )].max( )
        if nums == 0: fc = ( 1.0, 1.0, 1.0, 0.0 )
        else: fc = sm.to_rgba( nums )
        art_key = '%s_polys_%s' % ( key, fips )
        if art_key not in plot_artists:
            plot_artists.setdefault( art_key, [ ] )
            for shape in boundaries[ fips ]:
                x, y = m( shape[:,0], shape[:,1] )
                poly = Polygon(
                    numpy.array([ x, y ]).T, closed = True,
                    linewidth = poly_line_width, linestyle = 'dashed',
                    facecolor = fc, alpha = 0.4 )
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
        cb.set_label( 'number of %s after %s' % ( type_disp, startdate.strftime('%d %B %Y' ) ),
                     fontsize = 18, fontweight = 'bold' )
        cb.formatter.set_useMathText( True )
        cb.formatter.set_powerlimits((0, 0))
        plot_artists[ 'cb' ] = cb
    #
    ## now put in the legend in upper left corner, fontsize = 14, weight = bold
    ## following info: date, days after beginning, number of cases
    date_s = df_dfm.date.max().strftime( '%d %B %Y' )
    num_tot = df_dfm[ key ].max( )
    num_upto_startdate = df_dfm_startdate[ key ].max( )
    datestring = startdate.strftime( '%d-%m-%Y' )
    if '%s_text' % key not in plot_artists:
        txt = ax.text(
            0.01, 0.02, '\n'.join([
                '%s' % date_s,
                '%d days from %s' % ( days_from_beginning, datestring ),
                '%s cumulative %s from %s' % ( get_string_commas_num( num_tot - num_upto_startdate ), type_disp, datestring ) ]),
            color = ( 0.0, 0.0, 0.0, 0.8 ),
            fontsize = 18, fontweight = 'bold', transform = ax.transAxes,
            horizontalalignment = 'left', verticalalignment = 'bottom' )
        plot_artists[ '%s_text' % key ] = txt
    else:
        plot_artists[ '%s_text' % key ].set_text('\n'.join([
            '%s' % date_s,
            '%d days from %s' % ( days_from_beginning, datestring ),
            '%s cumulative %s from %s' % ( type_disp, get_string_commas_num( num_tot ), datestring ) ] ) )
            
    if doTitle:
        ax.set_title( '\n'.join([
            'Cumulative number of COVID-19 %s' % type_disp,
            'in %s after %d / %d days from %s' % ( regionName, days_from_beginning, last_timedelta_fromdate.days, datestring ) ] ),
                    fontsize = 18, fontweight = 'bold' )

def plot_cases_deaths_region_linear_fromdate(
    inc_data, regionName, ax_cases, ax_death, days_from_beginning = 0, doTitle = True, startdate = _default_startdate ):
    assert( days_from_beginning >= 0 )
    assert( startdate in set( inc_data['df'].date ) )
    last_timedelta_fromdate = max( inc_data['df'].date ) - startdate
    assert( days_from_beginning <= last_timedelta_fromdate.days )
    timedelta_todate = startdate - min( inc_data['df'].date )
    startdate_days_from_beginning = timedelta_todate.days
    df_sub = inc_data['df'][ inc_data['df'].date >= startdate ]
    df_cases_deaths_region = pandas.DataFrame({
        'date' : df_sub.date,
        'cases' : df_sub.cases - df_sub.cases.min( ) ,
        'death' : df_sub.death - df_sub.death.min( ),
        'days_from_startdate' : df_sub.days_from_beginning - df_sub.days_from_beginning.min( ) } )
    cases_begin = df_sub.cases.min( )
    death_begin = df_sub.death.min( )
    ax_cases.clear( ) # first clear everything in this axes (cases)
    ax_death.clear( ) # first clear everything in this axes (death)
    #
    first_date = min( df_cases_deaths_region.date )
    last_date = max( df_cases_deaths_region.date )
    #
    df_cases_deaths_regions_bef = df_cases_deaths_region[
        df_cases_deaths_region.days_from_startdate <= days_from_beginning ].copy( )
    df_cases_deaths_regions_aft = df_cases_deaths_region[
        df_cases_deaths_region.days_from_startdate >= days_from_beginning ].copy( )
    #
    ##
    df_dfm = df_cases_deaths_region[
        df_cases_deaths_region.days_from_startdate == days_from_beginning ]
    num_cases = df_dfm.cases.max( )
    num_death = df_dfm.death.max( )
    num_cases_tot = df_cases_deaths_region.cases.max( )
    num_death_tot = df_cases_deaths_region.death.max( )
    #
    ## before, full solid color plot
    ax_cases.plot(
        df_cases_deaths_regions_bef.days_from_startdate,
        df_cases_deaths_regions_bef.cases, linewidth = 4.5,
        color = 'C0', label = '\n'.join([
            'extra cases: %s / %s' % tuple(map(get_string_commas_num, (num_cases, num_cases_tot ) ) ),
            'after %s' % startdate.strftime('%d-%m-%Y' ),
            '%s cases by %s' % ( get_string_commas_num( cases_begin ), startdate.strftime('%d-%m-%Y' ) ) ] ) )
    ax_cases.grid( axis = 'both' )
    ax_death.plot(
       df_cases_deaths_regions_bef.days_from_startdate,
       df_cases_deaths_regions_bef.death, linewidth = 4.5,
       color = 'C1', label = '\n'.join([
           'extra death: %s / %s' % tuple(map(get_string_commas_num, (num_death, num_death_tot ) ) ),
           'after %s' % startdate.strftime('%d %B %Y' ),
           '%s death by %s' % ( get_string_commas_num( death_begin ), startdate.strftime('%d-%m-%Y' ) ) ] ) )
    #
    ## after, alpha = 0.5
    ax_cases.plot(
        df_cases_deaths_regions_aft.days_from_startdate,
        df_cases_deaths_regions_aft.cases, linewidth = 4.5,
        color = 'C0', alpha = 0.5 )
    ax_death.plot(
        df_cases_deaths_regions_aft.days_from_startdate,
        df_cases_deaths_regions_aft.death, linewidth = 4.5,
        color = 'C1', alpha = 0.5 )
    #
    ## now just do colors
    ax_cases.scatter([ days_from_beginning ], [ df_dfm.cases.max( ) ], s = 100, color = 'C0' )
    ax_death.scatter([ days_from_beginning ], [ df_dfm.death.max( ) ], s = 100, color = 'C1' )
    #
    ax_cases.set_xlim(0.0, df_cases_deaths_region.days_from_startdate.max( ) )
    ax_cases.set_ylim(0.0, 1.05 * df_cases_deaths_region.cases.max( ) )
    ax_death.set_ylim(0.0, 1.05 * df_cases_deaths_region.death.max( ) )
    # ax_cases.set_aspect( inc_data[ 'last day' ] / 1.15 * df_cases_deaths_region.cases.max( ) )
    ax_cases.set_xlabel(
        'Days After %s' % startdate.strftime( '%d %B %Y' ),
        fontsize = 18, fontweight = 'bold' )
    ax_cases.set_ylabel( '\n'.join([
        'Cumulative Number of Cases',
        'After %s' %startdate.strftime( '%d %B %Y' ) ]),
                        fontsize = 18, fontweight = 'bold' )
    ax_death.set_ylabel( '\n'.join([
        'Cumulative Number of Deaths',
        'After %s' %startdate.strftime( '%d %B %Y' ) ]),
                        fontsize = 18, fontweight = 'bold' )
    if doTitle:
        ax_cases.set_title( '\n'.join(
            [
                '%s Trend in COVID-19' % titlecase.titlecase( regionName ),
                'through %d / %d days after %s' % ( days_from_beginning, df_cases_deaths_region.days_from_startdate.max( ),
                                                  startdate.strftime( '%d %B %Y' ) ),
            ]), fontsize = 18, fontweight = 'bold' )
    #
    ## scientific and math formatting
    for formatter in list(map(lambda axes: axes.yaxis.get_major_formatter( ), ( ax_cases, ax_death ) ) ):
        formatter.set_useMathText( True )
        formatter.set_powerlimits((0,0))
        
    #
    ## text on last day
    ax_cases.text( 0.02, 0.7, '\n'.join([
        'last day: %s' % last_date.strftime('%d-%m-%Y'),
        '%d days after %s' % ( df_cases_deaths_region.days_from_startdate.max( ), startdate.strftime('%d-%m-%Y') ) ]),
            transform = ax_cases.transAxes, fontsize = 18, fontweight = 'bold',
            horizontalalignment = 'left', verticalalignment = 'center', color = 'purple' )
                                   
    ## tick labels size 20, bold
    for label in ax_cases.xaxis.get_majorticklabels( ) + ax_cases.yaxis.get_majorticklabels( ):
        label.set_fontsize( 14 )
        label.set_fontweight( 'bold' )
    for label in ax_death.yaxis.get_majorticklabels( ):
        label.set_fontsize( 14 )
        label.set_fontweight( 'bold' )
    for axes in ( ax_cases, ax_death ):
        axes.yaxis.offsetText.set_fontsize( 16 )
        axes.yaxis.offsetText.set_fontweight( 'bold' )
    #
    ## legend size 24, bold
    leg_cases = ax_cases.legend( loc = 'upper left' )
    leg_death = ax_death.legend( loc = 'upper left', bbox_to_anchor = ( 0.0, 0.88 ) )
    for txt in leg_cases.texts + leg_death.texts:
        txt.set_fontsize( 18 )
        txt.set_fontweight( 'bold' )

def create_plots_days_from_startdate(
    inc_data, regionName, prefix, days_from_beginning = [ 0 ],
    dirname = os.getcwd( ), maxnum_colorbar_cases = 5000,
    maxnum_colorbar_death = 500,
    startdate = _default_startdate ):
    assert( os.path.isdir( dirname ) )
    #assert(all(filter(lambda day: day >= 0, days_from_beginning ) ) )
    #assert(all(filter(lambda day: day <= inc_data[ 'last day' ], days_from_beginning ) ) )
    assert( maxnum_colorbar_cases > 1 )
    assert( maxnum_colorbar_death > 1 )
    doSmarter = False
    if prefix == 'conus': doSmarter = True
    fig = Figure( )
    ax_deaths = fig.add_subplot(111)
    #
    ## first plot, get correct width multiplication
    sorted_days = sorted( set( days_from_beginning ) )
    first_day = min( days_from_beginning )
    plot_cases_or_deaths_bycounty_linear_fromdate(
        inc_data, regionName, ax_deaths, type_disp = 'deaths',
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar_death,
        plot_artists = { }, doSmarter = doSmarter,
        startdate = startdate )
    ratio_width_height = ax_deaths.get_xlim( )[1] / ax_deaths.get_ylim( )[1]
    height_units = 2.0
    width_units = 1 + ratio_width_height
    #
    ## get collection of filenames to return
    fnames = [ ]
    #
    ## now create a figure of correct size, just trialing and erroring it
    fig = Figure( )
    fig.set_size_inches([ 30.0 * width_units / height_units, 30.0 * 0.8 ] )
    ax_deaths = fig.add_subplot(222)
    ax_cases = fig.add_subplot(224)
    ax_cases_plot = fig.add_subplot(223)
    ax_death_plot = ax_cases_plot.twinx( )
    #
    ## now plots
    death_plot_artists = { }
    cases_plot_artists = { }
    plot_cases_or_deaths_bycounty_linear_fromdate(
        inc_data, regionName, ax_deaths, type_disp = 'deaths',
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar_death,
        plot_artists = death_plot_artists, doSmarter = doSmarter,
        startdate = startdate )
    plot_cases_or_deaths_bycounty_linear_fromdate(
        inc_data, regionName, ax_cases, type_disp = 'cases',
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar_cases,
        plot_artists = cases_plot_artists, doSmarter = doSmarter,
        startdate = startdate )
    plot_cases_deaths_region_linear_fromdate(
        inc_data, regionName, ax_cases_plot, ax_death_plot,
        days_from_beginning = first_day, doTitle = False,
        startdate = startdate )
    #
    ## legend plot
    df_cases_deaths_region = inc_data[ 'df' ]
    first_date = min( df_cases_deaths_region.date )
    last_date = max( df_cases_deaths_region.date )
    last_timedelta_fromdate = max( df_cases_deaths_region.date ) - startdate
    max_fips_cases = max( map(lambda key: (
        key.replace('cases_','').strip( ),
        df_cases_deaths_region[ key ].max( ) -
        df_cases_deaths_region[ key ][ df_cases_deaths_region.date == startdate ].max( ) ),
       filter(lambda key: key.startswith('cases_'), df_cases_deaths_region)),
      key = lambda fips_case: fips_case[1] )
    cases_fips_max, cases_max = max_fips_cases
    cs_cases = core.get_county_state( cases_fips_max )
    #
    max_fips_deaths = max( map(lambda key: (
        key.replace('deaths_','').strip( ),
        df_cases_deaths_region[ key ].max( ) -
        df_cases_deaths_region[ key ][ df_cases_deaths_region.date == startdate ].max( ) ),
       filter(lambda key: key.startswith('deaths_'), df_cases_deaths_region)),
      key = lambda fips_death: fips_death[1] )
    death_fips_max, death_max = max_fips_deaths
    cs_death = core.get_county_state( death_fips_max )
    #
    ax_leg = fig.add_subplot(221)
    ax_leg.set_aspect( 1.0 )
    ax_leg.axis('off')
    ax_leg_txt = ax_leg.text(-0.1, 1.0, '\n'.join([
        regionName,
        'First COVID-19 CASE: %s' % first_date.strftime( '%d-%m-%Y' ),
        'Latest COVID-19 CASE: %s' % last_date.strftime( '%d-%m-%Y' ),
        '--',
        'Most County Cases',
        'After %s: %s' % ( startdate.strftime( '%d-%m-%Y' ),
                          get_string_commas_num( cases_max ) ),
        '%s, %s' % ( cs_cases['county'], cs_cases['state'] ),
        #
        '--',
        'Most County Deaths',
        'After %s: %s' % ( startdate.strftime( '%d-%m-%Y' ),
                          get_string_commas_num( death_max ) ),
        '%s, %s' % ( cs_death['county'], cs_death['state'] ),
        #
        '--',
        'Showing Day %d / %d' % ( first_day, last_timedelta_fromdate.days ),
        'After %s' % startdate.strftime( '%d %B %Y' ) ] ),
                             fontsize = 24, fontweight = 'bold', transform = ax_leg.transAxes,
                             horizontalalignment = 'left', verticalalignment = 'top' )
    canvas = FigureCanvasAgg( fig )
    fname = os.path.join( dirname, 'covid19_fromdate_%s_%s_%s.%04d.png' % (
        prefix, startdate.strftime('%d%m%Y'), last_date.strftime('%d%m%Y'), first_day ) )
    canvas.print_figure( fname, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( fname, fixEven = True )
    fnames.append( fname )
    #
    ## now do for the remaining days
    for day in sorted_days[1:]:
        plot_cases_or_deaths_bycounty_linear_fromdate(
            inc_data, regionName, ax_deaths, type_disp = 'deaths',
            days_from_beginning = day, doTitle = False,
            maxnum_colorbar = maxnum_colorbar_death,
            plot_artists = death_plot_artists, startdate = startdate )
        plot_cases_or_deaths_bycounty_linear_fromdate(
            inc_data, regionName, ax_cases, type_disp = 'cases',
            days_from_beginning = day, doTitle = False,
            maxnum_colorbar = maxnum_colorbar_cases,
            plot_artists = cases_plot_artists, startdate = startdate )
        plot_cases_deaths_region_linear_fromdate(
            inc_data, regionName, ax_cases_plot, ax_death_plot,
            days_from_beginning = day, doTitle = False,
            startdate = startdate )
        ax_leg_txt.set_text( '\n'.join([
            regionName,
            'First COVID-19 CASE: %s' % first_date.strftime( '%d-%m-%Y' ),
            'Latest COVID-19 CASE: %s' % last_date.strftime( '%d-%m-%Y' ),
            '--',
            'Most County Cases',
            'After %s: %s' % ( startdate.strftime( '%d-%m-%Y' ),
                            get_string_commas_num( cases_max ) ),
            '%s, %s' % ( cs_cases['county'], cs_cases['state'] ),
            #
            '--',
            'Most County Deaths',
            'After %s: %s' % ( startdate.strftime( '%d-%m-%Y' ),
                              get_string_commas_num( death_max ) ),
            '%s, %s' % ( cs_death['county'], cs_death['state'] ),
            #
            '--',
            'Showing Day %d / %d' % ( day, last_timedelta_fromdate.days ),
            'After %s' % startdate.strftime( '%d-%m-%Y' ) ] ) )
        canvas = FigureCanvasAgg( fig )
        fname = os.path.join( dirname, 'covid19_fromdate_%s_%s_%s.%04d.png' % (
            prefix, startdate.strftime('%d%m%Y'), last_date.strftime('%d%m%Y'), day ) )
        canvas.print_figure( fname, bbox_inches = 'tight' )
        autocrop_image.autocrop_image( fname, fixEven = True )
        fnames.append( fname )
    return fnames

def create_summary_cases_or_deaths_movie_from_startdate(
    data = core.get_msa_data( 'bayarea' ), maxnum_colorbar = 5000.0,
    type_disp = 'cases', dirname = os.getcwd( ), startdate = _default_startdate ):
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
    prefix = data[ 'prefix' ]
    regionName = data[ 'region name' ]
    counties_and_states = list( map( core.get_county_state, data[ 'fips' ] ) )
    inc_data = core.get_incident_data( data )
    assert( startdate in set( inc_data['df'].date ) )
    last_timedelta_fromdate = max( inc_data['df'].date ) - startdate
    #
    all_days_from_begin = list(range(last_timedelta_fromdate.days + 1 ) )
    numprocs = multiprocessing.cpu_count( )
    if data['prefix'] != 'conus': input_status = { 'doSmarter' : False, 'resolution' : 'h' }
    else: input_status = { 'doSmarter' : True, 'resolution' : 'i' }
    def myfunc( input_tuple ):
        days_collection, i_status = input_tuple
        time00 = i_status[ 'time00' ]
        resolution = i_status[ 'resolution' ]
        doSmarter = i_status[ 'doSmarter' ]
        days_coll_sorted = sorted( days_collection )
        fig = Figure( )
        fig.set_size_inches([24,18])
        ax = fig.add_subplot(111)
        plot_artists = { }
        fnames = [ ]
        for day in sorted( set( days_collection ) ):
            plot_cases_or_deaths_bycounty_linear_fromdate(
                inc_data, regionName, ax, type_disp = type_disp, days_from_beginning = day,
                resolution = resolution, doSmarter = doSmarter, plot_artists = plot_artists,
                startdate = _default_startdate )
            canvas = FigureCanvasAgg( fig )
            fname = os.path.join( tmp_dirname, 'covid19_%s_%s_%s_%s.%04d.png' % (
                prefix, type_disp, startdate.strftime('%d%m%Y' ), last_date.strftime('%d%m%Y'), day ) )
            canvas.print_figure( fname, bbox_inches = 'tight' )
            autocrop_image.autocrop_image( fname, fixEven = True )
            fnames.append( fname )
        logging.info( 'took %0.3f seconds to process %d of %d days.' % (
            time.time( ) - time00, len( fnames ), len( all_days_from_begin ) ) )
        return fnames

    input_status[ 'time00' ] = time.time( )
    with multiprocessing.Pool( processes = numprocs ) as pool:
        input_tuples = list(zip(map(lambda idx: all_days_from_begin[idx::numprocs], range(numprocs)),
                                [ input_status ] * numprocs ) )
        for tup in input_tuples:
            days_collection, _ = tup
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
    proc = subprocess.Popen([
        ffmpeg_exec, '-y', '-r', '5', '-f', 'image2', '-i', allfile_name,
        '-vcodec', 'libx264', '-crf', '25', '-pix_fmt', 'yuv420p',
        movie_name ], stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    stdout_val, stderr_val = proc.communicate( )
    #
    ## now later remove those images and then remove the directory
    list(map(lambda fname: os.remove( fname ), allfiles ) )
    shutil.rmtree( tmp_dirname )
    return os.path.basename( movie_name ) # for now return basename        

def create_summary_movie_from_startdate(
    data = core.get_msa_data( 'bayarea' ),
    maxnum_colorbar_cases = 5000.0,
    maxnum_colorbar_death = 500.0,
    dirname = os.getcwd( ),
    startdate = _default_startdate ):
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
    prefix = data[ 'prefix' ]
    regionName = data[ 'region name' ]
    counties_and_states = list( map( core.get_county_state, data[ 'fips' ] ) )
    inc_data = core.get_incident_data( data )
    assert( startdate in set( inc_data['df'].date ) )
    last_timedelta_fromdate = max( inc_data['df'].date ) - startdate
    #
    all_days_from_begin = list(range(last_timedelta_fromdate.days + 1 ) )
    def myfunc( input_tuple ):
        days_collection, time00 = input_tuple
        fnames = create_plots_days_from_startdate(
            inc_data, regionName, dirname = tmp_dirname,
            days_from_beginning = days_collection, prefix = prefix,
            maxnum_colorbar_cases = maxnum_colorbar_cases,
            maxnum_colorbar_death = maxnum_colorbar_death,
            startdate = startdate )
        logging.info( 'took %0.3f seconds to process %d of %d days.' % (
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
                logging.info( 'error days collection: %s.' % days_collection )
        allfiles = sorted(chain.from_iterable( pool.map( myfunc, input_tuples ) ) )
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
    proc = subprocess.Popen([ ffmpeg_exec, '-y', '-r', '5', '-f', 'image2', '-i', allfile_name,
                             '-vcodec', 'libx264', '-crf', '25', '-pix_fmt', 'yuv420p',
                             movie_name ], stdout = subprocess.PIPE,
                            stderr = subprocess.STDOUT )
    stdout_val, stderr_val = proc.communicate( )
    #
    ## now later remove those images and then remove the directory
    list(map(lambda fname: os.remove( fname ), allfiles ) )
    shutil.rmtree( tmp_dirname )
    return os.path.basename( movie_name )
