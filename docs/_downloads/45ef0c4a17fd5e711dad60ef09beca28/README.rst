Hello world! This is my COVID-19 tracker. This is not nearly as sophisticated as what's in `ncov2019.live`_, and described in `this New Yorker article`_.

I have made major changes in the functionality and implementation from the original commits, since commit `#78917`_ for instance.

* The API code has been refactored into the |engine_main| module, and is divided into three main submodules: |engine_core| provides the higher level API calls for processing the COVID-19 data; |engine_gis| provides the lower-level APIs to write out, read in, and process the raw GIS data provided mainly by the US Census Bureau; and |engine_viz| and |engine_viz2| do the visualization parts.

* The command line interfaces (CLI) back-ends live in ``covid19_stats.cli``. One of the command line interfaces, `covid19_update_database`_, updates the git submodule (the `NY Times COVID-19 repository`_) with the *latest* data. Previously, one updated the database by manually running, from the repository's top level directory,

  .. code-block:: console

     git -C covid19_stats/covid-19-data pull origin master
  
* The ``testing`` subdirectory contains `Jupyter Notebooks`_ that illuminate bits and pieces of this COVID-19 tracker's functionality. It also consists of `Jupyter Notebooks <https://jupyter.org>`_ that create output for the API documentation.

  * ``testing/covid19_excuse_gis_visualizations.ipynb`` shows output for the |engine_gis| module documentation.
  * ``testing/covid19_excuse_core_visualizations.ipynb`` shows output for the |engine_core| module documentation.
  * ``testing/covid19_excuse_main_visualizations.ipynb`` shows output for the |engine_top| module documentation, and specifically the `COVID19Database <https://tanimislam.github.io/covid19_stats/api/api.html#covid19_stats.COVID19Database>`_ object.
  * ``testing/covid19_excuse_viz_visualizations.ipynb`` shows output for the |engine_viz| module documentation.
  * ``testing/covid19_excuse_viz2_visualizations.ipynb`` shows output for the |engine_viz2| module documentation.
  

Here is some output from using this COVID-19 tracker. The data lives underneath https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies.

