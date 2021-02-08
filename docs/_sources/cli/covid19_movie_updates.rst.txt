.. include:: cli_urls.rst

.. _covid19_movie_updates:
	     
covid19_movie_updates
======================
This CLI is designed to be used by an external service to update the COVID-19 cumulative case and death summary movies and figures for the CONUS_, MSAs, and US states or territories. It uses MPI_ through the mpi4py_ Python module to parallelize the process of creating summary movies and figures; thus, it can leverage running on a supercomputer to parallelize individually long and high-memory tasks.

It uses API level back-ends to create COVID-19 summary movies and figures, of the CLI front-ends :ref:`covid19_create_movie_or_summary` and :ref:`covid19_state_summary`. Its help output, when running ``covid19_movie_updates -h``, is the following,

.. code-block:: console

   usage: covid19_movie_updates [-h] [--region [region [region ...]]] [--state [state [state ...]]] [--dirname DIRNAME] [--topN TOPN] [--info]

   optional arguments:
     -h, --help            show this help message and exit
     --region [region [region ...]]
			   regions to choose to create summary plots, big movies, and smaller movies.
     --state [state [state ...]]
			   states to choose to create summary plots, big movies, and smaller movies.
     --dirname DIRNAME     The name of the directory to which to put all this stuff. Default is /g/g12/islam5/.local/src/covid19_stats/docsrc.
     --topN TOPN           Print out JSON formatted COVID-19 summary data for the topN US MSAs. Default is 50.
     --info                If chosen, then turn on INFO logging.

This will create *nine* COVID-19 case and death summary movies and figures for each specified region you specify: the CONUS_ (if chosen), MSAs, and US states and territories. For example, for the CONUS_, it creates these figures and movies in the specified output directory,

* `covid19_conus_cds_LATEST.png <https://tanimislam.github.io/covid19movies/covid19_conus_cds_LATEST.png>`_ and `covid19_conus_cds_LATEST.pdf <https://tanimislam.github.io/covid19movies/covid19_conus_cds_LATEST.pdf>`_ are the PDF and PNG showing the *latest* trend of COVID-19 cases and deaths in the CONUS_.

* `covid19_conus_cases_LATEST.pdf <https://tanimislam.github.io/covid19movies/covid19_conus_cases_LATEST.pdf>`_ and `covid19_conus_cases_LATEST.png <https://tanimislam.github.io/covid19movies/covid19_conus_cases_LATEST.png>`_ are the PDF and PNG showing the CONUS_ county map, colored by number of COVID-19 cases, on the *LAST* incident day.

* `covid19_conus_death_LATEST.pdf <https://tanimislam.github.io/covid19movies/covid19_conus_death_LATEST.pdf>`_ and `covid19_conus_death_LATEST.png <https://tanimislam.github.io/covid19movies/covid19_conus_death_LATEST.png>`_ are the PDF and PNG showing the CONUS_ county map, colored by number of COVID-19 deaths, on the *LAST* incident day.

* `covid19_conus_LATEST.mp4 <https://tanimislam.github.io/covid19movies/covid19_conus_LATEST.mp4>`_ is the four-quadrant movie of trends, cumulative cases, and cumulative deaths in the CONUS_. See :numref:`fig_covid19_nyc_LATEST` for an example of its format, but for the NYC metropolitan area.

* `covid19_conus_cases_LATEST.mp4 <https://tanimislam.github.io/covid19movies/covid19_conus_cases_LATEST.mp4>`_ is the trend of cumulative cases in the CONUS_ (lower right quadrant of `covid19_conus_LATEST.mp4 <https://tanimislam.github.io/covid19movies/covid19_conus_LATEST.mp4>`_).

* `covid19_conus_deaths_LATEST.mp4 <https://tanimislam.github.io/covid19movies/covid19_conus_deaths_LATEST.mp4>`_ is the trend of cumulative deaths in the CONUS_ (upper right quadrant of `covid19_conus_LATEST.mp4 <https://tanimislam.github.io/covid19movies/covid19_conus_LATEST.mp4>`_).

Here are the flags and their meanings.
  
* ``--dirname`` specifies the directory into which to dump the output simulation results. The default is current working directory.

* ``--region`` specifies the MSAs or CONUS_. Thus, ``--region nyc conus`` means to create summary data for the NYC metropolitan area and the CONUS_.

* ``--state`` specifies the US states or territories. Thus, ``--state California Texas Virginia`` means to create summary data for the states of California, Texas, and Virginia.

* In addition, the ``--topN`` flag specifies the :math:`N \ge 1` top MSAs for which to create and store COVID-19 summary data into a JSON_ file. This JSON_ file lives in the speciified directory. Its name is :download:`covid19_topN_LATEST.json <examples/covid19_topN_LATEST.json>`. This example file has the data for the top 50 MSAs, and I include it below,

  .. literalinclude:: examples/covid19_topN_LATEST.json
     :language: JSON
     :linenos:
	      
* Finally, the ``--info`` optional flag tells this code to spit out INFO level debugging output.

.. warning::

   This data set can get extremely large even with a few regions. Currently, my (`Tanim Islam`_) data set is over 700 MB in size.

A hopefully illuminating example is shown in :download:`covid19_movie_updates_example.bash <examples/covid19_movie_updates_example.bash>`, where I run a SLURM_ scheduled job to farm out the creation of COVID-19 summary data among *nine* processors to 25 different regions,

* CONUS_
* 13 MSAs: nyc, bayarea, dc, richmond, losangeles, neworleans, chicago, seattle, houston, dallas, albuquerque, newhaven.
* 12 US states or territories: California, Virginia, Texas, Florida, "New York", Pennsylvania, Indiana, Michigan, Hawaii, "New Mexico", "New Jersey", Connecticut.

.. literalinclude:: examples/covid19_movie_updates_example.bash
   :language: bash
   :linenos:
   :lines: 1-61
