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
  
  .. list-table:: COVID-19 STATS FOR 50 METROS AS OF 14 NOVEMBER 2021
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
       - 623
       - 2,735,654
       - 66,949
       - 1,133,838
       - New York City, New York
     * - 2
       - losangeles
       - LA Metro Area
       - 18,711,436
       - 25 January 2020
       - 659
       - 2,694,027
       - 44,835
       - 1,512,028
       - Los Angeles County, California
     * - 3
       - chicago
       - Chicago Metro Area
       - 9,458,539
       - 24 January 2020
       - 660
       - 1,215,158
       - 19,643
       - 654,197
       - Cook County, Illinois
     * - 4
       - dallas
       - Dallas Metro Area
       - 7,573,136
       - 09 March 2020
       - 615
       - 1,168,486
       - 15,041
       - 409,318
       - Dallas County, Texas
     * - 5
       - houston
       - Houston Metro Area
       - 7,066,141
       - 04 March 2020
       - 620
       - 927,966
       - 13,613
       - 581,158
       - Harris County, Texas
     * - 6
       - bayarea
       - Bay Area
       - 6,860,207
       - 31 January 2020
       - 653
       - 525,507
       - 6,146
       - 149,251
       - Santa Clara County, California
     * - 7
       - dc
       - DC Metro Area
       - 6,280,487
       - 05 March 2020
       - 619
       - 584,973
       - 8,687
       - 100,867
       - Prince George's County, Maryland
     * - 8
       - miami
       - Miami Metro Area
       - 6,166,488
       - 06 March 2020
       - 618
       - 1,261,016
       - 18,065
       - 675,844
       - Miami-Dade County, Florida
     * - 9
       - philadelphia
       - Philadelphia Metro Area
       - 6,102,434
       - 06 March 2020
       - 618
       - 736,294
       - 14,404
       - 187,044
       - Philadelphia County, Pennsylvania
     * - 10
       - atlanta
       - Atlanta Metro Area
       - 6,020,364
       - 02 March 2020
       - 622
       - 853,545
       - 12,334
       - 134,435
       - Gwinnett County, Georgia
     * - 11
       - phoenix
       - Phoenix Metro Area
       - 4,948,203
       - 26 January 2020
       - 658
       - 844,732
       - 13,593
       - 767,759
       - Maricopa County, Arizona
     * - 12
       - boston
       - Boston Metro Area
       - 4,873,019
       - 01 February 2020
       - 652
       - 564,204
       - 12,277
       - 163,654
       - Middlesex County, Massachusetts
     * - 13
       - detroit
       - Detroit Metro Area
       - 4,319,629
       - 10 March 2020
       - 614
       - 554,681
       - 12,237
       - 209,592
       - Wayne County, Michigan
     * - 14
       - seattle
       - Seattle Metro Area
       - 3,979,845
       - 21 January 2020
       - 663
       - 333,316
       - 3,741
       - 168,884
       - King County, Washington
     * - 15
       - minneapolis
       - Minneapolis Metro Area
       - 3,640,043
       - 06 March 2020
       - 618
       - 516,439
       - 5,358
       - 165,628
       - Hennepin County, Minnesota
     * - 16
       - sandiego
       - San Diego Metro Area
       - 3,338,330
       - 10 February 2020
       - 643
       - 399,540
       - 4,280
       - 399,540
       - San Diego County, California
     * - 17
       - tampa
       - Tampa Metro Area
       - 3,194,831
       - 01 March 2020
       - 623
       - 486,546
       - 8,210
       - 243,294
       - Hillsborough County, Florida
     * - 18
       - denver
       - Denver Metro Area
       - 2,967,239
       - 05 March 2020
       - 619
       - 389,536
       - 4,292
       - 96,348
       - Denver County, Colorado
     * - 19
       - stlouis
       - St. Louis Metro Area
       - 2,803,228
       - 07 March 2020
       - 617
       - 400,690
       - 6,406
       - 132,329
       - St. Louis County, Missouri
     * - 20
       - baltimore
       - Baltimore Metro Area
       - 2,800,053
       - 08 March 2020
       - 616
       - 255,953
       - 5,020
       - 78,295
       - Baltimore County, Maryland
     * - 21
       - charlotte
       - Charlotte Metro Area
       - 2,636,883
       - 11 March 2020
       - 613
       - 415,894
       - 4,435
       - 159,425
       - Mecklenburg County, North Carolina
     * - 22
       - orlando
       - Orlando Metro Area
       - 2,608,147
       - 12 March 2020
       - 612
       - 418,891
       - 5,204
       - 229,270
       - Orange County, Florida
     * - 23
       - sanantonio
       - San Antonio Metro Area
       - 2,550,960
       - 12 February 2020
       - 641
       - 399,032
       - 6,697
       - 324,022
       - Bexar County, Texas
     * - 24
       - portland
       - Portland Metro Area
       - 2,492,412
       - 28 February 2020
       - 625
       - 188,626
       - 2,179
       - 58,525
       - Multnomah County, Oregon
     * - 25
       - sacramento
       - Sacramento Metro Area
       - 2,363,730
       - 21 February 2020
       - 632
       - 245,789
       - 3,238
       - 165,395
       - Sacramento County, California
     * - 26
       - pittsburgh
       - Pittsburgh Metro Area
       - 2,317,600
       - 13 March 2020
       - 611
       - 295,816
       - 5,441
       - 140,263
       - Allegheny County, Pennsylvania
     * - 27
       - lasvegas
       - Las Vegas Metro Area
       - 2,266,715
       - 05 March 2020
       - 619
       - 345,658
       - 6,049
       - 345,658
       - Clark County, Nevada
     * - 28
       - austin
       - Austin Metro Area
       - 2,227,083
       - 13 March 2020
       - 611
       - 254,786
       - 2,905
       - 120,940
       - Travis County, Texas
     * - 29
       - cincinnati
       - Cincinnati Metro Area
       - 2,221,208
       - 14 March 2020
       - 610
       - 316,348
       - 4,035
       - 109,052
       - Hamilton County, Ohio
     * - 30
       - kansascity
       - Kansas City Metro Area
       - 2,157,990
       - 07 March 2020
       - 617
       - 233,004
       - 2,996
       - 79,838
       - Johnson County, Kansas
     * - 31
       - columbus
       - Columbus Metro Area
       - 2,122,271
       - 14 March 2020
       - 610
       - 285,450
       - 3,094
       - 170,486
       - Franklin County, Ohio
     * - 32
       - indianapolis
       - Indianapolis Metro Area
       - 2,074,537
       - 06 March 2020
       - 618
       - 305,896
       - 4,870
       - 139,593
       - Marion County, Indiana
     * - 33
       - cleveland
       - Cleveland Metro Area
       - 2,048,449
       - 09 March 2020
       - 615
       - 255,992
       - 4,174
       - 155,077
       - Cuyahoga County, Ohio
     * - 34
       - nashville
       - Nashville Metro Area
       - 1,934,317
       - 05 March 2020
       - 619
       - 365,924
       - 3,664
       - 133,942
       - Davidson County, Tennessee
     * - 35
       - virginiabeach
       - Virginia Beach Metro Area
       - 1,768,901
       - 09 March 2020
       - 615
       - 198,274
       - 2,872
       - 50,437
       - Virginia Beach city, Virginia
     * - 36
       - providence
       - Providence Metro Area
       - 1,624,578
       - 14 March 2020
       - 610
       - 252,869
       - 4,772
       - 116,947
       - Providence County, Rhode Island
     * - 37
       - milwaukee
       - Milwaukee Metro Area
       - 1,575,179
       - 11 March 2020
       - 613
       - 257,810
       - 2,753
       - 155,325
       - Milwaukee County, Wisconsin
     * - 38
       - jacksonville
       - Jacksonville Metro Area
       - 1,559,514
       - 10 March 2020
       - 614
       - 261,014
       - 4,358
       - 165,019
       - Duval County, Florida
     * - 39
       - oklahomacity
       - Oklahoma City Metro Area
       - 1,408,950
       - 13 March 2020
       - 611
       - 215,561
       - 3,309
       - 120,888
       - Oklahoma County, Oklahoma
     * - 40
       - raleigh
       - Raleigh Metro Area
       - 1,390,785
       - 03 March 2020
       - 621
       - 176,095
       - 1,305
       - 133,111
       - Wake County, North Carolina
     * - 41
       - memphis
       - Memphis Metro Area
       - 1,346,045
       - 08 March 2020
       - 616
       - 220,769
       - 3,436
       - 147,417
       - Shelby County, Tennessee
     * - 42
       - richmond
       - Richmond Metro Area
       - 1,291,900
       - 12 March 2020
       - 612
       - 145,576
       - 2,412
       - 40,397
       - Chesterfield County, Virginia
     * - 43
       - neworleans
       - New Orleans Metro Area
       - 1,270,530
       - 09 March 2020
       - 615
       - 190,816
       - 3,411
       - 69,968
       - Jefferson Parish, Louisiana
     * - 44
       - louisville
       - Louisville/Jefferson County Metro Area
       - 1,265,108
       - 08 March 2020
       - 616
       - 199,520
       - 2,710
       - 122,722
       - Jefferson County, Kentucky
     * - 45
       - saltlakecity
       - Salt Lake City Metro Area
       - 1,232,696
       - 25 February 2020
       - 628
       - 215,275
       - 1,263
       - 202,568
       - Salt Lake County, Utah
     * - 46
       - hartford
       - Hartford Metro Area
       - 1,204,877
       - 14 March 2020
       - 610
       - 126,787
       - 3,195
       - 100,069
       - Hartford County, Connecticut
     * - 47
       - buffalo
       - Buffalo Metro Area
       - 1,127,983
       - 15 March 2020
       - 609
       - 141,559
       - 2,413
       - 115,291
       - Erie County, New York
     * - 48
       - birmingham
       - Birmingham Metro Area
       - 1,090,435
       - 13 March 2020
       - 611
       - 192,572
       - 3,161
       - 115,936
       - Jefferson County, Alabama
     * - 49
       - grandrapids
       - Grand Rapids Metro Area
       - 1,077,370
       - 12 March 2020
       - 612
       - 168,063
       - 1,807
       - 99,495
       - Kent County, Michigan
     * - 50
       - rochester
       - Rochester Metro Area
       - 1,069,644
       - 11 March 2020
       - 613
       - 124,482
       - 1,630
       - 91,267
       - Monroe County, New York

.. _png_figures:
	 
* The COVID-19 trends in cases and deaths for these 6 metropolitan areas as of 14 NOVEMBER 2021: SF Bay Area; Washington, DC; Richmond, VA; NYC; Los Angeles; and New Orleans.

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
  
* GIF'd video animations of the COVID-19 trends in cases/deaths for NYC, Chicago, Seattle, SF Bay Area, DC, and Richmond, as of 14 NOVEMBER 2021.	  

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

  And here is the animation for the continental United States as of 14 NOVEMBER 2021

  .. list-table::
     :widths: auto

     * - |anim_gif_conus|
     * - `Continental United States <https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_conus_LATEST.mp4>`_

* GIF'd video animations of the COVID-19 trends in cases/deaths for California, Texas, Florida, and Virginia, as of 14 NOVEMBER 2021.

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
