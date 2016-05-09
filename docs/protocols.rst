Protocols
=========

StratumGS very heavily relies on network communication to enable clients to play
games against each other. This makes the protocol used to communicate an
important part of the design. There are two primary parts to the protocol:
messages intended for the management infrastructure, and messages intended for
the game engine. While the format is the messages sent between the client and
server is defined, game engines have some flexibility in designing the protocol
for each specific game. These messages get embedded inside a special type of
wrapper message. The only requirement is that the engine use an object that can
be encoded and decoded using JSON.

All messages are sent as JSON-encoded strings, with a newline terminating each
message. Each message has a ``type`` field, which directs the server on how to
handle the message.

The following sections document the various messages that can be sent by each
party. For each message, a list of field names is given in bold, each followed
by a description of what the value of the field should be. These key value pairs
should be encoded using JSON before being sent.


Server to Client Messages
-------------------------

Name
^^^^
When a client connects, a name for the client is determined. This messages tells
the client the name that it has been assigned.

- **type**: ``"name"``
- **name**: The name the server has assigned to the client.

Start
^^^^^
Tells the client it has been included in a new game that has been started, so
that it can initialize the object needed to play the game.

- **type**: ``"start"``
- **game_name**: The name of the game to start.
- **game_id**: The integer id of the new game.

Message
^^^^^^^
This message type wraps a message from the engine, and forwards it along to the
client.

- **type**: ``"message"``
- **game_id**: The integer id of the game the message is for.
- **payload**: The JSON-encoded string that is the message for the engine.

Close
^^^^^
Sent to the client to indicate that a game is over and the connection is closed.

- **type**: ``"close"``
- **game_id**: The game id for the game that has been ended.


Client to Server Messages
-------------------------

Connect
^^^^^^^
Sent when the client first connects. Provides the server with information about
the client.

- **type**: ``"connect"``
- **supported_games**: A list of games that the client is capable of playing.
- **max_games**: An integer giving the maximum number of simultaneous games the
  client can support.
- **name**: The name the client would like to use to identify itself. If the
  name isn't unique, the server will make it unique by appending a
  unique integer to the end. The client should not assume this
  identifier is the one to be used; instead, the client should wait
  for the server to reply with the name it has chosen. If this field
  is null, the server will automatically generate a name.

Message
^^^^^^^
How the client communicates with game engines. The payload field is decoded and
passed along to the engine for the specific game id.

- **type**: ``"message"``
- **game_id**: An integer indicating the game id the message is intended for.
- **payload**: The JSON-encoded message that is decoded and passed along to the
  game engine.

Close
^^^^^
Sent from the client to the server when the client is shut down. Explicitly
tells the server it is shutting down.

- **type**: ``"close"``
