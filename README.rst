README
======

Hello world! This is my COVID-19 tracker. This is not nearly as sophisticated as what’s in `ncov2019.live`_, and described in `this New Yorker article`_.

I have made major changes in the functionality and implementation from the original commits, since commit `#78917`_ for instance.

* The API code has been refactored into the ``covid19_stats.engine`` subdirectory, and is divided into three main submodules: ``covid19_stats.engine.core`` provides the higher level API calls for processing the COVID-19 data; ``covid19_stats.engine.gis`` provides the lower-level APIs to write out, read in, and process the raw GIS data provided mainly by the US Census Bureau; and ``covid19_stats.engine.viz`` does the visualization part.

* The command line interfaces (CLI) back-ends live in ``covid19_stats.cli``. One of the command line interfaces, ``covid19_update_database``, updates the git submodule (the `NY Times COVID-19 repository`_) with the *latest* data. Previously, one updated the database by manually running, from the repository's top level directory,

  .. code-block:: console

     git -C covid19_stats/covid-19-data pull origin master
  
* The ``testing`` subdirectory contains `Jupyter Notebooks`_ that illuminate bits and pieces of this COVID-19 tracker’s functionality.

Here is some output from using this COVID-19 tracker. The data lives underneath `https://tanimislam.github.com/covid19movies <https://tanimislam.github.com/covid19movies>`_

