#!/usr/bin/env python3

import os, sys, numpy, engine, defaults

datas = [ defaults.bay_area_data, defaults.richmond_metro_data, defaults.nyc_data,
         { 'prefix' : 'us', 'region name' : 'All US',
          'counties' : engine.all_counties_state } ]
list(map(lambda dat: engine.get_summary_demo_data( data = dat, doShow = False ), datas ) )
