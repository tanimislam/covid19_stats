def determine_corners_center_stereo( boundary_dict, scaling = 1.0 ):
    import scipy.optimize
    all_latlngs = numpy.concatenate( list(chain.from_iterable( boundary_dict.values( ) ) ), axis = 0 )
    phis = numpy.radians( all_latlngs[:,0] )
    thets = numpy.pi / 2 - numpy.radians( all_latlngs[:,1])
    v_z = numpy.array([
        numpy.mean( numpy.cos( phis ) * numpy.sin( thets ) ),
        numpy.mean( numpy.sin( phis ) * numpy.sin( thets ) ),
        numpy.mean( numpy.cos( thets ) ) ])
    v_z = v_z / numpy.linalg.norm( v_z )
    cand_phi = numpy.arctan2( v_z[1], v_z[0] )
    cand_thet= numpy.arccos( v_z[2] )
    #
    def penalty_centroid( thet, phi ):
        v_z = numpy.array([ numpy.cos( phi ) * numpy.sin( thet ), numpy.sin( phi ) * numpy.sin( thet ), numpy.cos( thet ) ] )
        v_y = numpy.array([ -numpy.cos( phi ) * numpy.cos( thet ), -numpy.sin( phi ) * numpy.cos( thet ), numpy.sin( thet ) ] )
        v_x = numpy.array([ -numpy.sin( phi ), numpy.cos( phi ), 0 ])
        v_z = v_z / numpy.linalg.norm( v_z )
        v_y = v_y / numpy.linalg.norm( v_y )
        v_x = v_x / numpy.linalg.norm( v_x )
        #
        ## position on unit sphere, +Y true north, +X true east
        zvals = numpy.cos( phis ) * numpy.sin( thets ) * v_z[0] + numpy.sin( phis ) * numpy.sin( thets ) * v_z[1] + numpy.cos( thets ) * v_z[2]
        xvals = numpy.cos( phis ) * numpy.sin( thets ) * v_x[0] + numpy.sin( phis ) * numpy.sin( thets ) * v_x[1] + numpy.cos( thets ) * v_x[2]
        yvals = numpy.cos( phis ) * numpy.sin( thets ) * v_y[0] + numpy.sin( phis ) * numpy.sin( thets ) * v_y[1] + numpy.cos( thets ) * v_y[2]
        #
        ## stereoproj
        Xvs = xvals / zvals
        Yvs = yvals / zvals
        pen_x = 0.5 * ( Xvs.max( ) + Xvs.min( ) )
        pen_y = 0.5 * ( Yvs.max( ) + Yvs.min( ) )
        return pen_x**2 + pen_y**2

    thet, phi = scipy.optimize.fmin(lambda vec: penalty_centroid( vec[0], vec[1] ), [ cand_thet, cand_phi ], disp = False )
    #
    ## central latlngs?
    lat_cent = 90.0 - numpy.degrees( thet )
    lng_cent = numpy.degrees( phi )
    #
    ## now determine the dataframe for stereographic projections
    df_latlng_stereos = pandas.DataFrame({ 'lat' : all_latlngs[:,1], 'lng' : all_latlngs[:,0] })
    #
    ## now stereo proj
    v_z = numpy.array([ numpy.cos( phi ) * numpy.sin( thet ), numpy.sin( phi ) * numpy.sin( thet ), numpy.cos( thet ) ] )
    v_y = numpy.array([ -numpy.cos( phi ) * numpy.cos( thet ), -numpy.sin( phi ) * numpy.cos( thet ), numpy.sin( thet ) ] )
    v_x = numpy.array([ -numpy.sin( phi ), numpy.cos( phi ), 0 ])
    v_z = v_z / numpy.linalg.norm( v_z )
    v_y = v_y / numpy.linalg.norm( v_y )
    v_x = v_x / numpy.linalg.norm( v_x )
    #
    ## position on unit sphere, +Y true north, +X true east
    zvals = numpy.cos( phis ) * numpy.sin( thets ) * v_z[0] + numpy.sin( phis ) * numpy.sin( thets ) * v_z[1] + numpy.cos( thets ) * v_z[2]
    xvals = numpy.cos( phis ) * numpy.sin( thets ) * v_x[0] + numpy.sin( phis ) * numpy.sin( thets ) * v_x[1] + numpy.cos( thets ) * v_x[2]
    yvals = numpy.cos( phis ) * numpy.sin( thets ) * v_y[0] + numpy.sin( phis ) * numpy.sin( thets ) * v_y[1] + numpy.cos( thets ) * v_y[2]
    #
    ## stereoproj
    Xvs = xvals / zvals
    Yvs = yvals / zvals
    df_latlng_stereos[ 'Xvs' ] = Xvs
    df_latlng_stereos[ 'Yvs' ] = Yvs
    lng_max = df_latlng_stereos[ df_latlng_stereos.Xvs == df_latlng_stereos.Xvs.max( ) ].lng.max( )
    lng_min = df_latlng_stereos[ df_latlng_stereos.Xvs == df_latlng_stereos.Xvs.min( ) ].lng.min( )
    lat_max = df_latlng_stereos[ df_latlng_stereos.Yvs == df_latlng_stereos.Yvs.max( ) ].lat.max( )
    lat_min = df_latlng_stereos[ df_latlng_stereos.Yvs == df_latlng_stereos.Yvs.min( ) ].lat.min( )
    return {
        'lat_cent' : lat_cent, 'lng_cent' : lng_cent,
        'lat_min' : lat_cent + scaling * ( lat_min - lat_cent ),
        'lat_max' : lat_cent + scaling * ( lat_max - lat_cent ),
        'lng_min' : lng_cent + scaling * ( lng_min - lng_cent ),
        'lng_max' : lng_cent + scaling * ( lng_max - lng_cent ) }
