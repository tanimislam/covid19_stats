#!/usr/bin/env python3

import os, sys, numpy, engine

engine.get_summary_demo_data( doShow = False )
engine.get_summary_demo_data( prefix = 'richmond', state = 'Virginia',
                              regionName = 'Richmond Metropolitan Area',
                              list_of_counties = [
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
                                "Sussex" ], doShow = False )


engine.get_summary_demo_data( prefix = 'dc', state = 'District of Columbia',
                              regionName = 'Washington DC',
                              list_of_counties = [ "District of Columbia" ], doShow = False )