* The summary of COVID-19 statistics for the top 50 MSAs by estimated 2019 population.
  
  .. list-table:: COVID-19 STATS FOR 50 METROS AS OF 02 FEBRUARY 2021
     :widths: auto

     * - RANK
       - IDENTIFIER
       - NAME
       - POPULATION
       - FIRST INC.
       - NUM DAYS
       - NUM CASES
       - NUM DEATHS
       - MAX CASE COUNTY
       - MAX CASE COUNTY NAME
     * - 1
       - nyc
       - NYC Metro Area
       - 19,216,182
       - 01 March 2020
       - 338
       - 1,563,506
       - 52,766
       - 617,406
       - New York City, New York
     * - 2
       - losangeles
       - LA Metro Area
       - 18,711,436
       - 25 January 2020
       - 374
       - 1,992,750
       - 25,813
       - 1,121,349
       - Los Angeles County, California
     * - 3
       - chicago
       - Chicago Metro Area
       - 9,458,539
       - 24 January 2020
       - 375
       - 822,368
       - 15,044
       - 455,138
       - Cook County, Illinois
     * - 4
       - dallas
       - Dallas Metro Area
       - 7,573,136
       - 09 March 2020
       - 330
       - 695,663
       - 7,390
       - 261,382
       - Dallas County, Texas
     * - 5
       - houston
       - Houston Metro Area
       - 7,066,141
       - 04 March 2020
       - 335
       - 487,049
       - 6,021
       - 320,744
       - Harris County, Texas
     * - 6
       - bayarea
       - Bay Area
       - 6,860,207
       - 31 January 2020
       - 368
       - 329,311
       - 3,956
       - 102,836
       - Santa Clara County, California
     * - 7
       - dc
       - DC Metro Area
       - 6,280,487
       - 05 March 2020
       - 334
       - 366,095
       - 5,880
       - 68,323
       - Prince George's County, Maryland
     * - 8
       - miami
       - Miami Metro Area
       - 6,166,488
       - 06 March 2020
       - 333
       - 658,171
       - 9,225
       - 375,321
       - Miami-Dade County, Florida
     * - 9
       - philadelphia
       - Philadelphia Metro Area
       - 6,102,434
       - 06 March 2020
       - 333
       - 414,217
       - 10,231
       - 110,793
       - Philadelphia County, Pennsylvania
     * - 10
       - atlanta
       - Atlanta Metro Area
       - 6,020,364
       - 02 March 2020
       - 337
       - 478,722
       - 5,930
       - 84,277
       - Gwinnett County, Georgia
     * - 11
       - phoenix
       - Phoenix Metro Area
       - 4,948,203
       - 26 January 2020
       - 373
       - 521,027
       - 8,239
       - 478,097
       - Maricopa County, Arizona
     * - 12
       - boston
       - Boston Metro Area
       - 4,873,019
       - 01 February 2020
       - 367
       - 351,697
       - 9,585
       - 102,781
       - Middlesex County, Massachusetts
     * - 13
       - detroit
       - Detroit Metro Area
       - 4,319,629
       - 10 March 2020
       - 329
       - 247,933
       - 8,251
       - 97,255
       - Wayne County, Michigan
     * - 14
       - seattle
       - Seattle Metro Area
       - 3,979,845
       - 21 January 2020
       - 378
       - 142,892
       - 2,212
       - 78,680
       - King County, Washington
     * - 15
       - minneapolis
       - Minneapolis Metro Area
       - 3,640,043
       - 06 March 2020
       - 333
       - 288,434
       - 3,827
       - 96,097
       - Hennepin County, Minnesota
     * - 16
       - sandiego
       - San Diego Metro Area
       - 3,338,330
       - 10 February 2020
       - 358
       - 240,113
       - 2,629
       - 240,113
       - San Diego County, California
     * - 17
       - tampa
       - Tampa Metro Area
       - 3,194,831
       - 01 March 2020
       - 338
       - 201,626
       - 3,530
       - 101,551
       - Hillsborough County, Florida
     * - 18
       - denver
       - Denver Metro Area
       - 2,967,239
       - 05 March 2020
       - 334
       - 208,598
       - 3,017
       - 55,979
       - Denver County, Colorado
     * - 19
       - stlouis
       - St. Louis Metro Area
       - 2,803,228
       - 07 March 2020
       - 332
       - 244,646
       - 4,147
       - 84,001
       - St. Louis County, Missouri
     * - 20
       - baltimore
       - Baltimore Metro Area
       - 2,800,053
       - 08 March 2020
       - 331
       - 154,408
       - 3,091
       - 47,641
       - Baltimore County, Maryland
     * - 21
       - charlotte
       - Charlotte Metro Area
       - 2,636,883
       - 11 March 2020
       - 328
       - 214,498
       - 2,411
       - 87,233
       - Mecklenburg County, North Carolina
     * - 22
       - orlando
       - Orlando Metro Area
       - 2,608,147
       - 12 March 2020
       - 327
       - 184,650
       - 2,157
       - 104,286
       - Orange County, Florida
     * - 23
       - sanantonio
       - San Antonio Metro Area
       - 2,550,960
       - 12 February 2020
       - 356
       - 211,791
       - 3,093
       - 176,802
       - Bexar County, Texas
     * - 24
       - portland
       - Portland Metro Area
       - 2,492,412
       - 28 February 2020
       - 340
       - 85,339
       - 1,112
       - 30,234
       - Multnomah County, Oregon
     * - 25
       - sacramento
       - Sacramento Metro Area
       - 2,363,730
       - 21 February 2020
       - 347
       - 125,654
       - 1,709
       - 86,855
       - Sacramento County, California
     * - 26
       - pittsburgh
       - Pittsburgh Metro Area
       - 2,317,600
       - 13 March 2020
       - 326
       - 145,673
       - 3,376
       - 69,837
       - Allegheny County, Pennsylvania
     * - 27
       - lasvegas
       - Las Vegas Metro Area
       - 2,266,715
       - 05 March 2020
       - 334
       - 215,469
       - 3,313
       - 215,469
       - Clark County, Nevada
     * - 28
       - austin
       - Austin Metro Area
       - 2,227,083
       - 13 March 2020
       - 326
       - 136,751
       - 1,389
       - 70,089
       - Travis County, Texas
     * - 29
       - cincinnati
       - Cincinnati Metro Area
       - 2,221,208
       - 14 March 2020
       - 325
       - 185,282
       - 1,357
       - 67,772
       - Hamilton County, Ohio
     * - 30
       - kansascity
       - Kansas City Metro Area
       - 2,157,990
       - 07 March 2020
       - 332
       - 132,058
       - 1,596
       - 50,030
       - Johnson County, Kansas
     * - 31
       - columbus
       - Columbus Metro Area
       - 2,122,271
       - 14 March 2020
       - 325
       - 170,808
       - 1,184
       - 105,457
       - Franklin County, Ohio
     * - 32
       - indianapolis
       - Indianapolis Metro Area
       - 2,074,537
       - 06 March 2020
       - 333
       - 187,464
       - 3,093
       - 87,059
       - Marion County, Indiana
     * - 33
       - cleveland
       - Cleveland Metro Area
       - 2,048,449
       - 09 March 2020
       - 330
       - 144,460
       - 1,848
       - 89,554
       - Cuyahoga County, Ohio
     * - 34
       - nashville
       - Nashville Metro Area
       - 1,934,317
       - 05 March 2020
       - 334
       - 216,942
       - 2,193
       - 85,066
       - Davidson County, Tennessee
     * - 35
       - virginiabeach
       - Virginia Beach Metro Area
       - 1,768,901
       - 09 March 2020
       - 330
       - 101,057
       - 1,103
       - 26,580
       - Virginia Beach city, Virginia
     * - 36
       - providence
       - Providence Metro Area
       - 1,624,578
       - 14 March 2020
       - 325
       - 152,831
       - 3,431
       - 74,238
       - Providence County, Rhode Island
     * - 37
       - milwaukee
       - Milwaukee Metro Area
       - 1,575,179
       - 11 March 2020
       - 328
       - 169,993
       - 1,879
       - 103,672
       - Milwaukee County, Wisconsin
     * - 38
       - jacksonville
       - Jacksonville Metro Area
       - 1,559,514
       - 10 March 2020
       - 329
       - 127,033
       - 1,489
       - 82,738
       - Duval County, Florida
     * - 39
       - oklahomacity
       - Oklahoma City Metro Area
       - 1,408,950
       - 13 March 2020
       - 326
       - 132,909
       - 1,051
       - 75,542
       - Oklahoma County, Oklahoma
     * - 40
       - raleigh
       - Raleigh Metro Area
       - 1,390,785
       - 03 March 2020
       - 336
       - 90,232
       - 644
       - 69,557
       - Wake County, North Carolina
     * - 41
       - memphis
       - Memphis Metro Area
       - 1,346,045
       - 08 March 2020
       - 331
       - 125,711
       - 1,908
       - 83,489
       - Shelby County, Tennessee
     * - 42
       - richmond
       - Richmond Metro Area
       - 1,291,900
       - 12 March 2020
       - 327
       - 73,132
       - 964
       - 19,449
       - Chesterfield County, Virginia
     * - 43
       - neworleans
       - New Orleans Metro Area
       - 1,270,530
       - 09 March 2020
       - 330
       - 105,410
       - 2,304
       - 41,512
       - Jefferson Parish, Louisiana
     * - 44
       - louisville
       - Louisville/Jefferson County Metro Area
       - 1,265,108
       - 08 March 2020
       - 331
       - 110,452
       - 1,320
       - 68,205
       - Jefferson County, Kentucky
     * - 45
       - saltlakecity
       - Salt Lake City Metro Area
       - 1,232,696
       - 25 February 2020
       - 343
       - 136,693
       - 713
       - 130,734
       - Salt Lake County, Utah
     * - 46
       - hartford
       - Hartford Metro Area
       - 1,204,877
       - 14 March 2020
       - 325
       - 81,360
       - 2,605
       - 64,818
       - Hartford County, Connecticut
     * - 47
       - buffalo
       - Buffalo Metro Area
       - 1,127,983
       - 15 March 2020
       - 324
       - 71,654
       - 1,752
       - 57,858
       - Erie County, New York
     * - 48
       - birmingham
       - Birmingham Metro Area
       - 1,090,435
       - 13 March 2020
       - 326
       - 107,585
       - 1,730
       - 67,359
       - Jefferson County, Alabama
     * - 49
       - grandrapids
       - Grand Rapids Metro Area
       - 1,077,370
       - 12 March 2020
       - 327
       - 82,467
       - 1,149
       - 49,522
       - Kent County, Michigan
     * - 50
       - rochester
       - Rochester Metro Area
       - 1,069,644
       - 11 March 2020
       - 328
       - 63,843
       - 1,186
       - 48,305
       - Monroe County, New York

