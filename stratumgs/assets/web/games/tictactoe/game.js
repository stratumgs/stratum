(function() {
    'use strict';

    StratumGSView.onstate = function(state) {
        var cells = document.querySelectorAll('#tictactoe-table td'),
            k = 0;
        for (var i in state["board"]) {
            for (var j in state["board"][i]) {
                cells[k].textContent = state["board"][i][j];
                k++;
            }
        }
    };

})();
