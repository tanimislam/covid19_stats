Hello world! This is my COVID-19 tracker. This is not nearly as sophisticated as what’s in `ncov2019.live`_, and described in `this New Yorker article`_.

I have made major changes in the functionality and implementation from the original commits, since commit `#78917`_ for instance.

* The API code has been refactored into the ``covid19_stats.engine`` subdirectory, and is divided into three main submodules: ``covid19_stats.engine.core`` provides the higher level API calls for processing the COVID-19 data; ``covid19_stats.engine.gis`` provides the lower-level APIs to write out, read in, and process the raw GIS data provided mainly by the US Census Bureau; and ``covid19_stats.engine.viz`` does the visualization part.

* The command line interfaces (CLI) back-ends live in ``covid19_stats.cli``. One of the command line interfaces, `covid19_update_database`_, updates the git submodule (the `NY Times COVID-19 repository`_) with the *latest* data. Previously, one updated the database by manually running, from the repository's top level directory,

  .. code-block:: console

     git -C covid19_stats/covid-19-data pull origin master
  
* The ``testing`` subdirectory contains `Jupyter Notebooks`_ that illuminate bits and pieces of this COVID-19 tracker’s functionality.

Here is some output from using this COVID-19 tracker. The data lives underneath `https://tanimislam.github.io/covid19movies <https://tanimislam.github.io/covid19movies>`_

