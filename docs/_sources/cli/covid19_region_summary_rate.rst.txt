.. include:: cli_urls.rst

.. _covid19_region_summary_rate:
	     
covid19_region_summary_rate
============================
The CLIs :ref:`covid19_create_movie_or_summary` and :ref:`covid19_state_summary` inspires this CLI. Unlike those tools, which visualize the *cumulative* COVID-19 cases and deaths for US geographical regions, this tool visualizes the *seven day average* new COVID-19 cases and deaths. This is designed to better identify COVID-19 hot spots as they flare up. It has *three* specific modes of operation. Its help output, when running ``covid19_region_summary_rate -h``, produces the following output,

.. code-block:: console

   usage: covid19_region_summary_rate [-h] [-d DIRNAME] [--info] [-R REGION] [--states] [--msas] {m,s,mcd} ...

   positional arguments:
     {m,s,mcd}             Choose one of three options: (m) make a movie of the COVID-19 cumulative stats for a geographhical region; (s) dumps summary plots of last incident date, and cumulative covid-19 stats, of a
			   geographical region; and (mcd) make a movie of either "CASES" or "DEATHS" in a geographical region.
       m                   Make a movie of the COVID-19 7-day averaged new cases and deaths trend for a geographical region.
       s                   Make a summary plot, and incident data file, of COVID-19 7-day averaged new cases and deaths trend, for a geographical region.
       mcd                 Make a large-sized movie of either "CASES" or "DEATHS" for a geographical region.

   optional arguments:
     -h, --help            show this help message and exit
     -d DIRNAME, --dirname DIRNAME
			   The directory into which to store the resulting files. Default is /usr/WS2/islam5/covid19_stats.
     --info                If chosen, then print out INFO level logging statements.
     -R REGION, --region REGION
			   Make movies or other summary 7 day averaged COVID-19 data for a geographical region. Can be a state or US territory, can be an MSA, or can be "conus". Default is "nyc".
     --states              If chosen, then print out possible states or US territories as geographical regions that you can choose.
     --msas                If chosen, then print out possible MSAs as geographical regions that you can choose.

These are the common elements for this tool,

* the *region* (with the ``-R`` or ``--region`` flag). This can be the identifier for an MSA_, an US state or territory, or "conus" for the CONUS_,
* the optional specific output directory (with ``-d`` or ``--directory``),

The ``--msas`` flag prints the identifiers for the 380 MSA_\ s, ordered from largest to smallest population. Here is the output from ``covid19_region_summary_rate --msas``,

.. _covid19_region_summary_rate_msas:

.. code-block:: console

   here are the 380 MSAs sorted from largest to smallest population: nyc, losangeles, chicago, dallas, houston, bayarea, dc, miami, philadelphia, atlanta
   phoenix, boston, detroit, seattle, minneapolis, sandiego, tampa, denver, stlouis, baltimore
   charlotte, orlando, sanantonio, portland, sacramento, pittsburgh, lasvegas, austin, cincinnati, kansascity
   columbus, indianapolis, cleveland, nashville, virginiabeach, providence, milwaukee, jacksonville, oklahomacity, raleigh
   memphis, richmond, neworleans, louisville, saltlakecity, hartford, buffalo, birmingham, grandrapids, rochester
   tucson, fresno, tulsa, urbanhonolulu, omaha, worcester, bridgeport, greenville, albuquerque, bakersfield
   albany, knoxville, mcallen, batonrouge, newhaven, elpaso, allentown, columbia, northport, dayton
   charleston, greensboro, capecoral, stockton, boisecity, coloradosprings, littlerock, lakeland, akron, desmoines
   springfield, ogden, poughkeepsie, winston, deltona, madison, syracuse, provo, durham, toledo
   wichita, augusta, palmbay, jackson, harrisburg, spokane, chattanooga, scranton, modesto, lansing
   lancaster, portland_me, youngstown, fayetteville, fayetteville_nc, lexington, pensacola, myrtlebeach, santarosa, portstlucie
   lafayette, reno, huntsville, springfield_mo, visalia, asheville, killeen, york, vallejo, santamaria
   salinas, salem, mobile, corpuschristi, brownsville, reading, gulfport, manchester, salisbury, fortwayne
   flint, peoria, canton, anchorage, shreveport, savannah, beaumont, tallahassee, naples, eugene
   davenport, montgomery, hickory, annarbor, trenton, ocala, fortcollins, huntington, lincoln, rockford
   gainesville, boulder, greeley, southbend, greenbay, lubbock, columbus_ga-al, spartanburg, evansville, roanoke
   clarksville, kingsport, kennewick, wilmington, olympia, utica, duluth, hagerstown, longview, crestview
   sanluisobispo, merced, laredo, waco, santacruz, cedarrapids, bremerton, erie, siouxfalls, norwich
   kalamazoo, amarillo, collegestation, atlanticcity, lynchburg, charleston_wv, tuscaloosa, yakima, fortsmith, fargo
   binghamton, appleton, prescottvalley, lafayette_in, tyler, topeka, macon, bellingham, champaign, daphne
   hiltonheadisland, rochester_mn, medford, burlington, chico, charlottesville, lascruces, yuma, athens, barnstabletown
   lakehavasucity, lakecharles, columbia_mo, houma, springfield_il, elkhart, florence, gainesville_ga, johnsoncity, stcloud
   monroe, jacksonville_nc, bend, racine, saginaw, puntagorda, terrehaute, warnerrobins, midland, billings
   elcentro, dover, greenville_nc, redding, joplin, bowlinggreen, jackson_tn, kingston, stgeorge, yubacity
   panamacity, muskegon, iowacity, abilene, oshkosh, bloomington, eaststroudsburg, burlington_nc, eauclaire, bloomington_in
   hattiesburg, waterloo, pueblo, blacksburg, kahului, odessa, coeurd'alene, auburn, janesville, wausau
   statecollege, sebastian, jackson_mi, madera, chambersburg, grandjunction, elizabethtown, niles, hanford, decatur
   bangor, alexandria, idahofalls, wichitafalls, jeffersoncity, monroe_mi, santafe, homosassasprings, vineland, dothan
   texarkana, florence_al, valdosta, albany_ga, rockymount, dalton, siouxcity, flagstaff, morristown, logan
   rapidcity, lebanon, winchester, sumter, morgantown, wheeling, lacrosse, sherman, carbondale, harrisonburg
   hammond, battlecreek, springfield_oh, jonesboro, thevillages, manhattan, johnstown, albany_or, mountvernon, bismarck
   lawton, sierravista, stjoseph, glensfalls, pittsfield, cleveland_tn, newbern, farmington, ames, goldsboro
   staunton, lawrence, sanangelo, altoona, mansfield, wenatchee, missoula, owensboro, brunswick, weirton
   beckley, sheboygan, muncie, anniston, california, williamsport, twinfalls, longview_wa, michigancity, kankakee
   watertown, lewiston, sebring, decatur_il, fonddulac, baycity, gettysburg, lima, gadsden, ithaca
   mankato, grandforks, victoria, cheyenne, hotsprings, rome, dubuque, cumberland, fairbanks, capegirardeau
   pocatello, corvallis, oceancity, parkersburg, pinebluff, grantspass, columbus_in, elmira, bloomsburg, midland_mi
   kokomo, greatfalls, hinesville, casper, danville, grandisland, lewiston_id-wa, enid, wallawalla, carsoncity.

The ``--states`` flag alphabetically prints out the 52 US states or territories. Here is the output from ``covid19_region_summary_rate --states``,

.. code-block:: console

   here are the 52 states or territories: Alabama, Alaska, Arizona, Arkansas, California, Colorado, Connecticut, Delaware, District of Columbia, Florida
   Georgia, Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas, Kentucky, Louisiana, Maine
   Maryland, Massachusetts, Michigan, Minnesota, Mississippi, Missouri, Montana, Nebraska, Nevada, New Hampshire
   New Jersey, New Mexico, New York, North Carolina, North Dakota, Ohio, Oklahoma, Oregon, Pennsylvania, Puerto Rico
   Rhode Island, South Carolina, South Dakota, Tennessee, Texas, Utah, Vermont, Virginia, Washington, West Virginia
   Wisconsin, Wyoming.

The ``--info`` flag prints out ``INFO`` level debugging statements.

.. _show_mode_region_rate:

show mode
-----------
``covid19_region_summary_rate s`` (SHOW flag) summarizes the latest COVID-19 statistics for an US geographical region.

When we run the SHOW flag on the NYC metro area, with the command, ``covid19_region_summary_rate -R nyc s``, here are the six output files.