* The summary of COVID-19 statistics for the top 50 MSAs by estimated 2019 population.
  
  .. list-table:: COVID-19 STATS FOR 50 METROS AS OF 17 OCTOBER 2021
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
       - 595
       - 2,663,499
       - 66,313
       - 1,105,853
       - New York City, New York
     * - 2
       - losangeles
       - LA Metro Area
       - 18,711,436
       - 25 January 2020
       - 631
       - 2,627,314
       - 43,754
       - 1,478,390
       - Los Angeles County, California
     * - 3
       - chicago
       - Chicago Metro Area
       - 9,458,539
       - 24 January 2020
       - 632
       - 1,167,020
       - 19,212
       - 631,261
       - Cook County, Illinois
     * - 4
       - dallas
       - Dallas Metro Area
       - 7,573,136
       - 09 March 2020
       - 587
       - 1,134,617
       - 14,090
       - 398,928
       - Dallas County, Texas
     * - 5
       - houston
       - Houston Metro Area
       - 7,066,141
       - 04 March 2020
       - 592
       - 908,898
       - 12,837
       - 569,900
       - Harris County, Texas
     * - 6
       - bayarea
       - Bay Area
       - 6,860,207
       - 31 January 2020
       - 625
       - 509,285
       - 6,146
       - 144,518
       - Santa Clara County, California
     * - 7
       - dc
       - DC Metro Area
       - 6,280,487
       - 05 March 2020
       - 591
       - 565,187
       - 8,472
       - 98,827
       - Prince George's County, Maryland
     * - 8
       - miami
       - Miami Metro Area
       - 6,166,488
       - 06 March 2020
       - 590
       - 1,245,238
       - 17,266
       - 667,933
       - Miami-Dade County, Florida
     * - 9
       - philadelphia
       - Philadelphia Metro Area
       - 6,102,434
       - 06 March 2020
       - 590
       - 700,193
       - 13,989
       - 179,451
       - Philadelphia County, Pennsylvania
     * - 10
       - atlanta
       - Atlanta Metro Area
       - 6,020,364
       - 02 March 2020
       - 594
       - 835,304
       - 11,494
       - 131,712
       - Gwinnett County, Georgia
     * - 11
       - phoenix
       - Phoenix Metro Area
       - 4,948,203
       - 26 January 2020
       - 630
       - 790,215
       - 12,878
       - 718,831
       - Maricopa County, Arizona
     * - 12
       - boston
       - Boston Metro Area
       - 4,873,019
       - 01 February 2020
       - 624
       - 537,903
       - 12,077
       - 156,101
       - Middlesex County, Massachusetts
     * - 13
       - detroit
       - Detroit Metro Area
       - 4,319,629
       - 10 March 2020
       - 586
       - 509,721
       - 11,772
       - 193,985
       - Wayne County, Michigan
     * - 14
       - seattle
       - Seattle Metro Area
       - 3,979,845
       - 21 January 2020
       - 635
       - 309,363
       - 3,521
       - 158,595
       - King County, Washington
     * - 15
       - minneapolis
       - Minneapolis Metro Area
       - 3,640,043
       - 06 March 2020
       - 590
       - 467,331
       - 5,090
       - 151,329
       - Hennepin County, Minnesota
     * - 16
       - sandiego
       - San Diego Metro Area
       - 3,338,330
       - 10 February 2020
       - 615
       - 379,944
       - 4,151
       - 379,944
       - San Diego County, California
     * - 17
       - tampa
       - Tampa Metro Area
       - 3,194,831
       - 01 March 2020
       - 595
       - 479,674
       - 7,758
       - 239,223
       - Hillsborough County, Florida
     * - 18
       - denver
       - Denver Metro Area
       - 2,967,239
       - 05 March 2020
       - 591
       - 355,435
       - 4,031
       - 88,868
       - Denver County, Colorado
     * - 19
       - stlouis
       - St. Louis Metro Area
       - 2,803,228
       - 07 March 2020
       - 589
       - 387,066
       - 6,190
       - 127,979
       - St. Louis County, Missouri
     * - 20
       - baltimore
       - Baltimore Metro Area
       - 2,800,053
       - 08 March 2020
       - 588
       - 246,633
       - 4,878
       - 75,686
       - Baltimore County, Maryland
     * - 21
       - charlotte
       - Charlotte Metro Area
       - 2,636,883
       - 11 March 2020
       - 585
       - 402,612
       - 4,214
       - 154,718
       - Mecklenburg County, North Carolina
     * - 22
       - orlando
       - Orlando Metro Area
       - 2,608,147
       - 12 March 2020
       - 584
       - 412,667
       - 4,862
       - 226,228
       - Orange County, Florida
     * - 23
       - sanantonio
       - San Antonio Metro Area
       - 2,550,960
       - 12 February 2020
       - 613
       - 389,926
       - 6,381
       - 316,907
       - Bexar County, Texas
     * - 24
       - portland
       - Portland Metro Area
       - 2,492,412
       - 28 February 2020
       - 597
       - 174,583
       - 1,926
       - 54,797
       - Multnomah County, Oregon
     * - 25
       - sacramento
       - Sacramento Metro Area
       - 2,363,730
       - 21 February 2020
       - 604
       - 233,629
       - 3,090
       - 157,620
       - Sacramento County, California
     * - 26
       - pittsburgh
       - Pittsburgh Metro Area
       - 2,317,600
       - 13 March 2020
       - 583
       - 266,732
       - 5,011
       - 127,653
       - Allegheny County, Pennsylvania
     * - 27
       - lasvegas
       - Las Vegas Metro Area
       - 2,266,715
       - 05 March 2020
       - 591
       - 334,318
       - 5,835
       - 334,318
       - Clark County, Nevada
     * - 28
       - austin
       - Austin Metro Area
       - 2,227,083
       - 13 March 2020
       - 583
       - 248,179
       - 2,770
       - 118,150
       - Travis County, Texas
     * - 29
       - cincinnati
       - Cincinnati Metro Area
       - 2,221,208
       - 14 March 2020
       - 582
       - 300,619
       - 3,705
       - 104,360
       - Hamilton County, Ohio
     * - 30
       - kansascity
       - Kansas City Metro Area
       - 2,157,990
       - 07 March 2020
       - 589
       - 224,082
       - 2,847
       - 76,717
       - Johnson County, Kansas
     * - 31
       - columbus
       - Columbus Metro Area
       - 2,122,271
       - 14 March 2020
       - 582
       - 270,375
       - 2,816
       - 162,448
       - Franklin County, Ohio
     * - 32
       - indianapolis
       - Indianapolis Metro Area
       - 2,074,537
       - 06 March 2020
       - 590
       - 292,923
       - 4,665
       - 134,544
       - Marion County, Indiana
     * - 33
       - cleveland
       - Cleveland Metro Area
       - 2,048,449
       - 09 March 2020
       - 587
       - 236,725
       - 3,877
       - 144,542
       - Cuyahoga County, Ohio
     * - 34
       - nashville
       - Nashville Metro Area
       - 1,934,317
       - 05 March 2020
       - 591
       - 357,716
       - 3,482
       - 131,065
       - Davidson County, Tennessee
     * - 35
       - virginiabeach
       - Virginia Beach Metro Area
       - 1,768,901
       - 09 March 2020
       - 587
       - 191,628
       - 2,711
       - 48,959
       - Virginia Beach city, Virginia
     * - 36
       - providence
       - Providence Metro Area
       - 1,624,578
       - 14 March 2020
       - 582
       - 242,734
       - 4,701
       - 112,799
       - Providence County, Rhode Island
     * - 37
       - milwaukee
       - Milwaukee Metro Area
       - 1,575,179
       - 11 March 2020
       - 585
       - 244,347
       - 2,633
       - 148,777
       - Milwaukee County, Wisconsin
     * - 38
       - jacksonville
       - Jacksonville Metro Area
       - 1,559,514
       - 10 March 2020
       - 586
       - 258,483
       - 4,159
       - 163,590
       - Duval County, Florida
     * - 39
       - oklahomacity
       - Oklahoma City Metro Area
       - 1,408,950
       - 13 March 2020
       - 583
       - 208,268
       - 2,801
       - 117,180
       - Oklahoma County, Oklahoma
     * - 40
       - raleigh
       - Raleigh Metro Area
       - 1,390,785
       - 03 March 2020
       - 593
       - 169,958
       - 1,257
       - 128,440
       - Wake County, North Carolina
     * - 41
       - memphis
       - Memphis Metro Area
       - 1,346,045
       - 08 March 2020
       - 588
       - 216,240
       - 3,264
       - 144,705
       - Shelby County, Tennessee
     * - 42
       - richmond
       - Richmond Metro Area
       - 1,291,900
       - 12 March 2020
       - 584
       - 139,657
       - 2,291
       - 38,728
       - Chesterfield County, Virginia
     * - 43
       - neworleans
       - New Orleans Metro Area
       - 1,270,530
       - 09 March 2020
       - 587
       - 187,948
       - 3,342
       - 69,122
       - Jefferson Parish, Louisiana
     * - 44
       - louisville
       - Louisville/Jefferson County Metro Area
       - 1,265,108
       - 08 March 2020
       - 588
       - 190,646
       - 2,548
       - 117,371
       - Jefferson County, Kentucky
     * - 45
       - saltlakecity
       - Salt Lake City Metro Area
       - 1,232,696
       - 25 February 2020
       - 600
       - 200,223
       - 1,184
       - 188,954
       - Salt Lake County, Utah
     * - 46
       - hartford
       - Hartford Metro Area
       - 1,204,877
       - 14 March 2020
       - 582
       - 122,977
       - 3,165
       - 97,087
       - Hartford County, Connecticut
     * - 47
       - buffalo
       - Buffalo Metro Area
       - 1,127,983
       - 15 March 2020
       - 581
       - 129,272
       - 2,335
       - 105,477
       - Erie County, New York
     * - 48
       - birmingham
       - Birmingham Metro Area
       - 1,090,435
       - 13 March 2020
       - 583
       - 188,192
       - 3,008
       - 114,056
       - Jefferson County, Alabama
     * - 49
       - grandrapids
       - Grand Rapids Metro Area
       - 1,077,370
       - 12 March 2020
       - 584
       - 151,694
       - 1,674
       - 90,019
       - Kent County, Michigan
     * - 50
       - rochester
       - Rochester Metro Area
       - 1,069,644
       - 11 March 2020
       - 585
       - 112,299
       - 1,559
       - 83,520
       - Monroe County, New York

