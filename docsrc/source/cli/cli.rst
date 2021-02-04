.. _using_the_cli:

USING THE CLI
==================
There are *six* command line interfaces that have been defined here.

covid19_update_database
------------------------
This CLI updates the git submodule (the `NY Times COVID-19 repository`_) with the *latest* data. Previously, one updated the database by manually running, from the repository's top level directory,

  .. code-block:: console

     git -C covid19_stats/covid-19-data pull origin master

covid19_create_movie_or_summary
--------------------------------
``covid19_create_movie_or_summary`` is the *main* top-level CLI currently in the repository. Its purpose is to *individually* create COVID-19 summary movies and figures, of cumulative cases and deaths, in the `Contiguous United States (CONUS) <CONUS_>`_ or one of the 380 defined metropolitan statistical areas (MSA).

It has four modes of operation. Its help output, while running ``covid19_create_movie_or_summary -h``, produces the following,

.. code:: console

   usage: covid19_create_movie_or_summary [-h] [-d DIRNAME] [--info] {M,m,s,mcd} ...

   positional arguments:
     {M,m,s,mcd}           Choose one of three options: (M) summarizes stats from metros; (m) make a movie of a metro region; and
			   (s) dumps summary plots of last incident date, and cumulative covid-19 stats, of a metro region.
       M                   If chosen, then list all the metropolitan areas through which we can look.
       m                   Make a movie of the COVID-19 cases and deaths trend for the specific Metropolitan Statistical Area
			   (MSA).
       s                   Make a summary plot, and incident data file, of COVID-19 cases and deaths trend, for the specific
			   Metropolitan Statistical Area (MSA).
       mcd                 Make a large-sized movie of either "CASES" or "DEATHS" for given MSA or CONUS.

   optional arguments:
     -h, --help            show this help message and exit
     -d DIRNAME, --dirname DIRNAME
			   The directory into which to store the resulting files. Default is /usr/WS2/islam5/covid19_data/nyc.
     --info                If chosen, then print out INFO level logging statements.

The default flags in the top level operation are,

* ``-h`` shows this help screen.
* ``-d`` or ``--dirname`` specifies the output directory. Default is the current working directory.
* ``--info`` says to show ``INFO`` logging output.
     
.. _metro_mode:
     
summarize MSAs
^^^^^^^^^^^^^^^^
``covid19_create_movie_or_summary M`` (METRO flag) lists the COVID-19 stats for all, or user-selected, MSAs by population. For example, here are the statistics for the top 30 MSAs.

