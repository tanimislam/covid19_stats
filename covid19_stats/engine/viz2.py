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
    maxnum_colorbar = 5000.0, doTitle = True, plot_artists = { },
    poly_line_width = 1.0, doSmarter = False, rows = 1, cols = 1, num = 1 ):
    cases_dict = { 'cases' : 'cases_new', 'deaths' : 'death_new' }
    assert( type_disp in cases_dict )
    assert( days_from_beginning >= inc_data['df_7day']['days_from_beginning'].min( ) )
    assert( days_from_beginning <= inc_data['df_7day']['days_from_beginning'].max( ) )
    assert( maxnum_colorbar > 1 )
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
                '%s 7 day average new: %s' % ( type_disp, get_string_commas_num_float( num_tot ) ) ]),
            color = ( 0.0, 0.0, 0.0, 0.8 ),
            fontsize = 18, fontweight = 'bold', transform = ax.transAxes,
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

def plot_cases_deaths_rate_region( inc_data, ax, days_from_beginning = 7, doTitle = True ):
    assert( 'region name' in inc_data )
    assert( days_from_beginning >= 7 )
    assert( days_from_beginning <= inc_data[ 'last day' ] )
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
    ax.lines[0].set_label( 'new cases/day: %s / %s (max)' % tuple(map(get_string_commas_num_float, (num_cases_new, num_cases_new_max ) ) ) )
    ax.lines[1].set_label( 'new death/day: %s / %s (max)' % tuple(map(get_string_commas_num_float, (num_death_new, num_death_new_max ) ) ) )
    #
    ax.set_xlim(7.0, inc_data[ 'last day' ] )
    ax.set_ylim(1.0, 1.15 * df_cases_deaths_7day_region.cases_new.max( ) )
    ax.set_aspect( ( inc_data[ 'last day' ] - 7.0 ) /
                  numpy.log10( 1.15 * df_cases_deaths_7day_region.cases_new.max( ) ) )
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
        txt.set_fontsize( 18 )
        txt.set_fontweight( 'bold' )

def create_plots_rate_daysfrombeginning(
    inc_data, days_from_beginning = [ 7 ], dirname = os.getcwd( ) ):
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
        maxnum_colorbar = 5000.0,
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
    maxnum_death_7day_rate = max(
        list(map(lambda fips: inc_data[ 'df_7day' ][ 'deaths_%s_7day_new' % fips ].max( ), inc_data[ 'fips' ] ) ) )
    maxnum_cases_7day_rate = max(
        list(map(lambda fips: inc_data[ 'df_7day'][ 'cases_%s_7day_new' % fips ].max( ), inc_data[ 'fips' ] ) ) )
    maxnum_colorbar_death = find_plausible_maxnum( maxnum_death_7day_rate )
    maxnum_colorbar_cases = find_plausible_maxnum( maxnum_cases_7day_rate )
    plot_cases_or_deaths_rate_bycounty(
        inc_data, fig, type_disp = 'deaths',
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar_death,
        plot_artists = death_plot_artists, doSmarter = doSmarter,
        rows = 2, cols = 2, num = 2 )
    plot_cases_or_deaths_rate_bycounty(
        inc_data, fig, type_disp = 'cases',
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar_cases,
        plot_artists = cases_plot_artists, doSmarter = doSmarter,
        rows = 2, cols = 2, num = 4 )
    plot_cases_deaths_rate_region(
        inc_data, ax_cd, days_from_beginning = first_day, doTitle = False )
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
    ax_leg.set_aspect( 1.0 )
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
            maxnum_colorbar = maxnum_colorbar_death,
            plot_artists = death_plot_artists,
            rows = 2, cols = 2, num = 2 )
        plot_cases_or_deaths_rate_bycounty(
            inc_data, fig, type_disp = 'cases',
            days_from_beginning = day, doTitle = False,
            maxnum_colorbar = maxnum_colorbar_cases,
            plot_artists = cases_plot_artists,
            rows = 2, cols = 2, num = 4 )
        plot_cases_deaths_rate_region(
            inc_data, ax_cd,
            days_from_beginning = day, doTitle = False )
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
        maxnum_7day_rate = max(
            list(map(lambda fips: inc_data[ 'df_7day' ][ '%s_%s_7day_new' % ( case, fips ) ].max( ),
                     inc_data[ 'fips' ] ) ) )
        maxnum_colorbar = find_plausible_maxnum( maxnum_7day_rate )
        plot_cases_or_deaths_rate_bycounty(
            inc_data, fig_mine, type_disp = case,
            days_from_beginning = inc_data[ 'last day' ],
            maxnum_colorbar = maxnum_colorbar, doTitle = True, doSmarter = doSmarter )
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

