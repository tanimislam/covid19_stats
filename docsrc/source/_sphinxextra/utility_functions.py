import requests, urllib3, json
from bs4 import BeautifulSoup
#
## disable insecure connection warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def _format_size( fsize_b ):
    """
    Formats the bytes value into a string with KiB, MiB or GiB units. This code has been copied from :py:meth:`deluge's format_size <deluge.ui.console.utils.format_utils.format_size>`.
    :param int fsize_b: the filesize in bytes.
    :returns: formatted string in KiB, MiB or GiB units.
    :rtype: str
    **Usage**
    
    >>> format_size( 112245 )
    '109.6 KiB'
    """
    fsize_kb = fsize_b / 1024.0
    if fsize_kb < 1024:
        return "%.2f KiB" % fsize_kb
    fsize_mb = fsize_kb / 1024.0
    if fsize_mb < 1024:
        return "%.2f MiB" % fsize_mb
    fsize_gb = fsize_mb / 1024.0
    return "%.2f GiB" % fsize_gb

def get_dataset_size_formatted( mainURL = 'https://tanimislam.sfo3.digitaloceanspaces.com', verify = True ):
    """
    Gets the size of the dataset in our default CDN: https://tanimislam.sfo3.digitaloceanspaces.com
    """
    response = requests.get( mainURL, verify = verify )
    if response.status_code != 200:
        raise ValueError("Error, could not access URL = %s." % mainURL )
    #
    ## now get a data manifest
    xml = BeautifulSoup( response.content, 'xml' )
    contents_entries = list(filter(lambda elem: 'covid19movies' in elem.Key.text and elem.Key.text != 'covid19movies/',
                                   xml.find_all( 'Contents' ) ) )
    total_size = sum(list(map( lambda elem: float( elem.Size.text ), filter(None, contents_entries ) ) ) )
    return _format_size( total_size )

def get_topN_json( mainURL = 'https://tanimislam.sfo3.digitaloceanspaces.com/covid19movies/covid19_topN_LATEST.json', verify = True ):
    response = requests.get( mainURL, verify = verify )
    if response.status_code != 200:
        raise ValueError( "Error, could not access %s." % mainURL )
    json_data = json.loads( response.content )
    def _reformat_entry( entry ):
        return dict(map(lambda tup: ( '_'.join( tup[0].split()).replace(".",""), tup[1] ), entry.items()))
    return list(map(_reformat_entry, json_data))