* ``covid19_7day_nyc_cds_LATEST.pdf`` and ``covid19_7day_nyc_cds_LATEST.png`` are the PDF and PNG showing the trend of 7-day averaged COVID-19 new cases/day and deaths/day in the NYC metro area.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_nyc_cds_LATEST.png
     :width: 100%
     :align: left

     The *latest* trend lines of 7-day averaged new cases/day and deaths/day in the NYC metro area. Note that overlayed in lower alpha are the *1-day averaged* new cases/day and deaths/day in the NYC metro area. These 1-day averaged plots have substantially more variation than the 7-day averaged plots.
  
* ``covid19_7day_nyc_cases_LATEST.pdf`` and ``covid19_nyc_cases_LATEST.png`` are the PDF_ and PNG_ showing the county map, colored by 7-day averaged number of COVID-19 new cases/day, on the *LAST* incident day.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_nyc_cases_LATEST.png
     :width: 100%
     :align: left

     The *latest* image of 7-day averaged new cases/day in the NYC metro area.

* ``covid19_7day_nyc_death_LATEST.pdf`` and ``covid19_7day_nyc_death_LATEST.png`` are the PDF_ and PNG_ showing the county map, colored by 7-day averaged number of COVID-19 new deaths/day, on the *LAST* incident day.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_nyc_death_LATEST.png
     :width: 100%
     :align: left

     The *latest* image of 7-day averaaged new deaths/day in the NYC metro area.

When we run the SHOW flag on California, with the command, ``covid19_region_summary_rate -R Calfornia s``, here are the six output files.

* ``covid19_7day_california_cds_LATEST.pdf`` and ``covid19_7day_california_cds_LATEST.png`` are the PDF and PNG showing the trend of 7-day averaged COVID-19 new cases/day and deaths/day in California.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_california_cds_LATEST.png
     :width: 100%
     :align: left

     The *latest* trend lines of 7-day averaged new cases/day and deaths/day in California. Note that overlayed in lower alpha are the *1-day averaged* new cases/day and deaths/day in California. These 1-day averaged plots have substantially more variation than the 7-day averaged plots.
  
* ``covid19_7day_california_cases_LATEST.pdf`` and ``covid19_california_cases_LATEST.png`` are the PDF_ and PNG_ showing the county map, colored by 7-day averaged number of COVID-19 new cases/day, on the *LAST* incident day.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_california_cases_LATEST.png
     :width: 100%
     :align: left

     The *latest* image of 7-day averaged new cases/day in California.

* ``covid19_7day_california_death_LATEST.pdf`` and ``covid19_7day_california_death_LATEST.png`` are the PDF_ and PNG_ showing the county map, colored by 7-day averaged number of COVID-19 new deaths/day, on the *LAST* incident day.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_california_death_LATEST.png
     :width: 100%
     :align: left

     The *latest* image of 7-day averaaged new deaths/day in California.

Finally, when we run the SHOW flag on the CONUS_, with the command, ``covid19_region_summary_rate -R conus s``, here are the six output files.

* ``covid19_7day_conus_cds_LATEST.pdf`` and ``covid19_7day_conus_cds_LATEST.png`` are the PDF and PNG showing the trend of 7-day averaged COVID-19 new cases/day and deaths/day in the CONUS_.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_conus_cds_LATEST.png
     :width: 100%
     :align: left

     The *latest* trend lines of 7-day averaged new cases/day and deaths/day in the CONUS_. Note that overlayed in lower alpha are the *1-day averaged* new cases/day and deaths/day in the CONUS_. These 1-day averaged plots have substantially more variation than the 7-day averaged plots.
  
* ``covid19_7day_conus_cases_LATEST.pdf`` and ``covid19_conus_cases_LATEST.png`` are the PDF_ and PNG_ showing the county map, colored by 7-day averaged number of COVID-19 new cases/day, on the *LAST* incident day.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_conus_cases_LATEST.png
     :width: 100%
     :align: left

     The *latest* image of 7-day averaged new cases/day in the CONUS_.

* ``covid19_7day_conus_death_LATEST.pdf`` and ``covid19_7day_conus_death_LATEST.png`` are the PDF_ and PNG_ showing the county map, colored by 7-day averaged number of COVID-19 new deaths/day, on the *LAST* incident day.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_conus_death_LATEST.png
     :width: 100%
     :align: left

     The *latest* image of 7-day averaaged new deaths/day in the CONUS_.

.. _movie_mode_region_rate:

movie mode
-----------
``covid19_region_summary_rate m`` (MOVIE flag) creates a quad MP4_ movie of 7-day averaged new COVID-19 cases/day and deaths/day for a US geographical regions. The help output, while running ``covid19_region_summary_rate m -h``, is shown below,

