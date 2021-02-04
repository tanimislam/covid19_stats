RESOURCES
===========
The ``resources`` subfolder consists of US census shapefile data, taken from `this URL <https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html>`_. The exploded ZIP archive of US counties was downloaded on 15 APRIL 2020 from `cb_2018_us_county_500k.zip <https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_county_500k.zip>`_. The FIPS data processed from the SHP files is stored in :download:`resources/fips_2018_data.pkl.gz </_static/fips_2018_data.pkl.gz>`.

I also want to find *recent* data that organizes counties (by FIPS code) into metropolitan areas. I was able to find the Excel spreadsheet of the `2019 metropolitan statistical areas <https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/metro/totals/cbsa-est2019-alldata.csv>`_. I have downloaded this Excel spreadsheet in :download:`resources/msa_2019.csv </_static/msa_2019.csv>`, and the Excel spreadsheet version :download:`resources/msa_2019.xlsx </_static/msa_2019.xlsx>`.

Finally, the file :download:`resources/README_template.rst </_static/README_template.rst>` is a template file that ``covid19_update_readme`` uses to *regenerate* the top-level ``README.rst``.
