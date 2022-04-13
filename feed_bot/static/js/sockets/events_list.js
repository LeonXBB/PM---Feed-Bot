var fake_div_str = '<div class="fake_div" id="central_divider"></div>';

function load_event_data(event_id) {
    
    let event_data_table = document.getElementById("event_data_table");

    event_data_table.innerHTML += '<table>t1</table>'; //api
    event_data_table.innerHTML += '<table>t2</table>'; //stats
}

function select_event(event_id) {
       
    if (document.getElementById("central_divider") === null) {
        document.getElementById("content_tables").innerHTML += fake_div_str; 
    }

    if (document.getElementById("event_data_table") === null) {
        document.getElementById("content_tables").innerHTML += '<div id="event_data_table"></div>';
        
        let event_data_table = document.getElementById("event_data_table");
        
        load_event_data(event_id);
    }

    if (document.getElementById("selected_event_arrow") === null) {
        
        //retreive live td position
        let event_row = document.getElementById(`event_${event_id}`);
        let live_event_cell = event_row.getElementsByClassName("live_event")[0];
        
        let live_event_cell_position = live_event_cell.getBoundingClientRect();
        let live_event_cell_position_x = live_event_cell_position.x;
        let live_event_cell_position_y = live_event_cell_position.y;

        let live_event_cell_width = live_event_cell.offsetWidth;
        let live_event_cell_height = live_event_cell.offsetHeight;
        
        //calculate image_coordinates and image_size
        let image_size = {
            width: live_event_cell_width * 2,
            height: live_event_cell_height * 7
        };
        
        let image_coordinates = {
            x: live_event_cell_position_x + live_event_cell_width * 1.5 + 1 - image_size.width / 2,
            y: live_event_cell_position_y - live_event_cell_height * 1.5 - image_size.height / 4
        };

        //create image
        let image = document.createElement("img", {"id": "selected_event_arrow"});
        image.src = "./../static/img/uix/selected_event_arrow.png";

        image.style.position = "absolute";
        image.style.left = image_coordinates.x + "px";
        image.style.top = image_coordinates.y + "px";
        image.style.width = image_size.width + "px";
        image.style.height = image_size.height + "px";

        document.getElementById("central_divider").appendChild(image);
    }

}

function unselect_event(event_id) {

    if (document.getElementById("central_divider") != null) {
        document.getElementById("central_divider").remove();
    }

    if (document.getElementById("selected_event_arrow") != null) {
        document.getElementById("selected_event_arrow").remove();
    }

    if (document.getElementById("event_data_table") != null) {
        document.getElementById("event_data_table").remove();
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

function get_html_string(data, button_id) {
    
    let rv = "<table class='centered_x' id='events_table'>";
    
    for (let i = 0; i < data.length; i+=7) {
        
        rv += `<tr class='event_row' id='event_${data[i+2]}' onclick=click_event(event_${data[i+2]})>`;
        
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

        rv += "</tr>";
    
        if (i >= 6*(max_events_to_show-1)) {
            rv += `<tr><td colspan="5"><button class="centered_y generic_button bordered grey" id="show_more_events_button" onclick=show_more_events(${button_id})>ЗАГРУЗИТЬ ЕЩЕ</button></td></tr></table>`;
            return rv;
        };
    }

    rv += "</table>";   

    return rv;
}

function show_event_list_for_rules_set(button_id, append=false) {

    let rules_set_id = button_id.split("_")[3];

    let button = document.getElementById(button_id);

    window.events_socket.send(rules_set_id);
    
    window.events_socket.onmessage = function(event) {

        let data = JSON.parse(event.data);

        if (button.classList.contains("selected")) {
            
            if (append === false) {
                button.classList.remove("selected");
                max_events_to_show = max_events_step;
            };

            if (document.getElementById("content_tables").innerHTML.trim() != "") {
                if (append === false) {
                    document.getElementById("content_tables").innerHTML = "";
                } else {
                    document.getElementById("content_tables").innerHTML = get_html_string(data, button_id);
                }
            } else {
                document.getElementById("content_tables").innerHTML = get_html_string(data, button_id);
            };
        
        } else {
            
            button.classList.add("selected");
            for (let another_button of document.getElementsByClassName("rules_set_button")) {
                if (another_button.id != button_id) {
                    another_button.classList.remove("selected");
                    max_events_to_show = max_events_step;
                };
            };

            document.getElementById("content_tables").innerHTML = get_html_string(data, button_id);
        };
    };
};