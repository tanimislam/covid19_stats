.. include:: api_urls.rst

.. _using_the_api:

THE COVID19_STATS API
========================
The API provides a much richer base of functionality than the :ref:`CLI tools <using_the_cli>`, although I have gotten *very* far by using them. The structure of the API consists of a singleton_ that contains all the GIS_, full COVID-19 state of all counties in the US, and necessary configuration data. :numref:`figure_of_api_flow` describes the implementation flow of synthesizing COVID-19 summary data.

.. _figure_of_api_flow:

.. figure:: figures/covid19_stats_api_covid19database_singleton.png
   :width: 100%
   :align: left

   :py:class:`COVID19Database <covid19_stats.COVID19Database>` is the singleton_ that contains US GIS_ data, and trends of cumulative COVID-19 cases and deaths for *all* counties and atomic territorial units within the United States. It is somewhat-lazily instantiated by GIS_ functionality that lives in :py:mod:`gis <covid19_stats.engine.gis>`, and is in turn called by utility methods in :py:mod:`core <covid19_stats.engine.core>`.

Subsequent subsections describe each of the main modules, with special emphasis given to :py:class:`COVID19Database <covid19_stats.COVID19Database>` due to its integral role.

.. toctree::
   :maxdepth: 3

   covid19_stats_api
   covid19_stats_engine_api
   covid19_stats_engine_gis_api
   covid19_stats_engine_core_api
   covid19_stats_engine_viz_api
   covid19_stats_engine_viz2_api
