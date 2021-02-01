Welcome to the COVID19_STATS repository
=========================================

.. include:: ../../README.rst

.. _getting_started:

GETTING STARTED
-------------------
First clone this repo using the command,

.. code-block:: console

   git clone https://github.com/tanimislam/covid19_stats.git

You will get the main directory structure, but you will notice that the ``covid19_stats/covid-19-data`` submodule is empty. To populate it, run

.. code-block:: console

   git submodule update --init --recursive

The requirements are in the ``requirements.txt``. You should be able to install these Python packages into your *user* Python library (typically at ``~/.local/lib/python3.X/site-packages``) by running,

.. code-block:: console

   pip install -r requirements.txt
   pip install --user -e .

Of course, if you feel adventurous, you can install all-in-one-go by doing this,

.. code-block:: console

   pip install --user git+https://github.com/tanimislam/covid19_stats.git#egginfo=covid19_stats
   
However, `Basemap <https://matplotlib.org/basemap/>`__ can be a bugbear to install. Here is what worked for me when installing on the Linux machine.

1. First, although Basemap_ will install, your Python shell (and hence your CLI) won’t be able to find it. This is almost certainly a bug in Basemap. Running ``from mpl_toolkits.basemap import Basemap`` won’t work. First, look for where ``basemap`` is installed. In my case, it was located at ``~/.local/lib/python3.7/site-packages/basemap-1.2.1-py3.7-linux-x86_64.egg/``. The directory structure right below it looks like this,

   .. code-block:: console

      EGG-INFO
      _geoslib.cpython-37m-x86_64-linux-gnu.so
      _geoslib.py
      mpl_toolkits
      __pycache__

2. ``cd`` into ``mpl_toolkits``. You should see a ``basemap`` subdirectory when you look in it.

   .. code-block:: console

      basemap
      __init__.py
      __pycache__

3. You should also have an ``mpl_toolkits`` library module installed locally. In my case it was ``~/.local/lib/python3.7/site-packages/mpl_toolkits/``. Inside it looks like,

   .. code-block:: console

      axes_grid
      axes_grid1
      axisartist
      mplot3d
      tests

4. In the real ``mpl_toolkits`` directory, make a symbolic link to the ``basemap`` directory underneath, e.g., ``~/.local/lib/python3.7/site-packages/basemap-1.2.1-py3.7-linux-x86_64.egg/``. Thus in the correct ``mpl_toolkits`` subdirectory, run, e.g.,

   .. code-block:: console

      ln -sf ~/.local/lib/python3.7/site-packages/basemap-1.2.1-py3.7-linux-x86_64.egg/mpl_toolkits/basemap basemap

   If you have done everything correctly, its data structure will look like what is shown below, with a valid symbolic link to ``basemap``.

   .. code-block:: console

      axes_grid
      axes_grid1
      axisartist
      basemap -> ~/.local/lib/python3.7/site-packages/basemap-1.2.1-py3.7-linux-x86_64.egg/
      mplot3d
      tests

If you’re lucky, running ``from mpl_toolkits.basemap import Basemap`` will work without further issues.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :numbered:

   cli


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
