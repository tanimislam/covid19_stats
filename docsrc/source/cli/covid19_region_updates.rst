.. include:: cli_urls.rst

.. _covid19_region_updates:

covid19_region_updates
=======================
This CLI is designed to create 19 summary files for a specific region defined by an input region file, such as :download:`brhd.json <examples/brhd.json>`. It can use machines that have MPI_ through the mpi4py_ Python module to parallelize the process of creating summary movies and figures for that region. It is similar underneath the hood to the API calls that, e.g., :ref:`covid19_movie_updates` uses.

Its help output, when running ``covid19_region_updates -h``, is the following,

.. code-block:: console

   usage: covid19_region_updates [-h] -r region [-d DIRNAME] [-i]

   optional arguments:
     -h, --help            show this help message and exit
     -r region, --region region
			   region as JSON file.
     -d DIRNAME, --dirname DIRNAME
			   The name of the directory to which to put all this stuff. Default is XXXX.
     -i, --info            If chosen, then turn on INFO logging.

Here are the command line flags.

* ``-r`` or ``--region`` is the geographical region JSON_ file, such as :download:`brhd.json <examples/brhd.json>` as described in :ref:`covid19_create_region`.

* ``-d`` or ``--dirname`` is the directory into which to dump the output files. By default, if unspecified, dumps into the current working directory.

* ``-i`` or ``--info`` turns on INFO level logging. This is useful to see what sort of output this CLI produces.

If you have access to a powerful supercomputer, I invite you try this out!

.. code-block:: console

   srun -N4 covid19_region_updates -r brhd.json -i

This will use 4 nodes on a supercomputing machine to generate the *latest* summary data on the `Blue Ridge Health District <brhd_>`_.
