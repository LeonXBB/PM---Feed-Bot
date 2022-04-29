function get_scores_string(scores_by_period, team_names, active_period, total_scores, total_periods) {

    let rv = "<div class='scores_table_div' id='scores'><table class='scores_table'>";

    rv += "<tr>";
    rv += "<td></td>";
    for (i = 0; i < total_periods; i++) {
        if (i < active_period) {    
            rv += "<td class='period_number'>" + (i+1) + "-й</td>";
        } else {
            rv += "<td class='period_number'>-</td>";
        }
    };

    rv += "<td class='total_score'>Всего</td></tr>";

    for (let i = 0; i < 2; i++) {
        rv += "<tr>";
        rv += "<td class='bold team_name'><b>" + team_names[i] + "</b></td>";
        for (let y = i; y < scores_by_period.length; y+=2) {
            rv += `<td class='period_score' id='team_${i}_period_${parseInt(y / 2)}'>` + scores_by_period[y] + "</td>";
        }
        rv += `<div class='total_score_div'><td class='bold total_score' id='total_${i}'>` + total_scores[i] + "</td></div>";
        rv += "</tr>";
    }
    rv += "</table></div>";

    return rv;
}

function get_messages_string(message_data) {

    let rv = '<div class="messages_table_div"><table class="messages_table"><thead><tr><th>TIME</th><th>SCORE</th><th>DESCRIPTION</th></tr></thead><tbody id="messages">';

    for (let i=0; i < message_data.length; i+=3) {
        
        rv += "<tr>";
        rv += "<td>" + message_data[i] + "</td>";
        rv += "<td>" + message_data[i+1] + "</td>";
        rv += "<td>" + message_data[i+2] + "</td>";
        rv += "</tr>";
    };

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

        if (data.includes("new_message")) {
            
            let tr=document.createElement("TR");
            let time_td=document.createElement("TD");
            let score_td=document.createElement("TD");
            let description_td=document.createElement("TD");

            time_td.innerHTML=data.split("new_message_")[1].split("_")[0];
            score_td.innerHTML=data.split("new_message_")[1].split("_")[1];
            description_td.innerHTML=data.split("new_message_")[1].split("_")[2];

            tr.appendChild(time_td);
            tr.appendChild(score_td);
            tr.appendChild(description_td);
            
            document.getElementById("messages").appendChild(tr);

            return;

        } else if (data.includes("new_score")) {
            
            let team_index = data.split("_")[2]
            let period_index = data.split("_")[3]
            let score_value = data.split("_")[4]
            let new_score = data.split("_")[5] 
            let opposite_score_value = data.split("_")[6]
            let opposite_new_score = data.split("_")[7]

            let period_score_td = document.getElementById("team_" + team_index + "_period_" + period_index);
            let total_score_td = document.getElementById("total_" + team_index);
            let opposite_period_score_td = document.getElementById("team_" + (1 - team_index) + "_period_" + period_index);
            let opposite_total_score_td = document.getElementById("total_" + (1 - team_index));

            period_score_td.innerHTML = new_score;
            total_score_td.innerHTML = parseInt(total_score_td.innerHTML) + parseInt(score_value);
            opposite_period_score_td.innerHTML = opposite_new_score;
            opposite_total_score_td.innerHTML = parseInt(opposite_total_score_td.innerHTML) + parseInt(opposite_score_value);

            return;

        } else if (data.includes("new_stats")) {
       
            return;
       
        } else {

            event_data_table.innerHTML = "";

            let total_periods = data[0];
            let scores_by_period = data.slice(1, data[0] * 2 + 1);
            let team_names = data.slice(scores_by_period.length + 1, scores_by_period.length + 3);
            let active_period = data.slice(scores_by_period.length + 1 + team_names.length, data.indexOf("messages_start") - 2)[0];
            let total_scores = data.slice(data.indexOf("messages_start") - 2, data.indexOf("messages_start"));

            let messages_data = data.slice(data.indexOf("messages_start") + 1, data.indexOf("messages_end"));

            event_data_table.innerHTML += get_scores_string(scores_by_period, team_names, active_period, total_scores, total_periods);
            event_data_table.innerHTML += get_messages_string(messages_data);

            //event_data_table.innerHTML += get_stats_string(data);
        };
    };
};