.. _png_figures:
	 
* The COVID-19 trends in cases and deaths for these 6 metropolitan areas as of 17 OCTOBER 2021: SF Bay Area; Washington, DC; Richmond, VA; NYC; Los Angeles; and New Orleans.

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
  
* GIF'd video animations of the COVID-19 trends in cases/deaths for NYC, Chicago, Seattle, SF Bay Area, DC, and Richmond, as of 17 OCTOBER 2021.	  

  .. list-table::
     :widths: auto

     * - |anim_gif_nyc|
       - |anim_gif_chicago|
       - |anim_gif_seattle|
     * - `NYC Metro <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_nyc_LATEST.mp4>`_
       - `Chicago <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_chicago_LATEST.mp4>`_
       - `Seattle <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_seattle_LATEST.mp4>`_
     * - |anim_gif_bayarea|
       - |anim_gif_dc|
       - |anim_gif_richmond|
     * - `SF Bay Area <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_bayarea_LATEST.mp4>`_
       - `Washington, DC <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_dc_LATEST.mp4>`_
       - `Richmond, VA <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_richmond_LATEST.mp4>`_
     * - |anim_gif_sacramento|
       - |anim_gif_houston|
       - |anim_gif_dallas|
     * - `Sacramento, CA <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_sacramento_LATEST.mp4>`_
       - `Houston, TX <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_houston_LATEST.mp4>`_
       - `Dallas, TX <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_dallas_LATEST.mp4>`_

  And here is the animation for the continental United States as of 17 OCTOBER 2021

  .. list-table::
     :widths: auto

     * - |anim_gif_conus|
     * - `Continental United States <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_conus_LATEST.mp4>`_

