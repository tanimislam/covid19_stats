.. include:: cli_urls.rst

.. _covid19_update_database:
	     
covid19_update_database
=========================
This CLI updates the git submodule (the `NY Times COVID-19 repository`_) with the *latest* data. Previously, one updated the database by manually running, from the repository's top level directory,

  .. code-block:: console

     git -C covid19_stats/covid-19-data pull origin master
