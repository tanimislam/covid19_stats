.. include:: cli_urls.rst

.. _covid19_create_region:

covid19_create_region
======================
This CLI is designed to create a custom geographical region, consisting of multiple counties, in a single state or US territory.

It has an associated CLI front-end, :ref:`covid19_region_updates`, that creates the latest COVID-19 summary of that region. Its help output, when running ``covid19_create_region -h``, is the following,

.. code-block:: console

   usage: covid19_create_region [-h] -c [COUNTIES [COUNTIES ...]] -s STATE -p PREFIX -n NAME

   optional arguments:
     -h, --help            show this help message and exit
     -c [COUNTIES [COUNTIES ...]], --counties [COUNTIES [COUNTIES ...]]
			   List of counties (all in a single state) out of which to create a geographical region.
     -s STATE, --state STATE
			   The single state from which to create a geographical region.
     -p PREFIX, --prefix PREFIX
			   The prefix of the geographical region. Must be a single word.
     -n NAME, --name NAME  Name of the geographical region.

Given a list of counties, the state, and the name of the geographical region, it spits out a JSON_ region file that :ref:`covid19_region_updates` can understand. Here are what the separate flags mean:

* ``-c`` or ``--counties`` specify the separate counties in this region.

* ``-s`` of ``--state`` specifies the state in which these counties reside.

* ``-p`` or ``--prefix`` is the prefix name of the underlying JSON_ file.