.. _png_figures:
	 
* The COVID-19 trends in cases and deaths for these 6 metropolitan areas as of 02 FEBRUARY 2021: SF Bay Area; Washington, DC; Richmond, VA; NYC; Los Angeles; and New Orleans.

  .. list-table::
     :widths: auto

     * - |cds_bayarea|
       - |cds_dc|
       - |cds_richmond|
     * - SF Bay Area
       - Washington, DC
       - Richmond, VA
     * - |cds_nyc|
       - |cds_losangeles|
       - |cds_neworleans|
     * - NYC Metro
       - Los Angeles
       - New Orleans

.. _gif_animations:
  
* GIF'd video animations of the COVID-19 trends in cases/deaths for NYC, Chicago, Seattle, SF Bay Area, DC, and Richmond, as of 02 FEBRUARY 2021.	  

  .. list-table::
     :widths: auto

     * - |anim_gif_nyc|
       - |anim_gif_chicago|
       - |anim_gif_seattle|
     * - `NYC Metro <https://tanimislam.github.io/covid19movies/covid19_nyc_LATEST.mp4>`_
       - `Chicago <https://tanimislam.github.io/covid19movies/covid19_chicago_LATEST.mp4>`_
       - `Seattle <https://tanimislam.github.io/covid19movies/covid19_seattle_LATEST.mp4>`_
     * - |anim_gif_bayarea|
       - |anim_gif_dc|
       - |anim_gif_richmond|
     * - `SF Bay Area <https://tanimislam.github.io/covid19movies/covid19_bayarea_LATEST.mp4>`_
       - `Washington, DC <https://tanimislam.github.io/covid19movies/covid19_dc_LATEST.mp4>`_
       - `Richmond, VA <https://tanimislam.github.io/covid19movies/covid19_richmond_LATEST.mp4>`_

  And here is the animation for the continental United States as of 02 FEBRUARY 2021

  .. list-table::
     :widths: auto

     * - |anim_gif_conus|
     * - `Continental United States <https://tanimislam.github.io/covid19movies/covid19_conus_LATEST.mp4>`_

