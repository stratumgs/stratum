TicTacToe
=========

Overview
--------

This engine, as you would expect, implements TicTacToe. It will simply prompt
the players for their move, starting with X, then O, and so on, until the game
is over. The game can end either with a player winning, or a draw. This engine
is very forgiving: if a player makes an invalid move, they are prompted again
for a different move.


Config
------

- **Number of Players**: 2


Protocol
--------

Engine to Client
^^^^^^^^^^^^^^^^

State
"""""
Sent to the client to provide the current state of the game.

- **type**: ``"state"``
- **board**: The current board. It is a two dimensional array containing the
  strings ``"X"`` and ``"O"`` to indicate moves that have been made, and
  ``null`` for empty squares.
- **winner**: The winner of the game. If the game is over, and either the X or O
  player has won, the value with be ``"X"`` or ``"O"`` respectively. If the game
  is not over, or has ended in a draw, the value will be ``null``.


Turn
""""
Sent to the client to prompt for a move.

- **type**: ``"turn"``


Repeat Turn
"""""""""""
If a client makes an invalid move, this message is sent to ask the client to
make a different move instead.

- **type**: ``"repeat-turn"``
- **error**: The reason the client is being asked to choose a different move. If
  the client's move was not a legal space on the board, this will be the string
  ``"out-of-bounds"``. If the client tried to play in a space that wasn't empty,
  this will be the string ``"space-not-empty"``.
- **last-move**: The last move that the client makes. This is sent in order to
  make is easier for the client to not make the same move twice. This move
  object will be in the same format as the move message the client sends.


Client to Engine
^^^^^^^^^^^^^^^^

Move
""""
Sent by the client to indicate the move to be made.

- **type**: ``"move"``
- **row**: An integer, either 0, 1, or 2, indicating which row to make the move
  in.
- **column**: An integer, either 0, 1, or 2, indicating which column to make the
  move in.