.. code-block:: console

   covid19_create_movie_or_summary M

   HERE ARE THE 380 METRO AREAS, ORDERED BY POPULATION
   DATA AS OF 15 June 2020.
   RANK  IDENTIFIER        NAME                                    POPULATION    FIRST INC.          NUM DAYS  NUM CASES    NUM DEATHS    MAX CASE COUNTY    MAX CASE COUNTY NAME
 ------  ----------------  --------------------------------------  ------------  ----------------  ----------  -----------  ------------  -----------------  ------------------------------------
      1  nyc               NYC Metro Area                          19,216,182    01 March 2020            106  483,453      39,029        215,011            New York City, New York
      2  losangeles        LA Metro Area                           18,711,436    25 January 2020          142  102,983      3,801         73,791             Los Angeles County, California
      3  chicago           Chicago Metro Area                      9,458,539     24 January 2020          143  125,857      6,001         85,184             Cook County, Illinois
      4  dallas            Dallas Metro Area                       7,573,136     09 March 2020             98  27,201       606           14,537             Dallas County, Texas
      5  houston           Houston Metro Area                      7,066,141     04 March 2020            103  23,848       427           17,282             Harris County, Texas
      6  bayarea           Bay Area                                6,860,207     31 January 2020          136  16,178       474           4,394              Alameda County, California
      7  dc                DC Metro Area                           6,280,487     05 March 2020            102  78,449       2,933         17,920             Prince George's County, Maryland
      8  miami             Miami Metro Area                        6,166,488     06 March 2020            101  40,295       1,613         22,196             Miami-Dade County, Florida
      9  philadelphia      Philadelphia Metro Area                 6,102,434     06 March 2020            101  68,012       5,026         24,475             Philadelphia County, Pennsylvania
     10  atlanta           Atlanta Metro Area                      6,020,364     02 March 2020            105  28,075       1,255         5,308              Gwinnett County, Georgia
     11  phoenix           Phoenix Metro Area                      4,948,203     26 January 2020          141  20,940       601           19,372             Maricopa County, Arizona
     12  boston            Boston Metro Area                       4,873,019     01 February 2020         135  77,267       5,373         23,227             Middlesex County, Massachusetts
     13  detroit           Detroit Metro Area                      4,319,629     10 March 2020             97  42,039       4,746         21,816             Wayne County, Michigan
     14  seattle           Seattle Metro Area                      3,979,845     21 January 2020          146  14,829       838           8,799              King County, Washington
     15  minneapolis       Minneapolis Metro Area                  3,640,043     06 March 2020            101  20,392       1,124         10,281             Hennepin County, Minnesota
     16  sandiego          San Diego Metro Area                    3,338,330     10 February 2020         126  9,673        320           9,673              San Diego County, California
     17  tampa             Tampa Metro Area                        3,194,831     01 March 2020            106  6,899        221           3,826              Hillsborough County, Florida
     18  denver            Denver Metro Area                       2,967,239     05 March 2020            102  18,591       1,121         6,376              Denver County, Colorado
     19  stlouis           St. Louis Metro Area                    2,803,228     07 March 2020            100  12,264       975           5,604              St. Louis County, Missouri
     20  baltimore         Baltimore Metro Area                    2,800,053     08 March 2020             99  23,162       1,169         7,220              Baltimore County, Maryland
     21  charlotte         Charlotte Metro Area                    2,636,883     11 March 2020             96  11,902       248           7,321              Mecklenburg County, North Carolina
     22  orlando           Orlando Metro Area                      2,608,147     12 March 2020             95  5,401        95            3,281              Orange County, Florida
     23  sanantonio        San Antonio Metro Area                  2,550,960     12 February 2020         124  5,169        105           4,449              Bexar County, Texas
     24  portland          Portland Metro Area                     2,492,412     28 February 2020         108  3,707        142           1,559              Multnomah County, Oregon
     25  sacramento        Sacramento Metro Area                   2,363,730     21 February 2020         115  2,555        96            1,793              Sacramento County, California
     26  pittsburgh        Pittsburgh Metro Area                   2,317,600     13 March 2020             94  3,765        316           2,086              Allegheny County, Pennsylvania
     27  lasvegas          Las Vegas Metro Area                    2,266,715     05 March 2020            102  8,815        379           8,815              Clark County, Nevada
     28  austin            Austin Metro Area                       2,227,083     13 March 2020             94  7,004        145           4,664              Travis County, Texas
     29  cincinnati        Cincinnati Metro Area                   2,221,208     14 March 2020             93  7,070        353           3,250              Hamilton County, Ohio
     30  kansascity        Kansas City Metro Area                  2,157,990     07 March 2020            100  5,518        197           1,750              Wyandotte County, Kansas

One can also select MSAs with the ``--metros`` flag. The ``-f`` or ``--format`` flag prints out a table of MSAs formatted in one of three ways: ``simple``, the default, is the tabular format shown above; ``github`` is `Github flavored Markdown`_; and ``rst`` is reStructuredText_. This is described in the help output, produced by ``covid19_create_movie_or_summary M -h``,

.. code-block:: console

   usage: covid19_create_movie_or_summary M [-h] [-f {simple,github,rst}]
					 [--metros METROS]

   optional arguments:
     -h, --help            show this help message and exit
     -f {simple,github,rst}, --format {simple,github,rst}
			   Format of the table that displays MSA summary. Default
			   is "simple".
     --metros METROS       If chosen, list of selected metros for which to
			   summarize COVID-19 data.

I have typically not specified a list of metros.

.. _show_mode:

show mode
^^^^^^^^^^
``covid19_create_movie_or_summary s`` (SHOW flag) summarizes the latest COVID-19 statistics for a specified MSA. The help output, while running ``covid19_create_movie_or_summary s -h``, is shown below,
  
