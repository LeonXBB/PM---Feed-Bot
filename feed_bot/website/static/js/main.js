var max_events_step = 7;
var max_events_to_show = max_events_step;

setInterval(updateDatetime, 500)

window.onload = function() {
    window.rules_sets_socket = new WebSocket(`ws://${document.getElementById("output_address").value}/ws/get_rules_sets/`);
    window.events_socket = new WebSocket(`ws://${document.getElementById("output_address").value}/ws/get_events_list/`);
    window.event_data_socket = new WebSocket(`ws://${document.getElementById("output_address").value}/ws/get_event_data/`);
    get_rules_sets();
};

