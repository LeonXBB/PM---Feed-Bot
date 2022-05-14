var central_div_str = '<div id="central_divider"></div>';
var right_div_str = '<div id="right_divider"></div>';

function select_event(event_id) {
       
    if (document.getElementById("central_divider") === null) {
        document.getElementById("content").innerHTML += central_div_str; 
    }

    if (document.getElementById("event_data") === null) {
        document.getElementById("content").innerHTML += '<div class="flex_column between" id="event_data"></div>';
        load_event_data(event_id);
    }

    if (document.getElementById("right_divider") === null) {
        document.getElementById("content").innerHTML += right_div_str;
    
    }
}

function unselect_event(event_id) {

    if (document.getElementById("central_divider") != null) {
        document.getElementById("central_divider").remove();
    }

    if (document.getElementById("event_data") != null) {
        document.getElementById("event_data").remove();
    }

    if (document.getElementById("right_divider") != null) {
        document.getElementById("right_divider").remove();
    }

}

function click_event(event_row_id) {
    
    let event_id = event_row_id.id.split("_")[1];

    if (document.getElementById(event_row_id.id).classList.contains("selected")) {
        event_row = document.getElementById(event_row_id.id);
        event_row.classList.remove("selected");
        unselect_event(event_id);

    } else { 

        for (let another_event_row of document.getElementsByClassName("event_row")) {
            if (another_event_row.id != event_row_id.id) {
                another_event_row.classList.remove("selected");
                unselect_event(event_id);
            }
        }

        event_row = document.getElementById(event_row_id.id);
        event_row.classList.add("selected");
        select_event(event_id);
    }
}

function show_more_events(button_id) {

    max_events_to_show += max_events_step;

    show_event_list_for_rules_set(button_id.id, true);
}

function get_row(data, i) {
     
    let rv = `<tr class='event_row' id='event_${data[i+2]}' onclick=click_event(event_${data[i+2]})>`;
    
    let event_date = data[i].replace("-", "/").replace("-", "/");
    let event_time = data[i+1];
    let event_id = data[i+2];
    let comp_name = data[i+3].toUpperCase();
    let home_team_name = data[i+4].toUpperCase();
    let away_team_name = data[i+5].toUpperCase();
    let is_live= data[i+6];
    
    rv += `<td class="event_datetime_cell"><table><tr><td>${event_date}</td></tr><tr><td>${event_time}</td></tr></table></td>`;
    rv += `<td class="id_cell">${event_id}</td>`;
    rv += `<td class="competition_name_cell">${comp_name}</td>`;
    rv += `<td><b>${home_team_name}<br>${away_team_name}</b></td>`;

    if (is_live == 1) {
        rv += "<td><img class='live_event' src='./../static/img/uix/live.png'></td>";
    } else {
        rv += "<td><img class='live_event' src='./../static/img/uix/non_live.png'></td>";
    }

    rv += "<td><img class='event_row_arrow' src='./../static/img/uix/selected_event_arrow.png'></td>";

    rv += "</tr>";

    return rv;
};

function get_html_string(data, button_id) {

    let rv = "<div class='events_table_div'><table class='centered_x' id='events_table'>";
    
    //if (data.length == 0) {
    //    rv += "<tr><td>No events found</td></tr>"; TODO something like this
    //}

    for (let i = 0; i < data.length; i+=7) {
        
        rv += get_row(data, i)
    
        if (i >= 7*(max_events_to_show - 1)) {
            rv += `<tr><td colspan="5"><button class="centered_y generic_button bordered grey" id="show_more_events_button" onclick=show_more_events(${button_id})>ЗАГРУЗИТЬ ЕЩЕ</button></td></tr></table>`;
            return rv;
        };
    }

    rv += "</table></div>";   

    return rv;
}

function show_event_list_for_rules_set(button_id, append=false) {

    let rules_set_id = button_id.split("_")[3];

    let button = document.getElementById(button_id);

    window.events_socket.send("rules_set_id=" + rules_set_id);

    window.events_socket.onmessage = function(event) {

        let data = JSON.parse(event.data);

        if (data.length > 7 && document.getElementById("show_more_events_button") === null) {
            
            if (data[7] == "append") {
                let events_table = document.getElementById("events_table");
                let new_event_row = get_row(data, 0);
                events_table.innerHTML += new_event_row;
                return;     
            };
        };

        if (button.classList.contains("selected")) {
            
            if (append === false) {
                button.classList.remove("selected");
                max_events_to_show = max_events_step;
            };

            if (document.getElementById("content").innerHTML.trim() != "") {
                if (append === false) {
                    document.getElementById("content").innerHTML = "";
                } else {
                    document.getElementById("content").innerHTML = get_html_string(data, button_id);
                }
            } else {
                document.getElementById("content").innerHTML = get_html_string(data, button_id);
            };
        
        } else {
            
            button.classList.add("selected");
            for (let another_button of document.getElementsByClassName("rules_set_button")) {
                if (another_button.id != button_id && another_button.classList.contains("selected")) {
                    another_button.classList.remove("selected");
                    max_events_to_show = max_events_step;
                };
            };

            document.getElementById("content").innerHTML = get_html_string(data, button_id);
        };
    };
};