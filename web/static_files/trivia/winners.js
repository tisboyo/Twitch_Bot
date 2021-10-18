function getAllUrlParams(url) {
    // Graciously stolen from sitepoint
    // https://www.sitepoint.com/get-url-parameters-with-javascript/
    // get query string from url (optional) or window
    var queryString = url ? url.split('?')[1] : window.location.search.slice(1);

    // we'll store the parameters here
    var obj = {};

    // if query string exists
    if (queryString) {
        // stuff after # is not part of query string, so get rid of it
        queryString = queryString.split('#')[0];

        // split our query string into its component parts
        var arr = queryString.split('&');

        for (var i = 0; i < arr.length; i++) {
            // separate the keys and the values
            var a = arr[i].split('=');

            // in case params look like: list[]=thing1&list[]=thing2
            var paramNum;
            var paramName = a[0].replace(/\[\d*\]/, function (v) {
                paramNum = v.slice(1, -1);
                return '';
            });

            // set parameter value (use 'true' if empty)
            var paramValue = typeof (a[1]) === 'undefined' ? true : a[1];

            // (optional) keep case consistent
            paramName = paramName.toLowerCase();
            paramValue = paramValue.toLowerCase();

            // if parameter name already exists
            if (obj[paramName]) {
                // convert value to array (if still string)
                if (typeof obj[paramName] === 'string') {
                    obj[paramName] = [obj[paramName]];
                }
                // if no array index number specified...
                if (typeof paramNum === 'undefined') {
                    // put the value on the end of the array
                    obj[paramName].push(paramValue);
                }
                // if array index number specified...
                else {
                    // put the value at that index number
                    obj[paramName][paramNum] = paramValue;
                }
            }
            // if param name doesn't exist yet, set it
            else {
                obj[paramName] = paramValue;
            }
        }
    }
    return obj;
}

async function startMQTTClient() {

    var params = getAllUrlParams(),
        client = mqtt.connect('wss://' + params.url + ':' + params.port, {
            clientId: 'triviawinners' + Math.random().toString(36).slice(2),
            username: params.username,
            password: params.password
        });


    client.on('connect', function () {
        client.subscribe('stream/trivia/winners'), function (err) { };
        client.subscribe('stream/trivia/show_winner_position'), function (err) { };
        client.subscribe('stream/trivia/trivia_winner_message'), function (err) { };
        console.log('mqtt connected');
    })

    window.onunload = () => {
        client.end();
    };

    client.on('message', function (topic, message) {
        // message is Buffer
        var data = JSON.parse(message);


        let firstPlace = document.getElementById("firstPlace");
        let secondPlace = document.getElementById("secondPlace");
        let thirdPlace = document.getElementById("thirdPlace");

        switch (topic) {
            case "stream/trivia/winners":
                if (data.first) {
                    firstPlace.innerHTML = '<div class="player">' + data.first.name + '</div><div class="score">' + data.first.score + '</div>';
                }
                if (data.second) {
                    secondPlace.innerHTML = '<div class="player">' + data.second.name + '</div><div class="score">' + data.second.score + '</div>';
                }
                if (data.third) {
                    thirdPlace.innerHTML = '<div class="player">' + data.third.name + '</div><div class="score">' + data.third.score + '</div>';
                }


                break;

            case "stream/trivia/show_winner_position":
                if (data.show == "third") {
                    thirdPlace.classList.add('winner-fadeIn')
                }
                else if (data.show == "second") {
                    secondPlace.classList.add('winner-fadeIn')
                }
                else if (data.show == "first") {
                    firstPlace.classList.add('winner-fadeIn')
                }

                break;

            case "stream/trivia/trivia_winner_message":
                var winner_message = document.getElementById('winner_message')

                if (data.message) {
                    winner_message.innerText = data.message;
                }
                break;


        }

    })
}

window.onload = startMQTTClient;
