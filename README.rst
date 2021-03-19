Hello world! This is my COVID-19 tracker. This is not nearly as sophisticated as what’s in `ncov2019.live`_, and described in `this New Yorker article`_.

I have made major changes in the functionality and implementation from the original commits, since commit `#78917`_ for instance.

* The API code has been refactored into the |engine_main| module, and is divided into three main submodules: |engine_core| provides the higher level API calls for processing the COVID-19 data; |engine_gis| provides the lower-level APIs to write out, read in, and process the raw GIS data provided mainly by the US Census Bureau; and |engine_viz| does the visualization part.

* The command line interfaces (CLI) back-ends live in ``covid19_stats.cli``. One of the command line interfaces, `covid19_update_database`_, updates the git submodule (the `NY Times COVID-19 repository`_) with the *latest* data. Previously, one updated the database by manually running, from the repository's top level directory,

  .. code-block:: console

     git -C covid19_stats/covid-19-data pull origin master
  
* The ``testing`` subdirectory contains `Jupyter Notebooks`_ that illuminate bits and pieces of this COVID-19 tracker’s functionality. It also consists of `Jupyter Notebooks <https://jupyter.org>`_ that create output for the API documentation.

  * ``testing/covid19_excuse_gis_visualizations.ipynb`` shows output for the |engine_gis| module documentation.
  * ``testing/covid19_excuse_core_visualizations.ipynb`` shows output for the |engine_core| module documentation.
  * ``testing/covid19_excuse_main_visualizations.ipynb`` shows output for the |engine_top| module documentation, and specifically the `COVID19Database <https://tanimislam.github.io/covid19_stats/api/api.html#covid19_stats.COVID19Database>`_ object.

Here is some output from using this COVID-19 tracker. The data lives underneath `https://tanimislam.github.io/covid19movies <https://tanimislam.github.io/covid19movies>`_

