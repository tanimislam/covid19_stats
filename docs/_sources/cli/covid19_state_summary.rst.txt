.. include:: cli_urls.rst

.. _covid19_state_summary:
	     
covid19_state_summary
======================
This CLI behaves *very* similarly to :ref:`covid19_create_movie_or_summary`, except it operates on US states or territories instead of the CONUS_ or US MSAs. It has *three* modes of operation. Its help output, when running ``covid19_state_summary -h``, produces the following hard-to-read output,

.. code-block:: console

   usage: covid19_state_summary [-h] [-d DIRNAME] [--info]
				[-n {Alabama,Alaska,Arizona,Arkansas,California,Colorado,Connecticut,Delaware,District of Columbia,Florida,Georgia,Hawaii,Idaho,Illinois,Indiana,Iowa,Kansas,Kentucky,Louisiana,Maine,Maryland,Massachusetts,Michigan,Minnesota,Mississippi,Missouri,Montana,Nebraska,Nevada,New Hampshire,New Jersey,New Mexico,New York,North Carolina,North Dakota,Ohio,Oklahoma,Oregon,Pennsylvania,Puerto Rico,Rhode Island,South Carolina,South Dakota,Tennessee,Texas,Utah,Vermont,Virginia,Washington,West Virginia,Wisconsin,Wyoming}]
				[-M MAXNUM] [-y]
				{m,s,mcd} ...

   positional arguments:
     {m,s,mcd}             Choose one of three options: (m) make a movie of the COVID-19 cumulative stats for the state; (s) dumps summary plots of last incident date, and cumulative covid-19
			   stats, of a state; and (mcd) make a movie of either "CASES" or "DEATHS" in the state.
       m                   Make a movie of the COVID-19 cases and deaths trend for the specific state.
       s                   Make a summary plot, and incident data file, of COVID-19 cases and deaths trend, for the specific state.
       mcd                 Make a large-sized movie of either "CASES" or "DEATHS" for given state.

   optional arguments:
     -h, --help            show this help message and exit
     -d DIRNAME, --dirname DIRNAME
			   The directory into which to store the resulting files. Default is /g/g12/islam5/.local/src/covid19_stats/docsrc.
     --info                If chosen, then print out INFO level logging statements.
     -n {Alabama,Alaska,Arizona,Arkansas,California,Colorado,Connecticut,Delaware,District of Columbia,Florida,Georgia,Hawaii,Idaho,Illinois,Indiana,Iowa,Kansas,Kentucky,Louisiana,Maine,Maryland,Massachusetts,Michigan,Minnesota,Mississippi,Missouri,Montana,Nebraska,Nevada,New Hampshire,New Jersey,New Mexico,New York,North Carolina,North Dakota,Ohio,Oklahoma,Oregon,Pennsylvania,Puerto Rico,Rhode Island,South Carolina,South Dakota,Tennessee,Texas,Utah,Vermont,Virginia,Washington,West Virginia,Wisconsin,Wyoming}
			   Make movies or other summary data for a state. Default is "New York".
     -M MAXNUM, --maxnum MAXNUM
			   The limit of cases/deaths to visualize. Default is a plausible amount for the chosen state. You should use a limit larger (by at least 2, no more than 10) than the
			   maximum number of cases recorded for a county in that state.
     -y, --yes             If chosen, then do not confirm --maxnum.

Instead of what :ref:`covid19_create_movie_or_summary` does, we first specify these common elements,

* the *state* (with the ``-n`` flag),
* the optional legend or color maximum (with ``-M`` or ``--maxnum``),
* the optional specific output directory (with ``-d`` or ``--directory``),
* the forcing flag (with the ``-y`` or ``--yes`` flag),

before moving to the three operations. The functionality of ``-M`` or ``--maxnum``, ``-d`` or ``--directory``, and ``-y`` or ``--yes``, is identical to what :ref:`covid19_create_movie_or_summary` does.

The ``--info`` flag prints out ``INFO`` level debugging statements.

.. _show_mode_state:

show mode
-----------
``covid19_state_summary s`` (SHOW flag) summarizes the latest COVID-19 statistics for a specified US state or territory. Here is what happens when we run the SHOW flag on California,

