function updateDatetime(){ //TODO move variables declaration to main 
    var date = new Date();

    var day = date.getDate();
    var hours = date.getHours();
    var minutes = date.getMinutes();

    var months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]; //TODO add to localization db and rewrite as a request to server
    var month = months[date.getMonth()];

    /*
    for (let element of [day, hours, minutes]) {
    //    if (element.toString().length < 2) {
    //        element += '0';
    //    }
    }
    */ //TODO this is not python, write js solution

    if (day.toString().length < 2) {
        day = '0' + day;
    }
    if (hours.toString().length < 2) {
        hours = '0' + hours;
    }
    if (minutes.toString().length < 2) {
        minutes = '0' + minutes;
    }

    var insert_string = day + " " + month + ", " + hours + ":" + minutes;
    document.getElementById("datetime").innerHTML = insert_string
}