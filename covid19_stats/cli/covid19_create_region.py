import sys, signal
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )
signal.signal( signal.SIGINT, signal_handler )
import os, numpy, tempfile, warnings, tabulate, logging, json, re, tabulate
from rapidfuzz.fuzz import ratio
from covid19_stats import COVID19Database
from covid19_stats.engine.core import create_readme_from_template
from argparse import ArgumentParser

#
## suppress warnings
warnings.simplefilter( 'ignore' )

#
## the because-vanilla-python-JSON-encoder-is-shit problem
## do this instead, following SO advice: https://stackoverflow.com/a/57915246
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        if isinstance(obj, numpy.floating):
            return float(obj)
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def get_closest_region_match(
    df_fips, county_name, state_name,
    minimum_partial = 0.9, county_names_dict = { } ):
    df_sub = df_fips[ df_fips.state_or_territory == state_name ]
    if df_sub.shape[0] == 0:
        raise ValueError("Error, no state or territory named %s." %
                         state_name )
    if len( county_names_dict ) == 0:
        county_names_dict = dict(map(lambda county: (
            re.sub('city', '', re.sub( 'county', '', county.lower())).strip(), county),
                                     sorted(df_sub.county )))
    best_match = max(county_names_dict, key = lambda clower: ratio(
        clower, county_name.lower( ) ) )
    best_match_score = ratio(
        county_name.lower(), best_match )
    if best_match_score < minimum_partial:
        return None
    return county_names_dict[ best_match ]

def get_closest_region_match_dict(
    df_fips, county_names, state_name, minimum_partial = 0.9 ):
    df_sub = df_fips[ df_fips.state_or_territory == state_name ]
    if df_sub.shape[1] == 0:
        raise ValueError("Error, no state or territory named %s." %
                         state_name )
    county_names_dict = dict(map(lambda county: (
        re.sub('city', '', re.sub( 'county', '', county.lower())).strip(), county),
                                 sorted(df_sub.county )))
    def _get_closest_match( county_name ):
        best_match = get_closest_region_match(
            df_sub, county_name, state_name,
            minimum_partial = minimum_partial,
            county_names_dict = county_names_dict )
        if best_match is None: return None
        return (county_name, best_match )

    county_match_dict = dict(map(_get_closest_match, county_names))
    len_vals = len( county_match_dict.values( ) )
    len_vals_set = len( set( county_match_dict.values( ) ) )
    if len_vals != len_vals_set:
        raise ValueError("Error, this cannot be right. Final list of candidate counties is %s." % (
            sorted( county_match_dict.values( )  ) ) )
    return county_match_dict

def create_region_json_file( df_fips, act_county_names, state_name, prefix, region_name ):
    df_sub = df_fips[ df_fips.state_or_territory == state_name ]
    list_fips = sorted(set(
        map(lambda county: df_sub[ df_sub.county == county ].fips.max( ),
            act_county_names)))
    tot_pop = sum(list(map(lambda fips: df_sub[ df_sub.fips == fips ].population.max( ),
                           list_fips)))
    region_data = {
        'prefix' : prefix,
        'region name' : region_name,
        'fips' : list_fips,
        'population' : tot_pop }
    json.dump( region_data, open( '%s.json' % prefix, 'w' ), indent = 1, cls = NpEncoder )

def yesno( ):
    """Simple Yes/No Function."""
    prompt = 'Does this look good ? (y/n): '
    ans = input(prompt).strip().lower()
    if ans not in ['y', 'n']:
        print(f'{ans} is invalid, please try again...')
        return yesno( )
    if ans == 'y':
        return True
    return False


def main( ):
    parser = ArgumentParser( )
    parser.add_argument('-c', '--counties', dest='counties', type=str, nargs="*", required = True,
                        help = 'List of counties (all in a single state) out of which to create a geographical region.' )
    parser.add_argument('-s', '--state', dest='state', type=str, required = True,
                        help = 'The single state from which to create a geographical region.' )
    parser.add_argument('-p', '--prefix', dest='prefix', type=str, required = True,
                        help = 'The prefix of the geographical region. Must be a single word.' )
    parser.add_argument('-n', '--name', dest='name', type=str, required = True,
                        help = 'Name of the geographical region.' )
    args = parser.parse_args( )
    #
    ## first get the FIPS database, assert state exists
    df_fips = COVID19Database.fips_dataframe_2019( )
    df_sub = df_fips[ df_fips.state_or_territory == args.state ]
    if df_sub.shape[ 0 ] == 0:
        print( 'ERROR, NO STATE NAMED %s. EXITING.' % args.state )
        return
    #
    ## prefix must be size 1
    num_toks = len( args.prefix.split( ) )
    if num_toks != 1:
        print('Error, the prefix = %s is not one word. Exiting.' % args.prefix )
        return
    #
    ##
    counties = sorted( set( args.counties ) )
    county_match_dict = get_closest_region_match_dict( df_sub, counties, args.state )
    print( 'In the state of %s here are the initial and finals.' % args.state )
    data = [ ]
    for county in counties:
        if county in county_match_dict:
            data.append(( county, county_match_dict[ county ] ) )
        else:
            data.append(( county, '' ) )
    print( '%s\n' % tabulate.tabulate( data, headers = [ 'INITIAL COUNTY NAME', 'ACTUAL COUNTY NAME' ] ) )
    status = yesno( )
    if not status:
        print( 'Does not look good. Exiting.' )
        return
    #
    ## now create the region
    create_region_json_file(
        df_fips, set(county_match_dict.values( ) ),
        args.state, args.prefix, args.name )
