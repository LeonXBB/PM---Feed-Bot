function get_rules_sets() {
    window.rules_sets_socket.onmessage = function(event) {
        var data = JSON.parse(event.data);
        
        var html_string = "";

        for (var i = 0; i < data.length; i+=2) {
            rules_set_id = data[i];
            rules_set_name = data[i+1];

            html_string += "<button class='centered_y generic_button rules_set_button bordered none' id='rules_set_button_" + rules_set_id + "'><div class='generic_button_text rules_set_button_text bold'><img src='./../static/img/sports/" + rules_set_id + ".png'> &nbsp" + rules_set_name.toUpperCase() + "</div></button>";
        }

        document.getElementById("rules_set_row").innerHTML = html_string;

        for (var i = 0; i < data.length; i+=2) {
            var button = document.getElementById("rules_set_button_" + data[i]);
            button.onclick = () => show_event_list_for_rules_set(button.id);
        };
    };
};