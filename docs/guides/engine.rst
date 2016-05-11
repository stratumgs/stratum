Creating a Game Engine
======================

There are four things that need to be done to create a game engine, as follows:

#. `Create the Game Engine`_
#. `Register the Game Engine`_
#. `Create the assets`_
#. `Document the Game Engine`_

For examples for any of these steps, reference the corresponding files for the
:doc:`../engines/tictactoe` game.


Create the Game Engine
----------------------

To create a game engine, add a module to ``stratumgs.game.games``. The name of
the module should be all lowercase, with minimal punctuation, and will be used
as the string identifier for your game. Within the module, you must define a
``CONFIG`` object, and a class called ``Engine``, which extends
:class:`stratumgs.game.engine.BaseEngine`.

The ``CONFIG`` object defines meta data about the engine. The config object
should define the following fields:

- **display_name** - The name that should be used to display the game engine in
  the user interface.
- **description** - The description of the game to display to the users.
- **num_players** - The number of players the game supports.
- **player_names** - The display name of each player in the game.

The ``Engine`` class should implement ``is_game_over``, ``get_state``, and
``play_turn``. For more information see the
:class:`stratumgs.game.engine.BaseEngine` documentation.


Register the Game Engine
------------------------

For the application to know the game engine is available, it must be registered.
This is accomplished by adding the module to the ``_GAME_ENGINES`` dictionary in
``stratumgs/game/__init__.py``.


Create the assets
-----------------

For the game to be visible in the browser, the HTML, CSS, and JavaScript files
that handle display need to be created.

First the needed HTML should be created in ``stratumgs/assets/templates/games``,
using the engine's module name as the file name.

In ``stratumgs/assets/web/games``, a folder for the engine module should be
created. In that folder should be a ``game.css``, with any needed CSS, and a
``game.js`` with the JavaScript needed to interpret and display state messages
from the engine.


Document the Game Engine
------------------------

The final step is to document the engine. The code itself should be documented,
which involves creating a file in ``docs/code`` using the full name of the module,
and adding an entry for it to the ``toctree`` in ``docs/code.rst``.

The engine should also be documented at a higher level. A file should be added
to ``docs/engines`` to accomplish this, and an entry for the file should be
added to the ``toctree`` in ``docs/engines.rst``. This documentation should
describe the game, and explain the protocols used by the engine.
