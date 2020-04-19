import os, sys, numpy
from PIL import Image, ImageChops

def autocrop_perproc(input_tuple):
    inputfilename, outputfilename = input_tuple
    val = autocrop_image(inputfilename, outputfilename = outputfilename )
    return inputfilename, val
    

def autocrop_image(inputfilename, outputfilename = None,
                   trans = False, fixEven = False ):
    im = Image.open(inputfilename)

    #
    ## if remove transparency, do the following
    ## follow instructions from https://twigstechtips.blogspot.com/2011/12/python-converting-transparent-areas-in.html
    if trans:
        im.convert( 'RGBA' )
        canvas = Image.new('RGBA', im.size, (255,255,255,255)) # Empty canvas colour (r,g,b,a)
        canvas.paste(im, mask = im) # Paste the image onto the canvas, using its alpha channel as mask
        im = canvas
    imd = numpy.asarray( im )
    rgba = numpy.array([ 255, 255, 255, 255 ], dtype=int )
    jdxvals, idxvals, _ = numpy.where( imd[:,:] != rgba )
    bbox = ( idxvals.min( ), jdxvals.min( ), idxvals.max( ), jdxvals.max( ) )
    if not bbox: return
    
    cropped = im.crop(bbox)
    #
    ## now what to do if we ensure width and heights are both even
    if fixEven:
        width_even = cropped.size[0]
        height_even= cropped.size[1]
        if width_even % 2 != 0: width_even += 1
        if height_even %2 != 0: height_even+= 1
        cropped = cropped.resize(( width_even, height_even ))
            
    if outputfilename is None:
        cropped.save(inputfilename)
    else:
        cropped.save(os.path.expanduser(outputfilename))
