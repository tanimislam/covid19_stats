import os, sys, numpy, titlecase, time, pandas
import subprocess, tempfile, shutil, datetime, logging
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
from nprstuff.core import autocrop_image
#
from covid19_stats.engine import gis, core, get_string_commas_num
from covid19_stats.engine.viz import (
    my_colorbar, create_and_draw_basemap, create_and_draw_basemap_smarter,
    determine_corners_center_stereo, display_fips_geom, display_fps, display_msa )
    
def plot_cases_or_deaths_bycounty(
    inc_data, regionName, ax, type_disp = 'cases', days_from_beginning = 0, resolution = 'h',
    maxnum_colorbar = 5000.0, doTitle = True, plot_artists = { },
    poly_line_width = 1.0, doSmarter = False ):
    assert( resolution in ( 'c', 'l', 'i', 'h', 'f' ) )
    assert( type_disp in ( 'cases', 'deaths' ) )
    assert( days_from_beginning >= 0 )
    assert( days_from_beginning <= inc_data[ 'last day' ] )
    assert( maxnum_colorbar > 1 )
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
        plot_artists[ 'sm' ] = ScalarMappable( norm = LogNorm( 1.0, maxnum_colorbar ), cmap = 'jet' )
    #
    ## draw boundaries if not defined
    boundaries = inc_data['boundaries']
    df_dfm = inc_data['df'][ inc_data['df']['days_from_beginning'] == days_from_beginning ].copy( )
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
    ax_deaths = fig.add_subplot(111)
    #
    ## first plot, get correct width multiplication
    sorted_days = sorted( set( days_from_beginning ) )
    first_day = min( days_from_beginning )
    plot_cases_or_deaths_bycounty(
        inc_data, regionName, ax_deaths, type_disp = 'deaths',
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar,
        plot_artists = { }, doSmarter = doSmarter )
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
    plot_cases_or_deaths_bycounty(
        inc_data, regionName, ax_deaths, type_disp = 'deaths',
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar,
        plot_artists = death_plot_artists, doSmarter = doSmarter )
    plot_cases_or_deaths_bycounty(
        inc_data, regionName, ax_cases, type_disp = 'cases',
        days_from_beginning = first_day, doTitle = False,
        maxnum_colorbar = maxnum_colorbar,
        plot_artists = cases_plot_artists, doSmarter = doSmarter )
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
    fname = os.path.join( dirname, 'covid19_%s_%s.%04d.png' % (
        prefix, last_date.strftime('%d%m%Y'), first_day ) )
    canvas.print_figure( fname, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( fname, fixEven = True )
    fnames.append( fname )
    #
    ## now do for the remaining days
    for day in sorted_days[1:]:
        plot_cases_or_deaths_bycounty(
            inc_data, regionName, ax_deaths, type_disp = 'deaths',
            days_from_beginning = day, doTitle = False,
            maxnum_colorbar = maxnum_colorbar,
            plot_artists = death_plot_artists )
        plot_cases_or_deaths_bycounty(
            inc_data, regionName, ax_cases, type_disp = 'cases',
            days_from_beginning = day, doTitle = False,
            maxnum_colorbar = maxnum_colorbar,
            plot_artists = cases_plot_artists )
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

def create_summary_cases_or_deaths_movie_frombeginning(
    data = core.get_msa_data( 'bayarea' ), maxnum_colorbar = 5000.0,
    type_disp = 'cases', dirname = os.getcwd( ) ):
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
    last_date = max( inc_data['df'].date )
    #
    all_days_from_begin = list(range(inc_data['last day'] + 1 ) )
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
            plot_cases_or_deaths_bycounty(
                inc_data, regionName, ax, type_disp = type_disp, days_from_beginning = day,
                resolution = resolution, doSmarter = doSmarter, plot_artists = plot_artists )
            canvas = FigureCanvasAgg( fig )
            fname = os.path.join( tmp_dirname, 'covid19_%s_%s_%s.%04d.png' % (
                prefix, type_disp, last_date.strftime('%d%m%Y'), day ) )
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

def create_summary_movie_frombeginning(
    data = core.get_msa_data( 'bayarea' ),
    maxnum_colorbar = 5000.0, dirname = os.getcwd( ) ):
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
    #
    all_days_from_begin = list(range(inc_data['last day'] + 1 ) )
    def myfunc( input_tuple ):
        days_collection, time00 = input_tuple
        fnames = create_plots_daysfrombeginning(
            inc_data, regionName, dirname = tmp_dirname,
            days_from_beginning = days_collection, prefix = prefix,
            maxnum_colorbar = maxnum_colorbar )
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

def get_summary_demo_data(
    data = core.get_msa_data( 'bayarea' ), maxnum_colorbar = 5000.0,
    dirname = os.getcwd( ) ):
    #
    ## now is dirname a directory
    assert( os.path.isdir( dirname ) )
    doSmarter = False
    if data[ 'prefix' ] == 'conus': doSmarter = True
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
        os.path.join( dirname, 'covid19_%s_%s.pkl.gz' % ( prefix, last_date_str ) ) )
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
    pngfile = os.path.abspath( os.path.join( dirname, '%s.png' % file_prefix ) )
    pdffile = os.path.abspath( os.path.join( dirname, '%s.pdf' % file_prefix ) )
    canvas.print_figure( pngfile, bbox_inches = 'tight' )
    canvas.print_figure( pdffile, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( pngfile )
    try: autocrop_image.autocrop_image_pdf( '%s.pdf' % file_prefix )
    except: pass
    #
    ## now create figures CASES
    fig1 = Figure( )
    ax1 = fig1.add_subplot(111)
    fig1.set_size_inches([ 12.0, 12.0 ])
    plot_cases_or_deaths_bycounty(
        inc_data, regionName, ax1, type_disp = 'cases',
        days_from_beginning = inc_data[ 'last day' ],
        maxnum_colorbar = maxnum_colorbar, doTitle = True, doSmarter = doSmarter )
    canvas = FigureCanvasAgg( fig1 )
    file_prefix = 'covid19_%s_cases_%s' % ( prefix, last_date_str )
    pngfile = os.path.abspath( os.path.join( dirname, '%s.png' % file_prefix ) )
    pdffile = os.path.abspath( os.path.join( dirname, '%s.pdf' % file_prefix ) )
    canvas.print_figure( pngfile, bbox_inches = 'tight' )
    canvas.print_figure( pdffile, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( pngfile )
    try: autocrop_image.autocrop_image_pdf( pdffile )
    except: pass
    #
    ## now create figures DEATHS
    fig2 = Figure( )
    ax2 = fig2.add_subplot(111)
    fig2.set_size_inches([ 12.0, 12.0 ])
    plot_cases_or_deaths_bycounty(
        inc_data, regionName, ax2, type_disp = 'deaths',
        days_from_beginning = inc_data[ 'last day' ],
        maxnum_colorbar = maxnum_colorbar, doTitle = True, doSmarter = doSmarter )
    canvas = FigureCanvasAgg( fig2 )
    file_prefix = 'covid19_%s_death_%s' % ( prefix, last_date_str )
    pngfile = os.path.abspath( os.path.join( dirname, '%s.png' % file_prefix ) )
    pdffile = os.path.abspath( os.path.join( dirname, '%s.pdf' % file_prefix ) )
    canvas.print_figure( pngfile, bbox_inches = 'tight' )
    canvas.print_figure( pdffile, bbox_inches = 'tight' )
    autocrop_image.autocrop_image( pngfile )
    try: autocrop_image.autocrop_image_pdf( pdffile )
    except: pass
