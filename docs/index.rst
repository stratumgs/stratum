Welcome to Stratum!
===================================

Stratum is a turn based game engine designed to pit autonomous players against
each other. The goal of the project is to produce a system where people can
create autonomous systems, and compete them against each other by playing games.
Adding a new game to the system is a fairly straightforward process. Clients do
not have to be tied to this project in any way, and can be independently
developed and implemented using whatever strategies are desired. Stratum can be
deployed for any group, from a small group of friends to a company (although at
this stage in development, the number of users the system can handle may be
limited).

The main components are the primary server, which consists of a web
server and tcp server, the clients, and the game engines. More information about
how these parts interact can be found on the :doc:`design` page. Information
about which games are available can be found on the :doc:`engines` page.

The main server is written using the asynchronous Python server Tornado. More
information about Tornado can be found on the project's official website:
`<http://www.tornadoweb.org/en/stable/>`_.

Stratum is licensed under the
`MIT License <https://opensource.org/licenses/MIT>`_.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   design
   protocols
   engines
   code

* :ref:`genindex`
* :ref:`modindex`

