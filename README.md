# README

[comment]: <> (Markdown internal anchors are hard because there is no spec. Only documentation that make it explicit is here: https://dev.to/stephencweiss/named-anchors-markdown-2hm5)

Hello world! This is my COVID-19 tracker. There is a git submodule, the [NY Times COVID-19 repository](https://github.com/nytimes/covid-19-data), that needs to be updated frequently to get the latest data. The easiest way to update is to run this command in the checked out repo,
```bash
git -C covid-19-data pull origin master
```
This is not nearly as sophisticated as what's in [ncov2019.live](https://ncov2019.live), and described in [this New Yorker article](https://www.newyorker.com/magazine/2020/03/30/the-high-schooler-who-became-a-covid-19-watchdog).

I have made major changes in the functionality and implementation from the original commits, since commit [#78917](https://github.com/tanimislam/covid19_stats/commit/78917dd20c43bd65320cf51958fa481febef4338) for instance.

* The API code has been refactored into the ``engine`` subdirectory, and is divided into three main submodules: ``engine.core`` provides the higher level API calls for processing the COVID-19 data; ``engine.gis`` provides the lower-level APIs to write out, read in, and process the raw GIS data provided mainly by the US Census Bureau; and ``engine.viz`` does the visualization part.

* There is a single command line interface (CLI), ``covid19_create_movie_or_summary.py``, that can do the following: summarizes US metropolitan statistical areas (MSA) and gives their latest COVID-19 statistics; makes movie animations of the COVID-19 cases and deaths, from first case to latest incident date, for a given MSA; and prints out summary plots, and incident data, of COVID-19 cases and deaths for the latest incident day.

* The ``testing`` subdirectory contains [Jupyter Notebooks](https://jupyter.org) that illuminate bits and pieces of this COVID-19 tracker's functionality.

* Some video output of the CLI is located in the ``movies`` subdirectory.

Here is some output from using this COVID-19 tracker.

* The summary of COVID-19 statistics for the top 50 MSAs by estimated 2019 population.

	|   RANK | IDENTIFIER       | NAME                                   | POPULATION   | FIRST INC.       |   NUM DAYS | NUM CASES   | NUM DEATHS   | MAX CASE COUNTY   | MAX CASE COUNTY NAME                 |
	|:-------|:-----------------|:---------------------------------------|:-------------|:-----------------|:-----------|:------------|:-------------|:------------------|:-------------------------------------|
	|      1 | nyc              | NYC Metro Area                         | 19,216,182   | 01 March 2020    |         62 | 393,715     | 24,909       | 172,364           | New York City, New York              |
	|      2 | losangeles       | LA Metro Area                          | 18,711,436   | 25 January 2020  |         98 | 34,459      | 1,545        | 24,894            | Los Angeles County, California       |
	|      3 | chicago          | Chicago Metro Area                     | 9,458,539    | 24 January 2020  |         99 | 56,230      | 2,466        | 40,227            | Cook County, Illinois                |
	|      4 | dallas           | Dallas Metro Area                      | 7,573,136    | 09 March 2020    |         54 | 8,522       | 243          | 3,899             | Dallas County, Texas                 |
	|      5 | houston          | Houston Metro Area                     | 7,066,141    | 04 March 2020    |         59 | 9,780       | 204          | 6,708             | Harris County, Texas                 |
	|      6 | bayarea          | Bay Area                               | 6,860,207    | 31 January 2020  |         92 | 8,013       | 304          | 2,204             | Santa Clara County, California       |
	|      7 | dc               | DC Metro Area                          | 6,280,487    | 05 March 2020    |         58 | 28,572      | 1,149        | 7,041             | Prince George's County, Maryland     |
	|      8 | miami            | Miami Metro Area                       | 6,166,488    | 06 March 2020    |         57 | 20,966      | 766          | 12,631            | Miami-Dade County, Florida           |
	|      9 | philadelphia     | Philadelphia Metro Area                | 6,102,434    | 06 March 2020    |         57 | 39,149      | 2,136        | 15,527            | Philadelphia County, Pennsylvania    |
	|     10 | atlanta          | Atlanta Metro Area                     | 6,020,364    | 02 March 2020    |         61 | 13,860      | 530          | 2,928             | Fulton County, Georgia               |
	|     11 | phoenix          | Phoenix Metro Area                     | 4,948,203    | 26 January 2020  |         97 | 4,856       | 172          | 4,421             | Maricopa County, Arizona             |
	|     12 | boston           | Boston Metro Area                      | 4,873,019    | 01 February 2020 |         91 | 50,589      | 2,859        | 15,048            | Middlesex County, Massachusetts      |
	|     13 | detroit          | Detroit Metro Area                     | 4,319,629    | 10 March 2020    |         53 | 31,106      | 3,320        | 17,106            | Wayne County, Michigan               |
	|     14 | seattle          | Seattle Metro Area                     | 3,979,845    | 21 January 2020  |        102 | 10,489      | 616          | 6,507             | King County, Washington              |
	|     15 | minneapolis      | Minneapolis Metro Area                 | 3,640,043    | 06 March 2020    |         57 | 3,271       | 331          | 1,980             | Hennepin County, Minnesota           |
	|     16 | sandiego         | San Diego Metro Area                   | 3,338,330    | 10 February 2020 |         82 | 3,905       | 150          | 3,905             | San Diego County, California         |
	|     17 | tampa            | Tampa Metro Area                       | 3,194,831    | 01 March 2020    |         62 | 2,364       | 78           | 1,240             | Hillsborough County, Florida         |
	|     18 | denver           | Denver Metro Area                      | 2,967,239    | 05 March 2020    |         58 | 9,701       | 503          | 3,222             | Denver County, Colorado              |
	|     19 | stlouis          | St. Louis Metro Area                   | 2,803,228    | 07 March 2020    |         56 | 6,555       | 376          | 3,244             | St. Louis County, Missouri           |
	|     20 | baltimore        | Baltimore Metro Area                   | 2,800,053    | 08 March 2020    |         55 | 9,241       | 424          | 3,183             | Baltimore County, Maryland           |
	|     21 | charlotte        | Charlotte Metro Area                   | 2,636,883    | 11 March 2020    |         52 | 3,326       | 113          | 1,699             | Mecklenburg County, North Carolina   |
	|     22 | orlando          | Orlando Metro Area                     | 2,608,147    | 12 March 2020    |         51 | 2,554       | 63           | 1,421             | Orange County, Florida               |
	|     23 | sanantonio       | San Antonio Metro Area                 | 2,550,960    | 12 February 2020 |         80 | 1,822       | 60           | 1,585             | Bexar County, Texas                  |
	|     24 | portland         | Portland Metro Area                    | 2,492,412    | 28 February 2020 |         64 | 1,884       | 92           | 734               | Multnomah County, Oregon             |
	|     25 | sacramento       | Sacramento Metro Area                  | 2,363,730    | 21 February 2020 |         71 | 1,483       | 69           | 1,106             | Sacramento County, California        |
	|     26 | pittsburgh       | Pittsburgh Metro Area                  | 2,317,600    | 13 March 2020    |         50 | 2,596       | 214          | 1,333             | Allegheny County, Pennsylvania       |
	|     27 | lasvegas         | Las Vegas Metro Area                   | 2,266,715    | 05 March 2020    |         58 | 4,225       | 215          | 4,225             | Clark County, Nevada                 |
	|     28 | austin           | Austin Metro Area                      | 2,227,083    | 13 March 2020    |         50 | 2,297       | 64           | 1,714             | Travis County, Texas                 |
	|     29 | cincinnati       | Cincinnati Metro Area                  | 2,221,208    | 14 March 2020    |         49 | 2,742       | 149          | 1,353             | Hamilton County, Ohio                |
	|     30 | kansascity       | Kansas City Metro Area                 | 2,157,990    | 07 March 2020    |         56 | 2,229       | 124          | 762               | Wyandotte County, Kansas             |
	|     31 | columbus         | Columbus Metro Area                    | 2,122,271    | 14 March 2020    |         49 | 5,045       | 116          | 2,698             | Franklin County, Ohio                |
	|     32 | indianapolis     | Indianapolis Metro Area                | 2,074,537    | 06 March 2020    |         57 | 9,533       | 642          | 5,983             | Marion County, Indiana               |
	|     33 | cleveland        | Cleveland Metro Area                   | 2,048,449    | 09 March 2020    |         54 | 3,286       | 184          | 2,305             | Cuyahoga County, Ohio                |
	|     34 | nashville        | Nashville Metro Area                   | 1,934,317    | 05 March 2020    |         58 | 6,577       | 106          | 2,875             | Davidson County, Tennessee           |
	|     35 | virginiabeach    | Virginia Beach Metro Area              | 1,768,901    | 09 March 2020    |         54 | 2,008       | 77           | 413               | Virginia Beach city, Virginia        |
	|     36 | providence       | Providence Metro Area                  | 1,624,578    | 14 March 2020    |         49 | 12,063      | 334          | 6,822             | Providence County, Rhode Island      |
	|     37 | milwaukee        | Milwaukee Metro Area                   | 1,575,179    | 11 March 2020    |         52 | 3,692       | 224          | 3,147             | Milwaukee County, Wisconsin          |
	|     38 | jacksonville     | Jacksonville Metro Area                | 1,559,514    | 10 March 2020    |         53 | 1,608       | 49           | 1,038             | Duval County, Florida                |
	|     39 | oklahomacity     | Oklahoma City Metro Area               | 1,408,950    | 13 March 2020    |         50 | 1,492       | 71           | 822               | Oklahoma County, Oklahoma            |
	|     40 | raleigh          | Raleigh Metro Area                     | 1,390,785    | 03 March 2020    |         60 | 1,136       | 53           | 870               | Wake County, North Carolina          |
	|     41 | memphis          | Memphis Metro Area                     | 1,346,045    | 08 March 2020    |         55 | 3,438       | 69           | 2,672             | Shelby County, Tennessee             |
	|     42 | richmond         | Richmond Metro Area                    | 1,291,900    | 12 March 2020    |         51 | 2,393       | 171          | 926               | Henrico County, Virginia             |
	|     43 | neworleans       | New Orleans Metro Area                 | 1,270,530    | 09 March 2020    |         54 | 16,457      | 1,088        | 6,524             | Orleans Parish, Louisiana            |
	|     44 | louisville       | Louisville/Jefferson County Metro Area | 1,265,108    | 08 March 2020    |         55 | 2,211       | 142          | 1,365             | Jefferson County, Kentucky           |
	|     45 | saltlakecity     | Salt Lake City Metro Area              | 1,232,696    | 25 February 2020 |         67 | 2,678       | 30           | 2,609             | Salt Lake County, Utah               |
	|     46 | hartford         | Hartford Metro Area                    | 1,204,877    | 14 March 2020    |         49 | 7,280       | 871          | 6,112             | Hartford County, Connecticut         |
	|     47 | buffalo          | Buffalo Metro Area                     | 1,127,983    | 15 March 2020    |         48 | 4,055       | 257          | 3,598             | Erie County, New York                |
	|     48 | birmingham       | Birmingham Metro Area                  | 1,090,435    | 13 March 2020    |         50 | 1,479       | 62           | 946               | Jefferson County, Alabama            |
	|     49 | grandrapids      | Grand Rapids Metro Area                | 1,077,370    | 12 March 2020    |         51 | 2,090       | 51           | 1,697             | Kent County, Michigan                |
	|     50 | rochester        | Rochester Metro Area                   | 1,069,644    | 11 March 2020    |         52 | 1,886       | 109          | 1,534             | Monroe County, New York              |

	
* The COVID-19 trends in cases and deaths for these 6 metropolitan areas through 20 APRIL 2020: SF Bay Area; Washington, DC; Richmond, VA; NYC; Los Angeles; and New Orleans.

	| | | |
	|:---------------------------------------------------------------:|:------------------------------------------------------------------:|:------------------------------------------------------------------:|
	| <img width=100% src="figures/covid19_bayarea_cds_20042020.png"> | <img width=100% src="figures/covid19_dc_cds_20042020.png">         | <img width=100% src="figures/covid19_richmond_cds_20042020.png">   |
	| SF Bay Area                                                     | Washington, DC                                                     | Richmond, VA                                                       |
	| <img width=100% src="figures/covid19_nyc_cds_20042020.png">     | <img width=100% src="figures/covid19_losangeles_cds_20042020.png"> | <img width=100% src="figures/covid19_neworleans_cds_20042020.png"> |
	| NYC Metro                                                       | Los Angeles                                                        | New Orleans                                                        |


* <a id="gif-animations"></a>GIF'd video animations of the COVID-19 trends in cases/deaths for NYC, Chicago, and Seattle up to 2 MAY 2020.

	| | | |
	|:---------------------------------------------------------------:|:------------------------------------------------------------------:|:------------------------------------------------------------------:|
	| <img width=100% src="figures/covid19_nyc_latest.gif">           | <img width=100% src="figures/covid19_chicago_latest.gif">          | <img width=100% src="figures/covid19_seattle_latest.gif">          | 
	| NYC Metro                                                       | Chicago                                                            | Seattle                                                            |

  And here is the animation for the continental United States, up to 4 MAY 2020.
  
    |                                                          |
	|:--------------------------------------------------------:|
	| <img width=100% src="figures/covid19_conus_latest.gif">  |
	| Continental United States

The remainder of this README has two sections: [*GETTING STARTED*](#getting-started) and [*USING THE CLI*](#using-cli).

## <a id="getting-started"></a> GETTING STARTED

First clone this repo using the command
```bash
git clone https://github.com/tanimislam/covid19_stats.git
```
You will get the main directory structure, but you will notice that the ``covid-19-data`` submodule is empty. To populate it, run
```bash
git submodule update --init --recursive
```
The requirements are in the ``requirements.txt``. You should be able to install these Python packages into your *user* Python library (typically at ``~/.local/lib/python3.X/site-packages``) by running,
```bash
pip install -r requirements.txt
```
However, [Basemap](https://matplotlib.org/basemap/) can be a bugbear to install. Here is what worked for me when installing on the Linux machine.

1. First, although [Basemap](https://matplotlib.org/basemap/) will install, your Python shell (and hence your CLI) won't be able to find it. This is almost certainly a bug in Basemap. Running ``from mpl_toolkits.basemap import Basemap`` won't work. First, look for where ``basemap`` is installed. In my case, it was located at ``~/.local/lib/python3.7/site-packages/basemap-1.2.1-py3.7-linux-x86_64.egg/``. The directory structure right below it looks like this,
     ```bash
	 EGG-INFO  _geoslib.cpython-37m-x86_64-linux-gnu.so  _geoslib.py  mpl_toolkits  __pycache__
	 ```

2. ``cd`` into ``mpl_toolkits``. You should see a ``basemap`` subdirectory when you look in it.
     ```bash
	 basemap  __init__.py  __pycache__
	 ```

3. You should also have an ``mpl_toolkits`` library module installed locally. In my case it was ``~/.local/lib/python3.7/site-packages/mpl_toolkits/``. Inside it looks like,
     ```bash
	 axes_grid  axes_grid1  axisartist  mplot3d  tests
	 ```

4. In the real ``mpl_toolkits`` directory, make a symbolic link to the ``basemap`` directory underneath, e.g., ``~/.local/lib/python3.7/site-packages/basemap-1.2.1-py3.7-linux-x86_64.egg/``. Thus in the correct ``mpl_toolkits`` subdirectory, run, e.g.,
     ```bash
	 ln -sf ~/.local/lib/python3.7/site-packages/basemap-1.2.1-py3.7-linux-x86_64.egg/mpl_toolkits/basemap basemap
	 ```

   If you have done everything correctly, its data structure will look like what is shown below, with a valid symbolic link to ``basemap``.
     ```bash
	 axes_grid
	 axes_grid1
	 axisartist
	 basemap -> ~/.local/lib/python3.7/site-packages/basemap-1.2.1-py3.7-linux-x86_64.egg/
	 mplot3d
	 tests
	 ```

If you're lucky, running ``from mpl_toolkits.basemap import Basemap`` will work without further issues.

### <a id="subsec-updating-data"></a> Updating the COVID-19 Database

Just run this from the main directory,
```bash 
git -C covid-19-data pull origin master
```
in order to get the latest COVID-19 data.

## <a id="using-cli"></a> USING THE CLI

``covid19_create_movie_or_summary.py`` is the only top-level CLI currently in the repository. It has three modes of operation. Its help output, while running ``covid19_create_movie_or_summary.py -h``, produces the following,
```bash
usage: covid19_create_movie_or_summary.py [-h] {M,m,s} ...

positional arguments:
  {M,m,s}     Choose either showing list of metros, or make a movie of a metro
              region
    M         If chosen, then list all the metropolitan areas through which we
              can look.
    m         Make a movie of the COVID-19 cases and deaths trend for the
              specific Metropolitan Statistical Area (MSA).
    s         Make a summary plot, and incident data file, of COVID-19 cases
              and deaths trend, for the specific Metropolitan Statistical Area
              (MSA).

optional arguments:
  -h, --help  show this help message and exit
```

* <a id="metro-mode"></a>``covid19_create_movie_or_summary.py M`` (METRO flag) lists the COVID-19 stats for all, or user-selected, metropolitan statistical areas (MSAs) by population. For example, here are the statistics for the top 30 MSAs.
	```bash
	covid19_create_movie_or_summary.py M
	
	HERE ARE THE 380 METRO AREAS, ORDERED BY POPULATION
	DATA AS OF 24 April 2020.
	  RANK  IDENTIFIER        NAME                                    POPULATION    FIRST INC.          NUM DAYS  NUM CASES    NUM DEATHS    MAX CASE COUNTY    MAX CASE COUNTY NAME
	------  ----------------  --------------------------------------  ------------  ----------------  ----------  -----------  ------------  -----------------  ------------------------------------
		 1  nyc               NYC Metro Area                          19,216,182    01 March 2020             54  342,209      20,541        150,484            New York City, New York
		 2  losangeles        LA Metro Area                           18,711,436    25 January 2020           90  25,847       1,094         18,545             Los Angeles County, California
		 3  chicago           Chicago Metro Area                      9,458,539     24 January 2020           91  38,306       1,728         27,616             Cook County, Illinois
		 4  dallas            Dallas Metro Area                       7,573,136     09 March 2020             46  6,207        169           2,834              Dallas County, Texas
		 5  houston           Houston Metro Area                      7,066,141     04 March 2020             51  7,937        138           5,482              Harris County, Texas
		 6  bayarea           Bay Area                                6,860,207     31 January 2020           84  6,875        249           2,018              Santa Clara County, California
		 7  dc                DC Metro Area                           6,280,487     05 March 2020             50  18,782       675           4,403              Prince George's County, Maryland
		 8  miami             Miami Metro Area                        6,166,488     06 March 2020             49  18,114       604           10,925             Miami-Dade County, Florida
		 9  philadelphia      Philadelphia Metro Area                 6,102,434     06 March 2020             49  29,605       1,273         11,877             Philadelphia County, Pennsylvania
		10  atlanta           Atlanta Metro Area                      6,020,364     02 March 2020             53  11,054       395           2,500              Fulton County, Georgia
		11  phoenix           Phoenix Metro Area                      4,948,203     26 January 2020           89  3,433        129           3,116              Maricopa County, Arizona
		12  boston            Boston Metro Area                       4,873,019     01 February 2020          83  39,079       1,859         11,681             Middlesex County, Massachusetts
		13  detroit           Detroit Metro Area                      4,319,629     10 March 2020             45  28,002       2,582         15,407             Wayne County, Michigan
		14  seattle           Seattle Metro Area                      3,979,845     21 January 2020           94  9,251        542           5,691              King County, Washington
		15  minneapolis       Minneapolis Metro Area                  3,640,043     06 March 2020             49  1,981        176           1,200              Hennepin County, Minnesota
		16  sandiego          San Diego Metro Area                    3,338,330     10 February 2020          74  2,826        112           2,826              San Diego County, California
		17  tampa             Tampa Metro Area                        3,194,831     01 March 2020             54  2,011        52            1,022              Hillsborough County, Florida
		18  denver            Denver Metro Area                       2,967,239     05 March 2020             50  7,412        399           2,385              Denver County, Colorado
		19  stlouis           St. Louis Metro Area                    2,803,228     07 March 2020             48  5,285        248           2,625              St. Louis County, Missouri
		20  baltimore         Baltimore Metro Area                    2,800,053     08 March 2020             47  6,681        250           2,234              Baltimore County, Maryland
		21  charlotte         Charlotte Metro Area                    2,636,883     11 March 2020             44  2,700        76            1,407              Mecklenburg County, North Carolina
		22  orlando           Orlando Metro Area                      2,608,147     12 March 2020             43  2,317        54            1,289              Orange County, Florida
		23  sanantonio        San Antonio Metro Area                  2,550,960     12 February 2020          72  1,393        54            1,206              Bexar County, Texas
		24  portland          Portland Metro Area                     2,492,412     28 February 2020          56  1,616        74            596                Multnomah County, Oregon
		25  sacramento        Sacramento Metro Area                   2,363,730     21 February 2020          63  1,357        62            1,019              Sacramento County, California
		26  pittsburgh        Pittsburgh Metro Area                   2,317,600     13 March 2020             42  2,213        160           1,177              Allegheny County, Pennsylvania
		27  lasvegas          Las Vegas Metro Area                    2,266,715     05 March 2020             50  3,443        168           3,443              Clark County, Nevada
		28  austin            Austin Metro Area                       2,227,083     13 March 2020             42  1,800        40            1,379              Travis County, Texas
		29  cincinnati        Cincinnati Metro Area                   2,221,208     14 March 2020             41  1,956        108           932                Hamilton County, Ohio
		30  kansascity        Kansas City Metro Area                  2,157,990     07 March 2020             48  1,617        110           527                Wyandotte County, Kansas
	```
	
	One can also select MSAs with the ``--metros`` flag. The ``-f`` or ``--format`` flag prints out a table of MSAs formatted in one of three ways: ``simple``, the default, is the tabular format shown above; ``github`` is [Github flavored Markdown](https://github.github.com/gfm/); and ``rst`` is [reStructuredText](https://docutils.sourceforge.io/rst.html). This is described in the help output, produced by ``covid19_create_movie_or_summary.py M -h``,
	```bash
	usage: covid19_create_movie_or_summary.py M [-h] [-f {simple,github,rst}]
                                            [--metros METROS]
												
	optional arguments:
	  -h, --help            show this help message and exit
	  -f {simple,github,rst}, --format {simple,github,rst}
							Format of the table that displays MSA summary. Default
							is "simple".
	  --metros METROS       If chosen, list of selected metros for which to
							summarize COVID-19 data.
	```

* <a id="show-mode"></a>``covid19_create_movie_or_summary.py s`` (SHOW flag) summarizes the latest COVID-19 statistics for a specified MSA. The help output, while running ``covid19_create_movie_or_summary.py s -h``, is shown below,
    ```bash
	usage: covid19_create_movie_or_summary.py s [-h] [-n NAME] [-M MAXNUM] [-y]

	optional arguments:
	  -h, --help            show this help message and exit
	  -n NAME, --name NAME  Create a summary plot and incident data file of this
							metropolitan area. Default is "bayarea".
	  -M MAXNUM, --maxnum MAXNUM
							The limit of cases/deaths to visualize. Default is
							5,000. You should use a limit larger (by at least 2,
							no more than 10) than the maximum number of cases
							recorded for a county in that MSA.
	  -y, --yes             If chosen, then do not confirm --maxnum.
    ```

    The required ``-n`` or ``--name`` flag specifies the MSA. The ``-M`` or ``--maxnum`` sets the color limits of cases and deaths to this number (the default is 5000); and the ``-y`` or ``--yes`` flag suppresses the intermediate prompt that asks the user whether the specified or default maximum number is sufficient. For example, for the NYC metro area,
	```bash
	covid19_create_movie_or_summary.py s -n nyc
	HERE ARE DETAILS FOR NYC Metro Area.
	2019 EST. POP = 19,216,182.
	FIRST CASE:  01 March 2020.
	LATEST CASE: 24 April 2020 (54 days after first case)
	MAXIMUM NUMBER OF CASES: 150,484 (in New York City, New York)
	MAXIMUM NUMBER OF CASES FOR VISUALIZATION: 5,000.
	CONTINUE (must choose one) [y/n]:
	```
	
	The maximum number of cases and deaths for visualization is 5000, whereas the county with the most cases has over 150k; coloring of cases and deaths by counties is insufficient to visually resolve the absolute and relative time trend of cases and deaths in ``New York City``. Here, I would suggest running ``covid19_create_movie_or_summary.py s -n nyc -M 200000`` to get sufficient contrast.
	
	This mode of operation, for example for NYC will output the following seven files:
	
	* ``covid19_nyc_23042020.pkl.gz`` is the [Pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) of the COVID-19 cases and deaths, total and per county, from the date of first incident to the latest incident.
	
	* ``covid19_nyc_cds_23042020.pdf`` and ``covid19_nyc_cds_23042020.png`` are the PDF and PNG showing the trend of COVID-19 cases and deaths in the NYC metro area.
	
	* ``covid19_nyc_cases_23042020.pdf`` and ``covid19_nyc_cases_23042020.png`` are the PDF and PNG showing the county map, colored by number of COVID-19 cases, on the LAST incident day.
	
	* ``covid19_nyc_death_23042020.pdf`` and ``covid19_nyc_death_23042020.png`` are the PDF and PNG showing the county map, colored by number of COVID-19 deaths, on the LAST incident day.


* <a id="movie-mode"></a>``covid19_create_movie_or_summary.py m`` (MOVIE flag) creates an [MP4](https://en.wikipedia.org/wiki/MPEG-4_Part_14) movie of COVID-19 cases and deaths for the MSA you specify (see the [high quality GIF animations](#gif-animations) of these MP4 movies). The help output, while running ``covid19_create_movie_or_summary.py m -h``, is shown below,
    ```bash
	usage: covid19_create_movie_or_summary.py m [-h] [-n NAME] [-M MAXNUM] [-y]

	optional arguments:
	  -h, --help            show this help message and exit
	  -n NAME, --name NAME  Make a movie of this metropolitan area. Default is
							"bayarea"
	  -M MAXNUM, --maxnum MAXNUM
							The limit of cases/deaths to visualize. Default is
							5,000. You should use a limit larger (by at least 2,
							no more than 10) than the maximum number of cases
							recorded for a county in that MSA.
	  -y, --yes             If chosen, then do not confirm --maxnum.
	```
	The meaning of the ``-M`` and ``-y`` flags are the same as in [SHOW mode](#show-mode).
