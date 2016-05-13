Client
======

Clients are the players in the games. They are run on a user's machine, and
communicate to the server over a network connection. Implementing a client to
play a game is relatively simple.

The documentation for the client library can be found here:
https://python-client.stratumgs.org.

The first step is to install the library.

.. code-block:: shell

    pip install sgsclient

Next, create a class that extends :class:`sgsclient.StratumGSClientInstance`.
This subclass should implement the ``server_closed_connection`` and 
``message_received_from_server`` methods. 

For more information about the messages the client might receive from the
engine, see the documentation for that engine.

To start the program, call :func:`sgsclient.main`. The main function takes in
several parameters that configures how your client connects to the server, such
as the name of the client, how many concurrent games it supports, and which
games it can play. Additionally you can specify a default server and port, which
will be used if they are not provided as arguments on the command line.
