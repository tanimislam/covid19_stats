.. include:: cli_urls.rst

.. _covid19_post2server:
	     
covid19_post2server
======================
This CLI is designed to be used by an external service to upload data sets created by :ref:`covid19_movie_updates` to an external location. I (`Tanim Islam`_) have tested it, but stopped using it, because the data set I currently have is impractically large; instead I have a private repository with a public `GitHub Page`_ to which I push my latest COVID-19 summary data updates. This CLI is a front-end to functionality that lives in ``covid19_stats.engine.pushpull``.

Its help output, when running ``covid19_post2server -h``, is the following,

.. code-block:: console

   usage: covid19_post2server [-h] [-d DIRNAME] -D REMOTE_DIRNAME [--pe PROCESS_ENDPOINT] [--ve VERIFY_ENDPOINT] [--info] {ssh,http} ...

   positional arguments:
     {ssh,http}            Here, we choose the form of the connection. ssh: perform an SSH tunnel to the RESTful server. http: direct HTTP(S) connection to the RESTful server.
       ssh                 Use SSH tunneling to RESTful server.
       http                Direct HTTP or HTTPS connection to RESTful server.

   optional arguments:
     -h, --help            show this help message and exit
     -d DIRNAME, --dirname DIRNAME
			   Name of the directory that contains the COVID-19 movies and figures to send off to the external RESTful endpoint. Default is /usr/WS2/islam5/covid19movies.
     -D REMOTE_DIRNAME, --remote REMOTE_DIRNAME
			   Name of the REMOTE (on server) directory into which to store the COVID-19 movies and figures.
     --pe PROCESS_ENDPOINT
			   The name of the PROCESSING RESTful endpoint on the remote HTTP server. Default is /api/covid19/processresults.
     --ve VERIFY_ENDPOINT  The name of the PROCESSING RESTful endpoint on the remote HTTP server. Default is /api/covid19/verifyprocessedresults.
     --info                If chosen, then print out INFO level logging statements.

Here are its top-level common arguments.

* ``-d`` or ``--dirname`` is the directory that contains the COVID-19 movies and figures.

* ``-D`` or ``-remote`` is the directory on the *remote* server into which to store the COVID-19 movies and figures.

* ``--ve`` is the *verification endpoint* for the REST_ server.

* ``--pe`` is the *processing endpoint* for the REST_ server.

* ``--info`` if chosen, then run with INFO level debugging to screen.

.. _restful_absolute_locations:
  
If ``https://remote_http_server`` is the remote HTTP(S) server, then the verification endpoint is at ``https://remote_http_server/VERIFY_ENDPOINT``, and the processing endpoint is at ``https://remote_http_server/PROCESSING_ENDPOINT``.
     
``covid19_post2server`` has two modes of operation, either connection through an SSH tunnel (via the ``ssh`` keyword as described in :numref:`ssh_operation`) or through the standard un-tunnelled connection (via the ``http`` keyword as described in :numref:`http_operation`). However, this construction is *incomplete*. The client REST_ commands that this CLI emits requires a REST_ server to consume those commands and *transfer* that data.

* The server must have a remote directory, specified by ``REMOTE_DIRNAME``, that is owned by the server process.

* The accessible server REST_ remote prefix address, with the name ``HTTP_SERVER`` specified when running ``covid19_post2server http``.

* The server REST_ endpoint, by default ``/api/covid19/verifyprocessedresults``, used for *verifying* that the client can upload data to the server into the server's remote directory.

* The server REST_ endpoint, by default ``/api/covid19/processedresults``, used to upload data to the server's remote directory.

* *Implicitly*, the REST_ server must be able to authenticate an user by their email address and password in :ref:`http mode <http_operation>`, or must be able to login an user remotely through SSH_ with their username and password in :ref:`ssh mode <ssh_operation>`. Also, as described in :ref:`ssh mode <ssh_operation>`, the REST_ server must *also* be able to authenticate with SSH_ username and password.

.. _http_operation:

http operation
---------------
In this mode, one specifies a *valid* email address and password, to the REST_ server, to upload the COVID-19 data. 

Its help screen, when running ``covid19_post2server http -h``, is,

.. code-block:: console

   usage: covid19_post2server http [-h] -e HTTP_EMAIL -p HTTP_PASSWORD -s HTTP_SERVER [--noverify]

   optional arguments:
     -h, --help            show this help message and exit
     -e HTTP_EMAIL, --email HTTP_EMAIL
			   This RESTful server email address to authenticate for pulling in COVID-19 summary data.
     -p HTTP_PASSWORD, --password HTTP_PASSWORD
			   This RESTful server PASSWORD to authenticate for pulling in COVID-19 summary data.
     -s HTTP_SERVER, --server HTTP_SERVER
			   The URL of the HTTPS server that contains the RESTful COVID-19 processing endpoints.
     --noverify            If chosen, then do not verify SSL connections.

Use ``-e`` or ``--email`` to specify the user's email address, and ``-p`` or ``--password`` to specify their password. Use ``-s`` or ``--server`` to specify the remote REST_ server's accessible URL. This URL must have an ``http`` or ``https`` prefix in front of it.

Use ``--noverify`` to optionally disable SSL verification.
     
.. _ssh_operation:

ssh operation
---------------
In this mode, one specifies the remote name of the SSH_ server, and the username and password to login to the server.

*In actuality*, ``covid19_post2server`` performs an SSH_ tunnel from port 31999 on the local machine, to port 443 on the remote server machine. At that point, REST_ operations occur as described in :ref:`http mode <http_operation>`. *Implicitly*, the REST_ server must also be able to authenticate a REST_ client with the SSH_ login username and password.

* Its verification endpoint is locally at ``http://localhost:31999/VERIFY_ENDPOINT``.

* Its processing endpoint is locally at ``http://localhost:31999/PROCESSING_ENDPOINT``.

Its help screen, when running ``covid19_post2server http -h``, is,

.. code-block:: console

   usage: covid19_post2server ssh [-h] -u SSH_USERNAME -p SSH_PASSWORD -s SSH_SERVER

   optional arguments:
     -h, --help            show this help message and exit
     -u SSH_USERNAME, --username SSH_USERNAME
			   The SSH server username.
     -p SSH_PASSWORD, --password SSH_PASSWORD
			   The SSH server password associated with the username.
     -s SSH_SERVER, --server SSH_SERVER
			   The SSH server into which to tunnel.

``-u`` or ``--username`` is the SSH_ login username, ``-p`` or ``--password`` is the SSH_ login password, and ``-s`` or ``--server`` is the SSH_ server's address.