.. code-block:: console

   bash$ covid19_state_summary -n California s

   HERE ARE DETAILS FOR California.
   2019 EST. POP = 39,239,334.
   FIRST CASE:  25 January 2020.
   LATEST CASE: 03 February 2021 (375 days after first case)
   MAXIMUM NUMBER OF CASES: 1,129,957 (in Los Angeles County, California)
   MAXIMUM NUMBER OF CASES FOR VISUALIZATION: 1,700,000.
   CONTINUE (must choose one) [y/n]:

.. warning::

   The command line output shown above for the operation of ``covid19_state_summary -n California s`` is for 03 FEBRUARY 2021. Example images shown below are for this or *later* dates.

This mode of operation, for example for California, will output seven files:

* ``covid19_california_LATEST.pkl.gz`` is the `Pandas DataFrame`_  of the COVID-19 cases and deaths, total and per county, from the date of first incident to the latest incident.


* ``covid19_california_cds_LATEST.pdf`` and ``covid19_california_cds_LATEST.png`` are the PDF and PNG showing the trend of COVID-19 cases and deaths in California.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_california_cds_LATEST.png
     :width: 100%
     :align: left

     The *latest* trend lines of cumulative cases and deaths in California.
  
* ``covid19_california_cases_LATEST.pdf`` and ``covid19_california_cases_LATEST.png`` are the PDF and PNG showing the county map, colored by number of COVID-19 cases, on the *LAST* incident day.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_california_cases_LATEST.png
     :width: 100%
     :align: left

     The *latest* image of cumulative cases in California.

* ``covid19_california_death_LATEST.pdf`` and ``covid19_california_death_LATEST.png`` are the PDF and PNG showing the county map, colored by number of COVID-19 deaths, on the *LAST* incident day.

  .. figure:: https://tanimislam.github.io/covid19movies/covid19_california_death_LATEST.png
     :width: 100%
     :align: left

     The *latest* image of cumulative deaths in California.

.. _movie_mode_state:

movie mode
-----------
``covid19_state_summary m`` (MOVIE flag) creates an MP4_ movie of COVID-19 cases and deaths for the US state or territory you specify. Its functionality is very similar to :ref:`movie mode in covid19_create_movie_or_summary <movie_mode>`.

This mode of operation for California,

.. code-block:: console

   covid19_state_summary -n California -y m

will output a quad structured movie of the cumulative COVID-19 cases and deaths for California, `covid19_california_LATEST.mp4`_. :numref:`fig_covid19_california_LATEST` is a GIF animation of that.

.. _fig_covid19_california_LATEST:

.. figure:: https://tanimislam.github.io/covid19movies/covid19_california_LATEST.gif
   :width: 100%
   :align: left

   The four-quadrant movie, that ``covid19_state_summary m`` creates, of the cumulative COVID-19 cases and deaths in the state of California. Upper left quad is the summary information for the MSA. Lower left quad is the running tally of cumulative cases and deaths, by day from first incident. Upper right is *logarithmic* coloration of cumulative deaths, by day from first incident. Lower right is *logarithmic* coloration of cumulative cases, by day from first incident. Its structure matches that of :numref:`fig_covid19_nyc_LATEST`.

Note also that the created MP4_ files have metadata associated with them. You can either inspect them using mp4info_ or using code in the :py:mod:`mutagen.mp4.MP4`. Here is what ``mp4info covid19_california_LATEST.mp4`` returns,

.. code-block:: console

   mp4info version -r
   docs/covid19_california_LATEST.mp4:
   Track   Type    Info
   1       video   H264 High@4, 75.000 secs, 153 kbps, 1330x1168 @ 5.000000 fps
    Name: california, ALL, 02-02-2021
    Artist: Tanim Islam
    Encoded with: Lavf57.56.101
    Release Date: 02-02-2021
    Album: STATE

.. _states_ALL_mp4_metadata:
    
For US states and territories,

* *Album* is ``STATE``.
* *Artist* is `Tanim Islam`_ (duh).
* *Name* is the name of the US state or territory, ``ALL`` if showing cases and deaths as quads in one movie (this is what `covid19_california_LATEST.mp4`_ shows), and the *last date* of COVID-19 cases and deaths that are reported.
* *Release Date* is also the *last date* of COVID-19 cases and deaths that are reported.