* The summary of COVID-19 statistics for the top 50 MSAs by estimated 2019 population.
  
  .. list-table:: COVID-19 STATS FOR 50 METROS AS OF 18 MARCH 2021
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
       - 382
       - 1,941,561
       - 58,713
       - 790,069
       - New York City, New York
     * - 2
       - losangeles
       - LA Metro Area
       - 18,711,436
       - 25 January 2020
       - 418
       - 2,138,664
       - 36,272
       - 1,213,242
       - Los Angeles County, California
     * - 3
       - chicago
       - Chicago Metro Area
       - 9,458,539
       - 24 January 2020
       - 419
       - 883,286
       - 16,433
       - 485,771
       - Cook County, Illinois
     * - 4
       - dallas
       - Dallas Metro Area
       - 7,573,136
       - 09 March 2020
       - 374
       - 786,772
       - 9,828
       - 287,641
       - Dallas County, Texas
     * - 5
       - houston
       - Houston Metro Area
       - 7,066,141
       - 04 March 2020
       - 379
       - 565,822
       - 7,766
       - 368,213
       - Harris County, Texas
     * - 6
       - bayarea
       - Bay Area
       - 6,860,207
       - 31 January 2020
       - 412
       - 363,137
       - 5,344
       - 113,173
       - Santa Clara County, California
     * - 7
       - dc
       - DC Metro Area
       - 6,280,487
       - 05 March 2020
       - 378
       - 416,254
       - 7,063
       - 75,876
       - Prince George's County, Maryland
     * - 8
       - miami
       - Miami Metro Area
       - 6,166,488
       - 06 March 2020
       - 377
       - 764,235
       - 10,876
       - 430,941
       - Miami-Dade County, Florida
     * - 9
       - philadelphia
       - Philadelphia Metro Area
       - 6,102,434
       - 06 March 2020
       - 377
       - 476,384
       - 11,655
       - 123,959
       - Philadelphia County, Pennsylvania
     * - 10
       - atlanta
       - Atlanta Metro Area
       - 6,020,364
       - 02 March 2020
       - 381
       - 554,207
       - 7,807
       - 95,278
       - Gwinnett County, Georgia
     * - 11
       - phoenix
       - Phoenix Metro Area
       - 4,948,203
       - 26 January 2020
       - 417
       - 569,314
       - 10,309
       - 521,251
       - Maricopa County, Arizona
     * - 12
       - boston
       - Boston Metro Area
       - 4,873,019
       - 01 February 2020
       - 411
       - 402,267
       - 10,875
       - 117,031
       - Middlesex County, Massachusetts
     * - 13
       - detroit
       - Detroit Metro Area
       - 4,319,629
       - 10 March 2020
       - 373
       - 278,369
       - 8,794
       - 108,045
       - Wayne County, Michigan
     * - 14
       - seattle
       - Seattle Metro Area
       - 3,979,845
       - 21 January 2020
       - 422
       - 159,546
       - 2,596
       - 87,140
       - King County, Washington
     * - 15
       - minneapolis
       - Minneapolis Metro Area
       - 3,640,043
       - 06 March 2020
       - 377
       - 312,851
       - 4,150
       - 104,017
       - Hennepin County, Minnesota
     * - 16
       - sandiego
       - San Diego Metro Area
       - 3,338,330
       - 10 February 2020
       - 402
       - 266,819
       - 3,478
       - 266,819
       - San Diego County, California
     * - 17
       - tampa
       - Tampa Metro Area
       - 3,194,831
       - 01 March 2020
       - 382
       - 233,676
       - 4,209
       - 117,040
       - Hillsborough County, Florida
     * - 18
       - denver
       - Denver Metro Area
       - 2,967,239
       - 05 March 2020
       - 378
       - 233,024
       - 3,187
       - 62,090
       - Denver County, Colorado
     * - 19
       - stlouis
       - St. Louis Metro Area
       - 2,803,228
       - 07 March 2020
       - 376
       - 270,598
       - 4,914
       - 90,956
       - St. Louis County, Missouri
     * - 20
       - baltimore
       - Baltimore Metro Area
       - 2,800,053
       - 08 March 2020
       - 375
       - 173,232
       - 3,531
       - 53,317
       - Baltimore County, Maryland
     * - 21
       - charlotte
       - Charlotte Metro Area
       - 2,636,883
       - 11 March 2020
       - 372
       - 250,486
       - 2,931
       - 99,894
       - Mecklenburg County, North Carolina
     * - 22
       - orlando
       - Orlando Metro Area
       - 2,608,147
       - 12 March 2020
       - 371
       - 212,128
       - 2,670
       - 119,223
       - Orange County, Florida
     * - 23
       - sanantonio
       - San Antonio Metro Area
       - 2,550,960
       - 12 February 2020
       - 400
       - 243,331
       - 4,078
       - 201,285
       - Bexar County, Texas
     * - 24
       - portland
       - Portland Metro Area
       - 2,492,412
       - 28 February 2020
       - 384
       - 93,171
       - 1,318
       - 32,564
       - Multnomah County, Oregon
     * - 25
       - sacramento
       - Sacramento Metro Area
       - 2,363,730
       - 21 February 2020
       - 391
       - 138,717
       - 2,106
       - 95,836
       - Sacramento County, California
     * - 26
       - pittsburgh
       - Pittsburgh Metro Area
       - 2,317,600
       - 13 March 2020
       - 370
       - 166,380
       - 3,870
       - 80,941
       - Allegheny County, Pennsylvania
     * - 27
       - lasvegas
       - Las Vegas Metro Area
       - 2,266,715
       - 05 March 2020
       - 378
       - 232,174
       - 4,039
       - 232,174
       - Clark County, Nevada
     * - 28
       - austin
       - Austin Metro Area
       - 2,227,083
       - 13 March 2020
       - 370
       - 152,854
       - 1,769
       - 77,916
       - Travis County, Texas
     * - 29
       - cincinnati
       - Cincinnati Metro Area
       - 2,221,208
       - 14 March 2020
       - 369
       - 207,869
       - 2,670
       - 75,093
       - Hamilton County, Ohio
     * - 30
       - kansascity
       - Kansas City Metro Area
       - 2,157,990
       - 07 March 2020
       - 376
       - 153,803
       - 1,910
       - 55,457
       - Johnson County, Kansas
     * - 31
       - columbus
       - Columbus Metro Area
       - 2,122,271
       - 14 March 2020
       - 369
       - 187,213
       - 2,155
       - 115,083
       - Franklin County, Ohio
     * - 32
       - indianapolis
       - Indianapolis Metro Area
       - 2,074,537
       - 06 March 2020
       - 377
       - 200,356
       - 3,800
       - 92,429
       - Marion County, Indiana
     * - 33
       - cleveland
       - Cleveland Metro Area
       - 2,048,449
       - 09 March 2020
       - 374
       - 160,835
       - 3,098
       - 99,155
       - Cuyahoga County, Ohio
     * - 34
       - nashville
       - Nashville Metro Area
       - 1,934,317
       - 05 March 2020
       - 378
       - 239,830
       - 2,627
       - 92,545
       - Davidson County, Tennessee
     * - 35
       - virginiabeach
       - Virginia Beach Metro Area
       - 1,768,901
       - 09 March 2020
       - 374
       - 122,803
       - 1,916
       - 32,116
       - Virginia Beach city, Virginia
     * - 36
       - providence
       - Providence Metro Area
       - 1,624,578
       - 14 March 2020
       - 369
       - 178,196
       - 4,143
       - 86,088
       - Providence County, Rhode Island
     * - 37
       - milwaukee
       - Milwaukee Metro Area
       - 1,575,179
       - 11 March 2020
       - 372
       - 178,796
       - 2,061
       - 108,590
       - Milwaukee County, Wisconsin
     * - 38
       - jacksonville
       - Jacksonville Metro Area
       - 1,559,514
       - 10 March 2020
       - 373
       - 140,042
       - 1,958
       - 91,085
       - Duval County, Florida
     * - 39
       - oklahomacity
       - Oklahoma City Metro Area
       - 1,408,950
       - 13 March 2020
       - 370
       - 146,256
       - 1,429
       - 82,710
       - Oklahoma County, Oklahoma
     * - 40
       - raleigh
       - Raleigh Metro Area
       - 1,390,785
       - 03 March 2020
       - 380
       - 107,020
       - 835
       - 82,420
       - Wake County, North Carolina
     * - 41
       - memphis
       - Memphis Metro Area
       - 1,346,045
       - 08 March 2020
       - 375
       - 135,993
       - 2,258
       - 89,919
       - Shelby County, Tennessee
     * - 42
       - richmond
       - Richmond Metro Area
       - 1,291,900
       - 12 March 2020
       - 371
       - 89,414
       - 1,713
       - 24,659
       - Chesterfield County, Virginia
     * - 43
       - neworleans
       - New Orleans Metro Area
       - 1,270,530
       - 09 March 2020
       - 374
       - 115,413
       - 2,505
       - 44,664
       - Jefferson Parish, Louisiana
     * - 44
       - louisville
       - Louisville/Jefferson County Metro Area
       - 1,265,108
       - 08 March 2020
       - 375
       - 123,390
       - 1,675
       - 76,402
       - Jefferson County, Kentucky
     * - 45
       - saltlakecity
       - Salt Lake City Metro Area
       - 1,232,696
       - 25 February 2020
       - 387
       - 148,609
       - 839
       - 141,849
       - Salt Lake County, Utah
     * - 46
       - hartford
       - Hartford Metro Area
       - 1,204,877
       - 14 March 2020
       - 369
       - 92,149
       - 2,853
       - 72,873
       - Hartford County, Connecticut
     * - 47
       - buffalo
       - Buffalo Metro Area
       - 1,127,983
       - 15 March 2020
       - 368
       - 85,180
       - 1,957
       - 69,273
       - Erie County, New York
     * - 48
       - birmingham
       - Birmingham Metro Area
       - 1,090,435
       - 13 March 2020
       - 370
       - 118,715
       - 2,183
       - 73,832
       - Jefferson County, Alabama
     * - 49
       - grandrapids
       - Grand Rapids Metro Area
       - 1,077,370
       - 12 March 2020
       - 371
       - 89,838
       - 1,259
       - 53,591
       - Kent County, Michigan
     * - 50
       - rochester
       - Rochester Metro Area
       - 1,069,644
       - 11 March 2020
       - 372
       - 72,660
       - 1,330
       - 54,672
       - Monroe County, New York

