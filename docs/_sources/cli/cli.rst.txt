.. include:: cli_urls.rst

.. _using_the_cli:

USING THE CLI
==================
There are *six* command line interfaces that have been defined here.

The first CLI, :ref:`covid19_update_database`, *only* updates the  `NY Times COVID-19 repository`_ with the latest data.

The next two CLIs, :ref:`covid19_create_movie_or_summary` and :ref:`covid19_state_summary`, synthesize the COVID-19 movies and figures, that represent cumulative cases and deaths, for metropolitan statistical areas (MSAs), the CONUS_, or individual US states and territories.

The final three CLIs, :ref:`covid19_movie_updates`, :ref:`covid19_post2server`, and :ref:`covid19_update_readme`, are designed for external services to *deploy* summary data on specific US regions into other locations.

.. toctree::
   :maxdepth: 3

   covid19_update_database
   covid19_create_movie_or_summary
   covid19_state_summary
   covid19_movie_updates
   covid19_post2server
   covid19_update_readme
