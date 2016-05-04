Design
======

This page provides a general overview of the structure of StratumGS and how the
various elements interact.

There are four main components to StratumGS: the web server, the client server,
the clients, and the game engines. The web server handles requests from the
browser, and it is what spawns new game engines, which run as separate processes
on the host machine. The client server handles clients that are connected, and
proxies the connections to those clients for the game engine. The clients
remotely connect from a user's machine, and are the autonomous players in the
game.


Web Server
----------

The web server is an asynchronous HTTP server, written using Tornado. It is the
primary way that users interact with the system. It serves three primary
puroses: displaying games, showing which games are in progress and what clients
are connected, and configuring and starting new games.

To display the connected clients and games in progress, the state is queried
from the relevant parts of the server and rendered in the browser. Configuring
new games is done by using a web form, which loads data from the ``CONFIG``
dictionary located in each game.

Viewing games is handled through a combination of WebSockets and JavaScript.
When a game view is opened, a WebSocket connection is made. That connection
receives state data from the game engine. The JavaScript code handles parsing
of the state data, and displaying the current state of the game.


Client Server
-------------

The client server, like the web server, is an asynchronous server, written with
tornado. It runs on the same main loop as the web server. It is a TCP server
that listens for incoming connections from clients. It is responsible for
managing these connections, as well as providing the game engines a way to
communicate with them.

Since the client server is asynchronous and the game engines are synchronous,
the client server also proxies the client connections using pipes or sockets,
depending on the system in use. Pipes are preferred, but as there is no way to
use pipes asynchronously on Windows, sockets are available as a backup.


Clients
-------

Clients are the players in the game, and they remotely connect from a user's
machine. They are typically implemented using a base library, which handles the
details of the communication protocol with the server, as well as running of the
main loop. While clients are intended to be autonomous, a client that takes
input from the user could be implemented, as a way to manually play against
other autonomous systems.


Game Engines
------------

The game engines are the backbone of the system. They run as a background
process, and communicate to the primary server using pipes or sockets. Again,
pipes are preferred, but sockets are provided as a backup where pipes are not
usable.

Game engines run synchronously on the system, and the process blocks while it is
waiting on input from a client. They handle all of the logic involved in running
a game, such as prompting clients for moves, processing those moves according to
the game rules, and determining when the game is over.
