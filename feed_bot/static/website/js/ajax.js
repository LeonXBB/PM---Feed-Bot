function update_content(responseText){
    //document.getElementById('content').innerHTML = responseText;
    alert(responseText.textContent);
}

function run_requests(){

    params = {
        "task": "get_all",
        "model": "EventTemplateEdit",
        "fields": ["id", "field_name", "old_value", "new_value"],
    }

    req = new XMLHttpRequest(onload=update_content);
    req.open("POST", server_address + "/api/", true);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.send(params); 
}

let server_address = JSON.parse(document.getElementById('server_address').textContent);
let requests_interval = JSON.parse(document.getElementById('requests_interval').textContent);

setInterval(run_requests, requests_interval);