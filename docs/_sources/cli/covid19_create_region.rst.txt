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

Best to show-by-example, where I am creating the `Blue Ridge Health District <brhd_>`_ (consisting of six counties) geographical region like so,

.. code-block::

  covid19_create_region \
    -c Charlottesville Albemarle Nelson Greene Louisa Fluvanna \
    -s Virginia -p brhd \
    -n "Blue Ridge Health District"

Here's the flow of the CLI with confirmation prompt.
    
It prompts for whether the list of counties look acceptable. If you chose ``y`` to the list of counties, this creates a geographical region file, :download:`brhd.json <examples/brhd.json>`.

.. literalinclude:: examples/brhd.json
   :language: json

This should look pretty similar to the Python dictionary of geographical data for `St. Louis <https://en.wikipedia.org/wiki/Greater_St._Louis>`_ I show in :py:meth:`create_and_store_msas_and_fips_2019 <covid19_stats.engine.gis.create_and_store_msas_and_fips_2019>`. In the :download:`brhd.json <examples/brhd.json>` dictionary are keys for the ``prefix``, the ``region name``, ``fips`` is a list of FIPS codes for its six counties, and ``population`` is its census-d population.