.. code-block:: console

   usage: covid19_region_summary_rate m [-h] [-s]

   optional arguments:
     -h, --help        show this help message and exit
     -s, --saveimages  If chosen, then save the images used to create the movie into a ZIP archive.

The ``-s`` or ``--saveimages`` optionally lets you choose to save the PNG_ images into a zip archive.
     
This mode of operation for the NYC metro area, ``covid19_region_summary_rate -R nyc m``, will output a quad structured movie of the cumulative COVID-19 cases and deaths for the NYC metro area, `covid19_7day_nyc_LATEST.mp4`_. :numref:`fig_covid19_7day_nyc_LATEST` is a GIF animation of that.

.. _fig_covid19_7day_nyc_LATEST:

.. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_nyc_LATEST.gif
   :width: 100%
   :align: left

   The four-quadrant movie, that ``covid19_state_summary m`` creates, of the 7-day averaged COVID-19 new cases/days and deaths/day for the NYC metro area. Upper left quad is the summary information for the geographical region. Upper right is *logarithmic* coloration of cumulative deaths, by seventh day from first incident. Lower right is *logarithmic* coloration of 7-day averaged new cases/day, by seventh day from first incident. Lower left quad is the running tally of 7-day averaged new cases/day and deaths, by seventh day from first incident; in lower alpha, overlayed over the 7-day averaged running tallies, are 1-day averaged running tallies of new cases/day and deaths/day.

This mode of operation for California, ``covid19_region_summary_rate -R California m``, will output a quad structured movie of the cumulative COVID-19 cases and deaths for California, `covid19_7day_california_LATEST.mp4`_. :numref:`fig_covid19_7day_california_LATEST` is a GIF animation of that.

.. _fig_covid19_7day_california_LATEST:

.. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_california_LATEST.gif
   :width: 100%
   :align: left

   The four-quadrant movie, that ``covid19_state_summary m`` creates, of the 7-day averaged COVID-19 new cases/days and deaths/day in the state of California. Format of the movie is the same as :numref:`fig_covid19_7day_nyc_LATEST`.

This mode of operation for the CONUS_, ``covid19_region_summary_rate -R conus m``, will output a quad structured movie of the cumulative COVID-19 cases and deaths for the CONUS_, `covid19_7day_conus_LATEST.mp4`_. :numref:`fig_covid19_7day_conus_LATEST` is a GIF animation of that.

.. _fig_covid19_7day_conus_LATEST:

.. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_conus_LATEST.gif
   :width: 100%
   :align: left

   The four-quadrant movie, that ``covid19_state_summary m`` creates, of the 7-day averaged COVID-19 new cases/days and deaths/day in the CONUS_. Format of the movie is the same as :numref:`fig_covid19_7day_nyc_LATEST`.

Note also that the created MP4_ files have metadata associated with them. You can either inspect them using mp4info_ or using code in :py:mod:`mutagen.mp4.MP4`.

Here is what ``mp4info covid19_7day_nyc_LATEST.mp4`` returns,

.. code-block:: console

   mp4info version -r
   docs/covid19_7day_nyc_LATEST.mp4:
   Track   Type    Info
   1       video   H264 High@4, 76.000 secs, 207 kbps, 1610x1186 @ 5.000000 fps
    Name: nyc, ALL 7 day new, 22-03-2021
    Artist: Tanim Islam
    Encoded with: Lavf57.56.101
    Release Date: 22-03-2021
    Album: METROPOLITAN STATISTICAL AREA

.. _nyc_ALL_rate_mp4_metadata:
    
For MSA_\ s,

* *Album* is ``STATE``.
* *Artist* is `Tanim Islam`_ (duh).
* *Name* is the name of the US state or territory, ``ALL 7 day new`` if showing 7-day averaged new cases/day and deaths/day as quads in one movie (this is what `covid19_7day_california_LATEST.mp4`_ shows), and the *last date* of COVID-19 cases and deaths that are reported.
* *Release Date* is also the *last date* of COVID-19 cases and deaths that are reported.

Here is what ``mp4info covid19_7day_california_LATEST.mp4`` returns,

.. _california_ALL_rate_mp4_metadata:

.. code-block:: console

   mp4info version -r
   docs/covid19_7day_california_LATEST.mp4:
   Track   Type    Info
   1       video   H264 High@4, 83.200 secs, 197 kbps, 1370x1186 @ 5.000000 fps
    Name: california, ALL 7 day new, 22-03-2021
    Artist: Tanim Islam
    Encoded with: Lavf57.56.101
    Release Date: 22-03-2021
    Album: STATE
    
