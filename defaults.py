import os, sys, numpy
from itertools import chain

def get_county_state_tuples( metro_area ):
    return list(chain.from_iterable(map(lambda state: map(lambda county: { 'county' : county, 'state' : state }, metro_area[ state ] ),
                                        metro_area ) ) )

#
## these are the 9 Bay Area counties
## gotten from https://mtc.ca.gov/about-mtc/what-mtc/nine-bay-area-counties
_bay_area_counties = {
    'California' : {
        "Alameda",
        "Contra Costa",
        "Marin",
        "Napa",
        "San Francisco",
        "San Mateo",
        "Santa Clara",
        "Solano",
        "Sonoma" } }

bay_area_data = {
    'prefix' : 'bayarea',
    'region name' : 'SF Bay Area',
    'counties' : get_county_state_tuples( _bay_area_counties )
    }

#
## these are the cities and counties in the Richmond, VA, metro area
## gotten from https://en.wikipedia.org/wiki/Greater_Richmond_Region
_richmond_metro_counties = {
    'Virginia' : {
        "Richmond",
        "Petersburg",
        "Hopewell",
        "Colonial Heights",
        "Amelia",
        "Caroline",
        "Charles City",
        "Chesterfield",
        "Dinwiddie",
        "Goochland",
        "Hanover",
        "Henrico",
        "King William",
        "New Kent",
        "Powhatan",
        "Prince George",
        "Sussex"
    } }

richmond_metro_data = {
    'prefix' : 'richmond',
    'region name' : 'Richmond Metropolitan Area',
    'counties' : get_county_state_tuples( _richmond_metro_counties ) }
    
dc_data = {
    'prefix' : 'dc',
    'region name' : 'Washington DC',
    'counties' : [ { 'county' : 'District of Columbia', 'state' : 'District of Columbia' } ] }

#
## these are the counties in the NYC metro area
## gotten from https://en.wikipedia.org/wiki/New_York_City_Metropolitan_Area
_nyc_metro_areas = {
    'New York' : {
        'Kings', 'Queens', 'New York', 'Bronx',
        'Richmond',
        'Westchester',
        'Putnam', 'Rockland',
        'Suffolk', 'Nassau',
        },
    'New Jersey' : {
        'Bergen', 'Hudson', 'Passaic',
        'Hudson', 'Passaic',
        'Putnam', 'Rockland',
        'Essex', 'Union', 'Morris',
        'Sussex', 'Hunterdon' },
    'Pennsylviania' : { 'Pike', } }
nyc_data = {
    'prefix' : 'nyc',
    'region name' : 'NYC Metro',
    'counties' : get_county_state_tuples( _nyc_metro_areas ) }
                      
#
## gotten these from the wikipedia for the Seattle metro area
## only include those parts in the US
_seattle_metro_areas = {
    'Washington' : {
        'King', 'Snohomish', 'Pierce',
        'Kitsap', 'Thurston', 'Skagit',
        'Island', 'Mason'
        } }
seattle_data = {
    'prefix' : 'seattle',
    'region name' : 'Seattle Metro',
    'counties' : get_county_state_tuples( _seattle_metro_areas ) }
