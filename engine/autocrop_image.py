import os, numpy, logging, shlex, subprocess, uuid
from PIL import Image
from PyPDF2 import PdfFileReader, PdfFileWriter
from distutils.spawn import find_executable

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
  #
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


#
## borrowed this code from https://gist.github.com/jpscaletti/7321281
## small changes:
## 1) all attributes and methods except for crop_pdf() are underscored
## 2) first search for "gs" executable. If there, then functionality can work
## 3) made a new method, crop_pdf_singlepage(), only for cropping SINGLE page (image) PDF files
"""
Pdfcrop
=======

Based on pdfcrop.pl_. Uses the BoundingBox [#]_

Dependencies:
  - PyPDF2_
  - ghostscript_


.. [#] http://commons.wikimedia.org/wiki/File:PDF_BOX_01.svg

.. _PyPDF2: https://github.com/mstamy2/PyPDF2/
.. _ghostscript: http://www.ghostscript.com/
.. _pdfcrop.pl: ftp://ftp.tex.ac.uk/tex-archive/support/pdfcrop/pdfcrop.pl

"""
_root_logger = logging.getLogger()
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
_root_logger.addHandler(_handler)
_devnull = open(os.devnull, 'w')

def _bbox(value):
  """
  >>> _bbox('%%BoundingBox: 217 208 566 357')
  [217, 208, 566, 357]
  """
  _, bbox = value.split(':')
  return list(map(int, bbox.split()))


def _hiresbb(value):
  """
  >>> _hiresbb('%%HiResBoundingBox: 98.765997 63.935998 694.025979 497.591774')
  [98.765997, 63.935998, 694.025979, 497.591774]
  """
  _, bbox = value.split(':')
  return list(map(float, bbox.split()))


def _get_boundingbox(pdfpath, hiresbb=False):
  """
  Given a pdf file path, return its bounding box.
  
  :hiresbb: Return hiresBoundingbox, instead of Boundingbox.

  >>> _get_boundingbox('/path/to/mypdf.pdf')   # doctest: +SKIP
  [[23, 34, 300, 555], [0, 0, 300, 555]]
  """
  gs_exec = find_executable( 'gs' )
  if gs_exec is None:
    raise IOError("Error, cannot find ghostscript executable")
  command = [ gs_exec, ] + shlex.split('-dSAFER -sDEVICE=bbox -dNOPAUSE -dBATCH' )
  command.append(pdfpath)
  process = subprocess.Popen(command, stdout=_devnull, stderr=subprocess.PIPE)
  out, err = process.communicate()  # gs sends output to stderr
  err = err.decode('utf-8')
  if hiresbb:
    return [_hiresbb(line) for line in err.split('\n') if line.startswith('%%HiResBoundingBox')]
  return [_bbox(line) for line in err.split('\n') if line.startswith('%%BoundingBox')]


def _make_pdf(i, fname, page):
  pdf_out = PdfFileWriter()
  outputfile = '{0}{1}'.format(i, fname)
  with open(outputfile, 'wb') as fout:
    pdf_out.addPage(page)
    pdf_out.write(fout)

def _crop_pdf(inputfile, outputfile=None):
  logger = logging.getLogger(__name__)
  bboxes = _get_boundingbox(inputfile)
  if outputfile is None:
    outputfile = 'cropped.{0}{1}'.format(*os.path.splitext(inputfile))
  logger.info('Writing pdf output to %s', outputfile)
  with open(inputfile, 'rb') as fin:
    pdf_in = PdfFileReader(fin)
    for i, bbox in enumerate(bboxes):
      left, bottom, right, top = bbox
      page = pdf_in.getPage(i)
      logger.debug('Original mediabox: %s, %s', page.mediaBox.lowerLeft, page.mediaBox.upperRight)
      logger.debug('Original boundingbox: %s, %s', (left, bottom), (right, top))
      page.mediaBox.lowerLeft = (left, bottom)
      page.mediaBox.upperRight = (right, top)
      logger.debug('modified mediabox: %s, %s', page.mediaBox.lowerLeft, page.mediaBox.upperRight)
      _make_pdf(i, outputfile, page)

def autocrop_image_pdf(inputfile, outputfile = None ):
  logger = logging.getLogger(__name__)
  bboxes = _get_boundingbox(inputfile)
  assert( len( bboxes ) == 1 ) # single page PDF
  sameFile = False
  if outputfile is None:
    sameFile = True
    outputfile = '%s.pdf' % ''.join(map(lambda idx: str(uuid.uuid4()), range(2)))
  pdf_in = PdfFileReader( open( inputfile, 'rb' ) )
  left, bottom, right, top = bboxes[0]
  page = pdf_in.getPage( 0 )
  logger.debug('Original mediabox: %s, %s', page.mediaBox.lowerLeft, page.mediaBox.upperRight)
  logger.debug('Original boundingbox: %s, %s', (left, bottom), (right, top))
  page.mediaBox.lowerLeft = (left, bottom)
  page.mediaBox.upperRight = (right, top)
  logger.debug('modified mediabox: %s, %s', page.mediaBox.lowerLeft, page.mediaBox.upperRight)
  #
  ## write out to this new file
  pdf_out = PdfFileWriter( )
  pdf_out.addPage( page )
  pdf_out.write( open(outputfile, 'wb') )
  if sameFile: os.rename( outputfile, inputfile )
  