* GIF'd video animations of the COVID-19 trends in cases/deaths for California, Texas, Florida, and Virginia, as of 17 OCTOBER 2021.

  .. list-table::
     :widths: auto

     * - |anim_gif_california|
       - |anim_gif_texas|
     * - `California <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_california_LATEST.mp4>`_
       - `Texas <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_texas_LATEST.mp4>`_
     * - |anim_gif_florida|
       - |anim_gif_virginia|
     * - `Florida <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_florida_LATEST.mp4>`_
       - `Virginia <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_virginia_LATEST.mp4>`_

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
.. _`COVID-19 Stats GitHub Page`: https://tanimislam.sfo3.digitaloceanspaces.com/covid19_stats


.. STATIC IMAGES

.. |cds_bayarea| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_bayarea_cds_LATEST.png
   :width: 100%
   :align: middle

.. |cds_dc| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_dc_cds_LATEST.png
   :width: 100%
   :align: middle

.. |cds_richmond| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_richmond_cds_LATEST.png
   :width: 100%
   :align: middle

.. |cds_nyc| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_nyc_cds_LATEST.png
   :width: 100%
   :align: middle

.. |cds_losangeles| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_losangeles_cds_LATEST.png
   :width: 100%
   :align: middle

.. |cds_neworleans| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_neworleans_cds_LATEST.png
   :width: 100%
   :align: middle
	   
.. GIF ANIMATIONS MSA

.. |anim_gif_nyc| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_nyc_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_chicago| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_chicago_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_seattle| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_seattle_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_bayarea| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_bayarea_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_dc| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_dc_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_richmond| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_richmond_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_sacramento| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_sacramento_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_houston| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_houston_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_dallas| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_dallas_LATEST.gif
   :width: 100%
   :align: middle

	   
.. GIF ANIMATIONS CONUS

.. |anim_gif_conus| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_conus_LATEST.gif
   :width: 100%
   :align: middle

.. GIF ANIMATIONS STATE

.. |anim_gif_california| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_california_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_texas| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_texas_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_florida| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_florida_LATEST.gif
   :width: 100%
   :align: middle

.. |anim_gif_virginia| image:: https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_virginia_LATEST.gif
   :width: 100%
   :align: middle

.. _`covid19_update_database`: https://tanimislam.github.io/covid19_stats/cli/covid19_update_database.html

.. |engine_gis|  replace:: `covid19_stats.engine.gis`_
.. |engine_main| replace:: `covid19_stats.engine`_
.. |engine_core| replace:: `covid19_stats.engine.core`_
.. |engine_viz|  replace:: `covid19_stats.engine.viz`_
.. |engine_viz2|  replace:: `covid19_stats.engine.viz2`_
.. |engine_top|  replace:: `covid19_stats`_
.. _`covid19_stats.engine.gis`: https://tanimislam.github.io/covid19_stats/api/covid19_stats_engine_gis_api.html
.. _`covid19_stats.engine`: https://tanimislam.github.io/covid19_stats/api/covid19_stats_engine_api.html 
.. _`covid19_stats.engine.core`: https://tanimislam.github.io/covid19_stats/api/covid19_stats_engine_core_api.html
.. _`covid19_stats.engine.viz`: https://tanimislam.github.io/covid19_stats/api/covid19_stats_engine_viz_api.html
.. _`covid19_stats.engine.viz2`: https://tanimislam.github.io/covid19_stats/api/covid19_stats_engine_viz2_api.html
.. _`covid19_stats`: https://tanimislam.github.io/covid19_stats/api/covid19_stats_api.html