For US states and territories, the only difference from :ref:`metadata for MSAs <nyc_all_RATE_mp4_metadata>` is, the *Album*, which is ``STATE``.

Finally, here is what ``mp4info covid19_7day_conus_LATEST.mp4`` returns,

.. _conus_ALL_rate_mp4_metadata:

.. code-block:: console

   mp4info version -r
   docs/covid19_7day_conus_LATEST.mp4:
   Track   Type    Info
   1       video   H264 High@4, 84.000 secs, 328 kbps, 1754x1166 @ 5.000000 fps
    Name: conus, ALL 7 day new, 22-03-2021
    Artist: Tanim Islam
    Encoded with: Lavf57.56.101
    Release Date: 22-03-2021
    Album: CONUS

For the CONUS_, the only difference from :ref:`metadata for MSAs <nyc_all_RATE_mp4_metadata>` is, the *Album*, which is ``CONUS``.
    
.. _movie_cases_deaths_mode_region_rate:

movie cases deaths mode
-------------------------
This is similar to :numref:`movie_mode_region_rate`, except we visualize movies of cases or deaths. The help output, while running ``covid19_region_summary_rate mcd -h``, is shown below,

.. code-block:: console

   usage: covid19_region_summary_rate mcd [-h] [-D DISP] [-s]

   optional arguments:
     -h, --help            show this help message and exit
     -D DISP, --disp DISP  Whether to display the "cases" or "death" trends of the given state. Default is "cases".
     -s, --saveimages      If chosen, then save the images used to create the movie into a ZIP archive.

* ``-D`` or ``--disp`` lets you choose whether to create a movie of the ``cases`` or ``deaths`` within the specified US state or territory.

* ``-s`` or ``--saveimages`` optionally lets you choose to save the PNG_ images into a zip archive.

:numref:`fig_covid19_7day_california_cases_LATEST` and :numref:`fig_covid19_7day_california_death_LATEST` demonstrates this operation to create COVID-19 ``cases`` and ``deaths`` summary movies for the NYC metropolitan area. The command line syntax to generate these two movies is shown in each of their captions.

.. _fig_covid19_7day_california_cases_LATEST:

.. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_california_cases_LATEST.gif
   :width: 100%
   :align: left

   The trend of latest 7-day averaged COVID-19 new cases/day (lower right quadrant in :numref:`fig_covid19_7day_california_LATEST`) in California. The underlying MP4 file is `covid19_7day_california_cases_LATEST.mp4`_. The syntax used to create this movie is,

   .. code-block:: console

      covid19_region_summary_rate -R California mcd -d cases

.. _fig_covid19_7day_california_death_LATEST:

.. figure:: https://tanimislam.github.io/covid19movies/covid19_7day_california_deaths_LATEST.gif
   :width: 100%
   :align: left

   The trend of latest 8-day averaged COVID-19 new deaths/day (upper right quadrant in :numref:`fig_covid19_7day_california_LATEST`) in California. The underlying MP4 file is `covid19_7day_california_deaths_LATEST.mp4`_. The syntax used to create this movie is,

   .. code-block:: console

      covid19_region_summary_rate -R California mcd -d death
   
Note also that the created MP4_ files have metadata associated with them. You can either inspect them using mp4info_ or using code in the :py:mod:`mutagen.mp4.MP4`.

Here is what ``mp4info covid19_7day_california_cases_LATEST.mp4`` returns,

.. code-block:: console

   mp4info version -r
   covid19_7day_california_cases_LATEST.mp4:
   Track   Type    Info
   1       video   H264 High@5, 83.200 secs, 228 kbps, 1900x1482 @ 5.000000 fps
    Name: california, CASES 7 day new, 22-03-2021
    Artist: Tanim Islam
    Encoded with: Lavf57.56.101
    Release Date: 22-03-2021
    Album: STATE

.. _california_casedeath_mp4_metadata:
    
Its metadata is similar to those :ref:`MP4 movies that show COVID-19 cases and deaths <nyc_ALL_rate_mp4_metadata>`. The difference is in the second element of the *Name*: it is ``CASES 7 day new`` if the movie shows cumulative COVID-19 cases, and ``DEATHS 7 day new`` if the movie shows cumulative COVID-19 deaths.
