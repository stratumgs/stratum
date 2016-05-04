(function() {
    'use strict';

    var socket_url,
        web_socket;

    if (window.location.protocol === 'https:') {
        socket_url = 'wss:';
    } else {
        socket_url = 'ws:';
    }
    socket_url += '//' + window.location.host;
    socket_url += window.location.pathname + '/socket';

    web_socket = new WebSocket(socket_url);
    web_socket.onmessage = function (msg) {
        var obj = JSON.parse(msg.data),
            state;
        if (obj["type"] !== "message") {
            throw new Error("Invalid message received from server.");
        }
        StratumGSView.onstate(JSON.parse(obj["payload"]));
    };

})();
