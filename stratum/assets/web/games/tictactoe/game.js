(function () {
    'use strict';

    var socket_url;
    if (window.location.protocol === 'https:') {
        socket_url = 'wss:';
    } else {
        socket_url = 'ws:';
    }
    socket_url += '//' + window.location.host;
    socket_url += window.location.pathname + '/socket';
    var ws = new WebSocket(socket_url);
    ws.onmessage = function (msg) {
        var state = JSON.parse(msg.data.substring(6)),
            cells = document.querySelectorAll('#tictactoe-table td');
        var k = 0;
        for (var i in state) {
            for (var j in state[i]) {
                cells[k].textContent = state[i][j];
                k++;
            }
        }
    };

})();