.. _png_figures:
	 
* The COVID-19 trends in cases and deaths for these 6 metropolitan areas as of 18 MARCH 2021: SF Bay Area; Washington, DC; Richmond, VA; NYC; Los Angeles; and New Orleans.

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
  
* GIF'd video animations of the COVID-19 trends in cases/deaths for NYC, Chicago, Seattle, SF Bay Area, DC, and Richmond, as of 18 MARCH 2021.	  

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
     * - |anim_gif_sacramento|
       - |anim_gif_houston|
       - |anim_gif_dallas|
     * - `Sacramento, CA <https://tanimislam.github.io/covid19movies/covid19_sacramento_LATEST.mp4>`_
       - `Houston, TX <https://tanimislam.github.io/covid19movies/covid19_houston_LATEST.mp4>`_
       - `Dallas, TX <https://tanimislam.github.io/covid19movies/covid19_dallas_LATEST.mp4>`_

  And here is the animation for the continental United States as of 18 MARCH 2021

  .. list-table::
     :widths: auto

     * - |anim_gif_conus|
     * - `Continental United States <https://tanimislam.github.io/covid19movies/covid19_conus_LATEST.mp4>`_

* GIF'd video animations of the COVID-19 trends in cases/deaths for California, Texas, Florida, and Virginia, as of 18 MARCH 2021.

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

.. |anim_gif_sacramento| image:: https://tanimislam.github.io/covid19movies/covid19_sacramento_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_houston| image:: https://tanimislam.github.io/covid19movies/covid19_houston_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_dallas| image:: https://tanimislam.github.io/covid19movies/covid19_dallas_LATEST.gif
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

.. |engine_gis|  replace:: `covid19_stats.engine.gis`_
.. |engine_main| replace:: `covid19_stats.engine`_
.. |engine_core| replace:: `covid19_stats.engine.core`_
.. |engine_viz|  replace:: `covid19_stats.engine.viz`_
.. |engine_top|  replace:: `covid19_stats`_
.. _`covid19_stats.engine.gis`: https://tanimislam.github.io/covid19_stats/api/api.html#covid19-stats-engine-gis-module
.. _`covid19_stats.engine`: https://tanimislam.github.io/covid19_stats/api/api.html#covid19-stats-engine-module
.. _`covid19_stats.engine.core`: https://tanimislam.github.io/covid19_stats/api/api.html#covid19-stats-engine-core-module
.. _`covid19_stats.engine.viz`: https://tanimislam.github.io/covid19_stats/api/api.html#covid19-stats-engine-viz-module
.. _`covid19_stats`: https://tanimislam.github.io/covid19_stats/api/api.html#covid19-stats-module
