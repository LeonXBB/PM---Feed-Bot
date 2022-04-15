function get_scores_string(scores_by_period, team_names, active_period, total_scores, total_periods) {

    console.log(scores_by_period, team_names, active_period, total_scores, total_periods)

    let rv = "<div class='scores_table_div' id='scores'><table class='scores_table'>";

    rv += "<tr>";
    rv += "<td></td>";
    for (i = 0; i < total_periods; i++) {
        if (i < active_period) {    
            rv += "<td>" + (i+1) + "-й</td>";
        } else {
            rv += "<td>-</td>";
        }
    };
    rv += "</tr>";

    for (let i = 0; i < 2; i++) {
        rv += "<tr>";
        rv += "<td>" + team_names[i] + "</td>";
        for (let y = i; y < scores_by_period.length; y+=2) {
            rv += `<td id='team_${i}_period_${y / 2}'>` + scores_by_period[y] + "</td>";
        }
        rv += "</tr>";
    }
    rv += "</table></div>";

    return rv;
}

function get_messages_string(data) {

    let rv = '<div class="messages_table_div"><table class="messages_table"><thead><tr><th>TIME</th><th>SCORE</th><th>DESCRIPTION</th></tr></thead><tbody id="messages">';

    rv += '</tbody></table></div>';

    return rv;
}

function get_stats_string(data) {
    return '<div class="stats_table_div"><table class="stats_table"><thead><tr><th>TIME</th><th>SCORE</th><th>DESCRIPTION</th></tr></thead><tbody>';
}

function load_event_data(event_id) {
    
    window.event_data_socket.send("event_id=" + event_id);

    window.event_data_socket.onmessage = function(event) {

        let data = JSON.parse(event.data);

        let event_data_table = document.getElementById("event_data");

        console.log(data)

        if (data.includes("new_message")) {
            
            let tr=document.createElement("TR");
            let time_td=document.createElement("TD");
            let score_td=document.createElement("TD");
            let description_td=document.createElement("TD");

            date = new Date;
            time_td.innerHTML=date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
            description_td.innerHTML = data.split("new_message_")[1]
            
            tr.appendChild(time_td);
            tr.appendChild(score_td);
            tr.appendChild(description_td);
            
            document.getElementById("messages").appendChild(tr);
            return;

        } else {
            
            if (document.getElementById("scores") != null) {
                event_data_table.removeChild(document.getElementById("scores"));
            }

            let total_periods = data[0];
            let scores_by_period = data.slice(1, data[0] * 2 + 1);
            let team_names = data.slice(scores_by_period.length + 1, scores_by_period.length + 3);
            let active_period = data.slice(scores_by_period.length + 1 + team_names.length, data.length - 2)[0];
            let total_scores = data.slice(data.length - 2, data.length);

            event_data_table.innerHTML += get_scores_string(scores_by_period, team_names, active_period, total_scores, total_periods);

            if (document.getElementById("messages") === null) {
                event_data_table.innerHTML += get_messages_string(data);
            }
            //event_data_table.innerHTML += get_stats_string(data);
        }
    };
};