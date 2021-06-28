.. _getting_started:

GETTING STARTED
=================
Here's how to install this repository, and to create COVID-19 case and death movies and figures for the United States as a whole, and specific regions inside it. Mentions of ``python3.7`` are specific to the installation environment of one of `Tanim Islam's <tanim_islam_>`_ machines, *and should not be taken as universal*.

#. First clone this repo using the command,

   .. code-block:: console
		   
      git clone https://github.com/tanimislam/covid19_stats.git

#. You will get the main directory structure, but you will notice that the ``covid19_stats/covid-19-data`` submodule is empty. To populate it, run

   .. code-block:: console

      git submodule update --init --recursive --progress

#. The requirements are in the ``requirements.txt``. You should be able to install these Python packages into your *user* Python library (typically at ``~/.local/lib/python3.X/site-packages``) by running,

   .. code-block:: console

      pip install -r requirements.txt
      pip install --user -e .

   Of course, if you feel adventurous, you can install all-in-one-go by doing this,

   .. code-block:: console

      pip install --user git+https://github.com/tanimislam/covid19_stats.git#egginfo=covid19_stats

.. note::

   If you are running the Anaconda_ Python distribution, I suggest you do this before step #3.

   .. code-block:: console

      conda install --channel conda-forge cartopy mpi4mpy openmpi

   These will install not only those Python modules, Cartopy and mpi4py, but also the lower-level libraries on which those module
      
.. _tanim_islam: https://tanimislam.github.io
.. _Anaconda: https://www.anaconda.com