.. code-block:: console

   usage: covid19_create_movie_or_summary s [-h] [-n NAME] [-M MAXNUM] [--conus]
					    [-y]

   optional arguments:
     -h, --help            show this help message and exit
     -n NAME, --name NAME  Create a summary plot and incident data file of this
			   metropolitan area. Default is "bayarea".
     -M MAXNUM, --maxnum MAXNUM
			   The limit of cases/deaths to visualize. Default is a
			   plausible amount for the chosen MSA or CONUS. You
			   should use a limit larger (by at least 2, no more than
			   10) than the maximum number of cases recorded for a
			   county in that MSA or CONUS.
     --conus               If chosen, then make a movie of the COVID-19 cases and
			   deaths trends for the Continental US (CONUS).
     -y, --yes             If chosen, then do not confirm --maxnum.

The required ``-n`` or ``--name`` flag specifies the MSA. The ``-M`` or ``--maxnum`` sets the color limits of cases and deaths to this number (the default is a number that is comfortable above the maximum number of cases in a county in the MSA); and the ``-y`` or ``--yes`` flag suppresses the intermediate prompt that asks the user whether the specified or default maximum number is sufficient. For example, for the NYC metro area,

.. code-block:: console

   bash$ covid19_create_movie_or_summary s -n nyc

   HERE ARE DETAILS FOR NYC Metro Area.
   2019 EST. POP = 19,216,182.
   FIRST CASE:  01 March 2020.
   LATEST CASE: 30 January 2021 (335 days after first case)
   MAXIMUM NUMBER OF CASES: 603,428 (in New York City, New York)
   MAXIMUM NUMBER OF CASES FOR VISUALIZATION: 1,000,000.
   CONTINUE (must choose one) [y/n]:

.. warning::

   The command line output shown above for the operation of ``covid19_create_movie_or_summary s -n nyc`` is for 31 JANUARY 2021. Example images shown below are for this or *later* dates.

This mode of operation, for example for NYC will output the following seven files:

* ``covid19_nyc_LATEST.pkl.gz`` is the `Pandas DataFrame`_  of the COVID-19 cases and deaths, total and per county, from the date of first incident to the latest incident.

* ``covid19_nyc_cds_LATEST.pdf`` and ``covid19_nyc_cds_LATEST.png`` are the PDF and PNG showing the trend of COVID-19 cases and deaths in the NYC metro area.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_nyc_cds_LATEST.png
     :width: 100%
     :align: left

     The *latest* trend lines of cumulative cases and deaths in the NYC metropolitan area.
  
* ``covid19_nyc_cases_LATEST.pdf`` and ``covid19_nyc_cases_LATEST.png`` are the PDF and PNG showing the county map, colored by number of COVID-19 cases, on the *LAST* incident day.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_nyc_cases_LATEST.png
     :width: 100%
     :align: left

     The *latest* image of cumulative cases in the NYC metropolitan area.

* ``covid19_nyc_death_LATEST.pdf`` and ``covid19_nyc_death_LATEST.png`` are the PDF and PNG showing the county map, colored by number of COVID-19 deaths, on the *LAST* incident day.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_nyc_death_LATEST.png
     :width: 100%
     :align: left

     The *latest* image of cumulative deaths in the NYC metropolitan area.

.. _movie_mode:
  
movie mode
^^^^^^^^^^^
``covid19_create_movie_or_summary m`` (MOVIE flag) creates an MP4_ movie of COVID-19 cases and deaths for the MSA you specify (see the :ref:`high quality GIF animations <gif_animations>` of these MP4 movies). The help output, while running ``covid19_create_movie_or_summary m -h``, is shown below,

.. code-block:: console

   usage: covid19_create_movie_or_summary m [-h] [-n NAME] [-M MAXNUM] [--conus]
					    [-y]

   optional arguments:
     -h, --help            show this help message and exit
     -n NAME, --name NAME  Make a movie of this metropolitan area. Default is
			   "bayarea"
     -M MAXNUM, --maxnum MAXNUM
			   The limit of cases/deaths to visualize. Default is a
			   plausible amount for the chosen MSA or CONUS. You
			   should use a limit larger (by at least 2, no more than
			   10) than the maximum number of cases recorded for a
			   county in that MSA or CONUS.
     --conus               If chosen, then make a movie of the COVID-19 cases and
			   deaths trends for the Continental US (CONUS).
     -y, --yes             If chosen, then do not confirm --maxnum.

