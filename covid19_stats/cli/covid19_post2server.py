import sys, signal
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )
signal.signal( signal.SIGINT, signal_handler )
import os, json, logging, time, glob, warnings
from covid19_stats.engine import pushpull
from argparse import ArgumentParser

warnings.simplefilter('ignore')

def _get_data_dict( dirname ):
    try:
        assert( os.path.isdir( dirname ) )
        summary_json_file = os.path.join( dirname, 'covid19_topN_LATEST.json' )
        assert( os.path.isfile( summary_json_file ) )
    except Exception as e:
        logging.error("ERROR, could not load in JSON file, covid19_topN_LATEST.json, in directory = %s. Error is %s." % (
            os.path.abspath( dirname ), str( e ) ) )
        return None
    init_mp4_files = set(filter(os.path.isfile, glob.glob( os.path.join( dirname, '*.mp4' ) ) ) )
    init_png_files = set(filter(os.path.isfile, glob.glob( os.path.join( dirname, '*.png' ) ) ) )
    #
    ## first make sure that this JSON summary of COVID-19 stats of topN metros is correct
    try:
        assert( pushpull.verify_summary_data( json.load( open( summary_json_file, 'r' ) ) ) )
    except Exception as e:
        logging.error('ERROR, could not load in %s. Exception message: %s.' % (
            os.path.abspath( summary_json_file ), str( e ) ) )
        return None
    #
    ## second, make sure the data dictionary is correct
    try:
        data_dict = pushpull.create_pushing_dictionary(
            init_mp4_files, init_png_files, summary_json_file )
        return data_dict
    except Exception as e:
        logging.error("ERROR, could not create the necessary collection of data to send to the server endpoint. Error message: %s." % ( str( e ) ) )
        return None

def main( ):
    time0 = time.time( )
    parser = ArgumentParser( )
    parser.add_argument(
        '-d', '--dirname', dest='dirname', action='store', type=str, default = os.getcwd( ),
        help = 'Name of the directory that contains the COVID-19 movies and figures to send off to the external RESTful endpoint. Def' )
    parser.add_argument(
        '-s', '--server', dest='server', action='store', type=str, default = '',
        help = '\n'.join([
            'The URL of the HTTPS server that contains the RESTful COVID-19 processing endpoints.',
            'For SSH tunneling, we do not need to define this.' ]) )
    parser.add_argument(
        '--pe', dest='process_endpoint', action='store', type=str, default = '/api/covid19/processresults',
        help = 'The name of the PROCESSING RESTful endpoint on the remote HTTP server. Default is /api/covid19/processresults.' )
    parser.add_argument(
        '--ve', dest='verify_endpoint', action='store', type=str, default = '/api/covid19/verifyprocessedresults',
        help = 'The name of the PROCESSING RESTful endpoint on the remote HTTP server. Default is /api/covid19/verifyprocessedresults.' )
    parser.add_argument(
        '-e', '--email', dest='email', type=str, action='store', required = True,
        help = 'This server needs to require an email address to authenticate for pulling in COVID-19 summary data.' )
    parser.add_argument(
        '-p', '--password', dest='password', type=str, action='store', required = True,
        help = 'This server needs to require a PASSWORD to authenticate for pulling in COVID-19 summary data.' )
    parser.add_argument(
        '--noverify', dest='do_verify', action='store_false', default = True,
        help = 'If chosen, then do not verify SSL connections.' )
    parser.add_argument(
        '--info', dest='do_info', action='store_true', default = False,
        help = 'If chosen, then print out INFO level logging statements.' )
    #
    ## now the SSH stuff
    subparsers = parser.add_subparsers(
        help = 'Here, we can OPTIONALLY put in SSH tunneling. This is the "ssh" keyword.',
        dest = 'choose_option' )
    #
    ## using the SSH connection.
    parser_ssh = subparsers.add_parser( 'ssh', help = 'Use SSH tunneling. If done, then provide SSH username and password.' )
    parser_ssh.add_argument( '-u', '--username', dest='ssh_username', type=str, action='store', required = True,
                            help = "The SSH server username." )
    parser_ssh.add_argument( '-P', '--password', dest='ssh_password', type=str, action='store', required = True,
                            help = "The SSH server password associated with the username." )
    parser_ssh.add_argument( '-S', '--server', dest='ssh_server', type=str, action='store', required = True,
                            help = "The SSH server into which to tunnel." )
    #
    ##
    args = parser.parse_args( )
    logger = logging.getLogger( )
    if args.do_info: logger.setLevel( logging.INFO )
    #
    ## now get the data_dict
    data_dict = _get_data_dict( args.dirname )
    if data_dict is None: return None
    #
    ## now if choosing the ssh connection
    ssh_connection_info = { }
    if args.choose_option == 'ssh':
        ssh_connection_info[ 'username' ] = args.ssh_username
        ssh_connection_info[ 'password' ] = args.ssh_password
        ssh_connection_info[ 'server'   ] = args.ssh_server
    #
    ## now do everything here
    messages_here_final = pushpull.post_to_server(
        args.server, args.process_endpoint,  args.verify_endpoint,
        data_dict, args.email, args.password, verify = args.do_verify,
        ssh_connection_info = ssh_connection_info )
    if 'messages' in messages_here_final:
        logging.info('\n'.join( messages_here_final[ 'messages' ] ) )
    else: logging.info( 'message block: %s.' % messages_here_final )