* GIF'd video animations of the COVID-19 trends in cases/deaths for California, Texas, Florida, and Virginia, as of 02 FEBRUARY 2021.

  .. list-table::
     :widths: auto

     * - |anim_gif_california|
       - |anim_gif_texas|
     * - `California <https://tanimislam.github.io/covid19movies/covid19_california_LATEST.mp4>`_
       - `Texas <https://tanimislam.github.io/covid19movies/covid19_texas_LATEST.mp4>`_
     * - |anim_gif_florida|
       - |anim_gif_virginia|
     * - `Florida <https://tanimislam.github.io/covid19movies/covid19_florida_LATEST.mp4>`_
       - `Virginia <https://tanimislam.github.io/covid19movies/covid19_virginia_LATEST.mp4>`_

The comprehensive documentation lives in HTML created with Sphinx_, and now in the `COVID-19 Stats GitHub Page`_ for this project. To generate the documentation,

* Go to the ``docs`` subdirectory.
* In that directory, run ``make html``.
* Load ``docs/build/html/index.html`` into a browser to see the documentation.
  
.. _`NY Times COVID-19 repository`: https://github.com/nytimes/covid-19-data
.. _`ncov2019.live`: https://ncov2019.live
.. _`this New Yorker article`: https://www.newyorker.com/magazine/2020/03/30/the-high-schooler-who-became-a-covid-19-watchdog
.. _`#78917`: https://github.com/tanimislam/covid19_stats/commit/78917dd20c43bd65320cf51958fa481febef4338
.. _`Jupyter Notebooks`: https://jupyter.org
.. _Basemap: https://matplotlib.org/basemap
.. _`Github flavored Markdown`: https://github.github.com/gfm
.. _reStructuredText: https://docutils.sourceforge.io/rst.html
.. _`Pandas DataFrame`: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.htm
.. _MP4: https://en.wikipedia.org/wiki/MPEG-4_Part_14
.. _Sphinx: https://www.sphinx-doc.org/en/master
.. _`COVID-19 Stats GitHub Page`: https://tanimislam.github.io/covid19_stats


.. STATIC IMAGES

.. |cds_bayarea| image:: https://tanimislam.github.io/covid19movies/covid19_bayarea_cds_LATEST.png
   :width: 100%
   :align: middle

.. |cds_dc| image:: https://tanimislam.github.io/covid19movies/covid19_dc_cds_LATEST.png
   :width: 100%
   :align: middle

.. |cds_richmond| image:: https://tanimislam.github.io/covid19movies/covid19_richmond_cds_LATEST.png
   :width: 100%
   :align: middle

.. |cds_nyc| image:: https://tanimislam.github.io/covid19movies/covid19_nyc_cds_LATEST.png
   :width: 100%
   :align: middle

.. |cds_losangeles| image:: https://tanimislam.github.io/covid19movies/covid19_losangeles_cds_LATEST.png
   :width: 100%
   :align: middle

.. |cds_neworleans| image:: https://tanimislam.github.io/covid19movies/covid19_neworleans_cds_LATEST.png
   :width: 100%
   :align: middle
	   
.. GIF ANIMATIONS MSA

.. |anim_gif_nyc| image:: https://tanimislam.github.io/covid19movies/covid19_nyc_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_chicago| image:: https://tanimislam.github.io/covid19movies/covid19_chicago_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_seattle| image:: https://tanimislam.github.io/covid19movies/covid19_seattle_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_bayarea| image:: https://tanimislam.github.io/covid19movies/covid19_bayarea_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_dc| image:: https://tanimislam.github.io/covid19movies/covid19_dc_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_richmond| image:: https://tanimislam.github.io/covid19movies/covid19_richmond_LATEST.gif
   :width: 100%
   :align: middle

.. GIF ANIMATIONS CONUS

.. |anim_gif_conus| image:: https://tanimislam.github.io/covid19movies/covid19_conus_LATEST.gif
   :width: 100%
   :align: middle

.. GIF ANIMATIONS STATE

.. |anim_gif_california| image:: https://tanimislam.github.io/covid19movies/covid19_california_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_texas| image:: https://tanimislam.github.io/covid19movies/covid19_texas_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_florida| image:: https://tanimislam.github.io/covid19movies/covid19_florida_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_virginia| image:: https://tanimislam.github.io/covid19movies/covid19_virginia_LATEST.gif
   :width: 100%
   :align: middle