The meaning of the ``-M`` and ``-y`` flags are the same as in :ref:`SHOW mode <show_mode>`. This mode of operation, for example for NYC,

.. code-block:: console

   covid19_create_movie_or_summary m -n nyc -y

will output a quad structured movie of the cumulative COVID-19 cases and deaths for the NYC metropolitan area, `covid19_nyc_LATEST.mp4`_. :numref:`fig_covid19_nyc_LATEST` is a GIF animation of that.

.. _fig_covid19_nyc_LATEST:

.. figure:: https://tanimislam.github.io/covid19movies/covid19_nyc_LATEST.gif
   :width: 100%
   :align: left

   The four-quadrant movie, that ``covid19_create_movie_or_summary m`` creates, of the cumulative COVID-19 cases and deaths in the NYC metropolitan area. Upper left quad is the summary information for the MSA. Lower left quad is the running tally of cumulative cases and deaths, by day from first incident. Upper right is *logarithmic* coloration of cumulative deaths, by day from first incident. Lower right is *logarithmic* coloration of cumulative cases, by day from first incident.

Note also that the created MP4_ files have metadata associated with them. You can either inspect them using mp4info_ or using code in the :py:mod:`mutagen.mp4.MP4`. Here is what ``mp4info covid19_nyc_LATEST.mp4`` returns,

.. code-block:: console

   mp4info version -r
   covid19_nyc_LATEST.mp4:
   Track   Type    Info
   1       video   H264 High@4, 67.200 secs, 160 kbps, 1590x1172 @ 5.000000 fps
    Name: nyc, ALL, 30-01-2021
    Artist: Tanim Islam
    Encoded with: Lavf57.56.101
    Release Date: 30-01-2021
    Album: METROPOLITAN STATISTICAL AREA

For MSAs,

* *Album* is ``METROPOLITAN STATISTICAL AREA``.
* *Artist* is `Tanim Islam`_ (duh).
* *Name* is MSA name, ``ALL`` if showing cases and deaths as quads in one movie (this is what `covid19_nyc_LATEST.mp4`_ shows), and the *last date* of COVID-19 cases and deaths that are reported.
* *Release Date* is also the *last date* of COVID-19 cases and deaths that are reported.

For the CONUS_, such as `covid19_conus_LATEST.mp4`_, here is the output when running mp4info_,

.. code-block:: console

   mp4info version -r
   covid19_conus_LATEST.mp4:
   Track   Type    Info
   1       video   H264 High@5, 75.200 secs, 277 kbps, 1908x1166 @ 5.000000 fps
    Name: conus, ALL, 30-01-2021
    Artist: Tanim Islam
    Encoded with: Lavf57.56.101
    Release Date: 30-01-2021
    Album: CONUS

And here is its metadata,

* *Album* is ``CONUS``.
* *Name* is ``CONUS``, ``ALL`` if showing cases and deaths as quads in one movie (this is what `covid19_conus_LATEST.mp4`_ shows), and the *last date* of COVID-19 cases and deaths that are reported.

.. _movie_cases_deaths_mode:

movie cases deaths mode
^^^^^^^^^^^^^^^^^^^^^^^^
This is similar to :ref:`movie_mode`, except now we can visualize movies of cases or deaths, and optionally *save*, the collection of PNG_ images used to create the movie, into a zip file. The help output, while running ``covid19_create_movie_or_summary mcd -h``, is shown below,