* The summary of COVID-19 statistics for the top 50 MSAs by estimated 2019 population.
  
  .. list-table:: COVID-19 STATS FOR 50 METROS AS OF 11 FEBRUARY 2021
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
       - 347
       - 1,646,943
       - 54,321
       - 655,228
       - New York City, New York
     * - 2
       - losangeles
       - LA Metro Area
       - 18,711,436
       - 25 January 2020
       - 383
       - 2,053,922
       - 28,585
       - 1,159,135
       - Los Angeles County, California
     * - 3
       - chicago
       - Chicago Metro Area
       - 9,458,539
       - 24 January 2020
       - 384
       - 839,044
       - 15,594
       - 463,581
       - Cook County, Illinois
     * - 4
       - dallas
       - Dallas Metro Area
       - 7,573,136
       - 09 March 2020
       - 339
       - 730,900
       - 8,151
       - 271,816
       - Dallas County, Texas
     * - 5
       - houston
       - Houston Metro Area
       - 7,066,141
       - 04 March 2020
       - 344
       - 508,192
       - 6,495
       - 331,837
       - Harris County, Texas
     * - 6
       - bayarea
       - Bay Area
       - 6,860,207
       - 31 January 2020
       - 377
       - 341,327
       - 4,381
       - 106,372
       - Santa Clara County, California
     * - 7
       - dc
       - DC Metro Area
       - 6,280,487
       - 05 March 2020
       - 343
       - 381,875
       - 6,129
       - 70,493
       - Prince George's County, Maryland
     * - 8
       - miami
       - Miami Metro Area
       - 6,166,488
       - 06 March 2020
       - 342
       - 684,899
       - 9,601
       - 389,518
       - Miami-Dade County, Florida
     * - 9
       - philadelphia
       - Philadelphia Metro Area
       - 6,102,434
       - 06 March 2020
       - 342
       - 429,209
       - 10,634
       - 113,878
       - Philadelphia County, Pennsylvania
     * - 10
       - atlanta
       - Atlanta Metro Area
       - 6,020,364
       - 02 March 2020
       - 346
       - 500,850
       - 6,415
       - 87,746
       - Gwinnett County, Georgia
     * - 11
       - phoenix
       - Phoenix Metro Area
       - 4,948,203
       - 26 January 2020
       - 382
       - 540,060
       - 9,030
       - 495,621
       - Maricopa County, Arizona
     * - 12
       - boston
       - Boston Metro Area
       - 4,873,019
       - 01 February 2020
       - 376
       - 365,605
       - 9,977
       - 106,482
       - Middlesex County, Massachusetts
     * - 13
       - detroit
       - Detroit Metro Area
       - 4,319,629
       - 10 March 2020
       - 338
       - 252,963
       - 8,430
       - 98,998
       - Wayne County, Michigan
     * - 14
       - seattle
       - Seattle Metro Area
       - 3,979,845
       - 21 January 2020
       - 387
       - 147,208
       - 2,322
       - 81,084
       - King County, Washington
     * - 15
       - minneapolis
       - Minneapolis Metro Area
       - 3,640,043
       - 06 March 2020
       - 342
       - 293,345
       - 3,910
       - 97,742
       - Hennepin County, Minnesota
     * - 16
       - sandiego
       - San Diego Metro Area
       - 3,338,330
       - 10 February 2020
       - 367
       - 250,037
       - 2,955
       - 250,037
       - San Diego County, California
     * - 17
       - tampa
       - Tampa Metro Area
       - 3,194,831
       - 01 March 2020
       - 347
       - 209,344
       - 3,722
       - 105,142
       - Hillsborough County, Florida
     * - 18
       - denver
       - Denver Metro Area
       - 2,967,239
       - 05 March 2020
       - 343
       - 214,115
       - 3,071
       - 57,539
       - Denver County, Colorado
     * - 19
       - stlouis
       - St. Louis Metro Area
       - 2,803,228
       - 07 March 2020
       - 341
       - 250,533
       - 4,357
       - 85,990
       - St. Louis County, Missouri
     * - 20
       - baltimore
       - Baltimore Metro Area
       - 2,800,053
       - 08 March 2020
       - 340
       - 159,182
       - 3,232
       - 49,010
       - Baltimore County, Maryland
     * - 21
       - charlotte
       - Charlotte Metro Area
       - 2,636,883
       - 11 March 2020
       - 337
       - 226,718
       - 2,563
       - 91,600
       - Mecklenburg County, North Carolina
     * - 22
       - orlando
       - Orlando Metro Area
       - 2,608,147
       - 12 March 2020
       - 336
       - 191,795
       - 2,303
       - 108,208
       - Orange County, Florida
     * - 23
       - sanantonio
       - San Antonio Metro Area
       - 2,550,960
       - 12 February 2020
       - 365
       - 223,884
       - 3,395
       - 186,358
       - Bexar County, Texas
     * - 24
       - portland
       - Portland Metro Area
       - 2,492,412
       - 28 February 2020
       - 349
       - 87,773
       - 1,154
       - 31,021
       - Multnomah County, Oregon
     * - 25
       - sacramento
       - Sacramento Metro Area
       - 2,363,730
       - 21 February 2020
       - 356
       - 129,785
       - 1,840
       - 89,652
       - Sacramento County, California
     * - 26
       - pittsburgh
       - Pittsburgh Metro Area
       - 2,317,600
       - 13 March 2020
       - 335
       - 150,847
       - 3,552
       - 72,447
       - Allegheny County, Pennsylvania
     * - 27
       - lasvegas
       - Las Vegas Metro Area
       - 2,266,715
       - 05 March 2020
       - 343
       - 220,710
       - 3,577
       - 220,710
       - Clark County, Nevada
     * - 28
       - austin
       - Austin Metro Area
       - 2,227,083
       - 13 March 2020
       - 335
       - 143,464
       - 1,493
       - 73,259
       - Travis County, Texas
     * - 29
       - cincinnati
       - Cincinnati Metro Area
       - 2,221,208
       - 14 March 2020
       - 334
       - 193,043
       - 1,573
       - 70,320
       - Hamilton County, Ohio
     * - 30
       - kansascity
       - Kansas City Metro Area
       - 2,157,990
       - 07 March 2020
       - 341
       - 135,779
       - 1,690
       - 51,608
       - Johnson County, Kansas
     * - 31
       - columbus
       - Columbus Metro Area
       - 2,122,271
       - 14 March 2020
       - 334
       - 175,701
       - 1,318
       - 108,226
       - Franklin County, Ohio
     * - 32
       - indianapolis
       - Indianapolis Metro Area
       - 2,074,537
       - 06 March 2020
       - 342
       - 191,829
       - 3,576
       - 88,899
       - Marion County, Indiana
     * - 33
       - cleveland
       - Cleveland Metro Area
       - 2,048,449
       - 09 March 2020
       - 339
       - 148,980
       - 2,021
       - 91,924
       - Cuyahoga County, Ohio
     * - 34
       - nashville
       - Nashville Metro Area
       - 1,934,317
       - 05 March 2020
       - 343
       - 223,825
       - 2,409
       - 87,282
       - Davidson County, Tennessee
     * - 35
       - virginiabeach
       - Virginia Beach Metro Area
       - 1,768,901
       - 09 March 2020
       - 339
       - 108,220
       - 1,217
       - 28,401
       - Virginia Beach city, Virginia
     * - 36
       - providence
       - Providence Metro Area
       - 1,624,578
       - 14 March 2020
       - 334
       - 162,363
       - 3,632
       - 78,666
       - Providence County, Rhode Island
     * - 37
       - milwaukee
       - Milwaukee Metro Area
       - 1,575,179
       - 11 March 2020
       - 337
       - 172,743
       - 1,945
       - 105,286
       - Milwaukee County, Wisconsin
     * - 38
       - jacksonville
       - Jacksonville Metro Area
       - 1,559,514
       - 10 March 2020
       - 338
       - 131,433
       - 1,624
       - 85,430
       - Duval County, Florida
     * - 39
       - oklahomacity
       - Oklahoma City Metro Area
       - 1,408,950
       - 13 March 2020
       - 335
       - 138,156
       - 1,155
       - 78,215
       - Oklahoma County, Oklahoma
     * - 40
       - raleigh
       - Raleigh Metro Area
       - 1,390,785
       - 03 March 2020
       - 345
       - 96,115
       - 721
       - 74,185
       - Wake County, North Carolina
     * - 41
       - memphis
       - Memphis Metro Area
       - 1,346,045
       - 08 March 2020
       - 340
       - 129,187
       - 2,062
       - 85,594
       - Shelby County, Tennessee
     * - 42
       - richmond
       - Richmond Metro Area
       - 1,291,900
       - 12 March 2020
       - 336
       - 78,790
       - 1,018
       - 21,469
       - Chesterfield County, Virginia
     * - 43
       - neworleans
       - New Orleans Metro Area
       - 1,270,530
       - 09 March 2020
       - 339
       - 108,809
       - 2,361
       - 42,647
       - Jefferson Parish, Louisiana
     * - 44
       - louisville
       - Louisville/Jefferson County Metro Area
       - 1,265,108
       - 08 March 2020
       - 340
       - 114,944
       - 1,443
       - 71,126
       - Jefferson County, Kentucky
     * - 45
       - saltlakecity
       - Salt Lake City Metro Area
       - 1,232,696
       - 25 February 2020
       - 352
       - 140,588
       - 742
       - 134,381
       - Salt Lake County, Utah
     * - 46
       - hartford
       - Hartford Metro Area
       - 1,204,877
       - 14 March 2020
       - 334
       - 84,400
       - 2,694
       - 67,142
       - Hartford County, Connecticut
     * - 47
       - buffalo
       - Buffalo Metro Area
       - 1,127,983
       - 15 March 2020
       - 333
       - 75,293
       - 1,819
       - 60,736
       - Erie County, New York
     * - 48
       - birmingham
       - Birmingham Metro Area
       - 1,090,435
       - 13 March 2020
       - 335
       - 110,743
       - 1,920
       - 69,117
       - Jefferson County, Alabama
     * - 49
       - grandrapids
       - Grand Rapids Metro Area
       - 1,077,370
       - 12 March 2020
       - 336
       - 84,182
       - 1,190
       - 50,419
       - Kent County, Michigan
     * - 50
       - rochester
       - Rochester Metro Area
       - 1,069,644
       - 11 March 2020
       - 337
       - 66,408
       - 1,249
       - 50,081
       - Monroe County, New York

.. _png_figures:
	 
* The COVID-19 trends in cases and deaths for these 6 metropolitan areas as of 11 FEBRUARY 2021: SF Bay Area; Washington, DC; Richmond, VA; NYC; Los Angeles; and New Orleans.

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
  
* GIF'd video animations of the COVID-19 trends in cases/deaths for NYC, Chicago, Seattle, SF Bay Area, DC, and Richmond, as of 11 FEBRUARY 2021.	  

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

  And here is the animation for the continental United States as of 11 FEBRUARY 2021

  .. list-table::
     :widths: auto

     * - |anim_gif_conus|
     * - `Continental United States <https://tanimislam.github.io/covid19movies/covid19_conus_LATEST.mp4>`_

* GIF'd video animations of the COVID-19 trends in cases/deaths for California, Texas, Florida, and Virginia, as of 11 FEBRUARY 2021.

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

.. _`covid19_update_database`: https://tanimislam.github.io/covid19_stats/cli/covid19_update_database.html#covid19-update-database
