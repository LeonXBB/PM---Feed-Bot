var max_events_step = 3;
var max_events_to_show = max_events_step;

setInterval(updateDatetime, 500)

window.onload = function() {
    window.rules_sets_socket = new WebSocket(`ws://${document.getElementById("server_address").value}/ws/get_rules_sets/`);
    window.events_socket = new WebSocket(`ws://${document.getElementById("server_address").value}/ws/get_events_list/`);
    get_rules_sets();
};