.. code-block:: console

   usage: covid19_create_movie_or_summary mcd [-h] [-n NAME] [-d DISP] [-M MAXNUM] [-s] [--conus] [-y]

   optional arguments:
     -h, --help            show this help message and exit
     -n NAME, --name NAME  Create a summary plot and incident data file of this metropolitan area. Default is "bayarea".
     -d DISP, --disp DISP  Whether to display the "cases" or "death" trends of the MSA or CONUS. Default is "cases".
     -M MAXNUM, --maxnum MAXNUM
			   The limit of cases/deaths to visualize. Default is a plausible amount for the chosen MSA or CONUS. You
			   should use a limit larger (by at least 2, no more than 10) than the maximum number of cases recorded
			   for a county in that MSA or CONUS.
     -s, --saveimages      If chosen, then save the images used to create the movie into a ZIP archive.
     --conus               If chosen, then make a movie of the COVID-19 cases and deaths trends for the Continental US (CONUS).
     -y, --yes             If chosen, then do not confirm --maxnum.

The usage of four flags -- ``-n``, ``-M`` or ``--maxnum``, ``--conus``, and ``-y`` or ``--yes`` -- are the same as described in :numref:`show_mode` and :numref:`movie_mode`.

* ``-d`` or ``-disp`` lets you choose whether to create a movie of the ``cases`` or ``deaths`` within the CONUS or a specific MSA.

* ``-s`` or ``--saveimages`` optionally lets you choose to save the PNG_ images into a zip archive.

:numref:`fig_covid19_nyc_cases_LATEST` and :numref:`fig_covid19_nyc_death_LATEST` demonstrates this operation to create COVID-19 ``cases`` and ``deaths`` summary movies for the NYC metropolitan area. The command line syntax to generate these two movies is shown in each of their captions.

.. _fig_covid19_nyc_cases_LATEST:

.. figure:: https://tanimislam.github.io/covid19movies/covid19_nyc_cases_LATEST.gif
   :width: 100%
   :align: left

   The trend of latest COVID-19 cumulative cases (lower right quadrant in :numref:`fig_covid19_nyc_LATEST`) in the NYC metropolitan area. The underlying MP4 file is `covid19_nyc_cases_LATEST.mp4`_. The syntax used to create this movie is,

   .. code-block:: console

      covid19_create_movie_or_summary mcd -n nyc -d cases -y

.. _fig_covid19_nyc_death_LATEST:

.. figure:: https://tanimislam.github.io/covid19movies/covid19_nyc_deaths_LATEST.gif
   :width: 100%
   :align: left

   The trend of latest COVID-19 cumulative deaths (upper right quadrant in :numref:`fig_covid19_nyc_LATEST`) in the NYC metropolitan area. The underlying MP4 file is `covid19_nyc_deaths_LATEST.mp4`_. The syntax used to create this movie is,

   .. code-block:: console

      covid19_create_movie_or_summary mcd -n nyc -d death -y
      
Finally, :numref:`fig_covid19_conus_cases_LATEST` demonstrates the latest trend of COVID-19 cases in the CONUS_. I generate it by running,

.. code-block:: console

   covid19_create_movie_or_summary mcd --conus -d cases -y

.. _fig_covid19_conus_cases_LATEST:

.. figure:: https://tanimislam.github.io/covid19movies/covid19_conus_cases_LATEST.gif
   :width: 100%
   :align: left

   The trend of latest COVID-19 cumulative cases for the CONUS_. The underlying MP4 file is `covid19_conus_cases_LATEST.mp4`_. The limits of the cases in each county is deliberate.


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
.. _CONUS: https://en.wikipedia.org/wiki/Contiguous_United_States
.. _`covid19_nyc_LATEST.mp4`: https://tanimislam.github.io/covid19movies/covid19_nyc_LATEST.mp4
.. _`covid19_conus_LATEST.mp4`: https://tanimislam.github.io/covid19movies/covid19_conus_LATEST.mp4
.. _PNG: https://en.wikipedia.org/wiki/Portable_Network_Graphics
.. _`covid19_nyc_cases_LATEST.mp4`: https://tanimislam.github.io/covid19movies/covid19_nyc_cases_LATEST.mp4
.. _`covid19_nyc_deaths_LATEST.mp4`: https://tanimislam.github.io/covid19movies/covid19_nyc_deaths_LATEST.mp4
.. _`covid19_conus_cases_LATEST.mp4`: https://tanimislam.github.io/covid19movies/covid19_conus_cases_LATEST.mp4
.. _mp4info: https://www.bento4.com/documentation/mp4info
.. _`Tanim Islam`: https://tanimislam.github.io
