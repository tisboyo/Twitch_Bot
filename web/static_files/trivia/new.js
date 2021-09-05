(function () {
    //Not a great coder look at all my globals
    var ActivePoll,
        TriviaQuestion,
        ChoiceCount,
        SubMultiplier;


    // Graciously stolen from sitepoint
    // https://www.sitepoint.com/get-url-parameters-with-javascript/
    function getAllUrlParams(url) {
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



    window.onload = async () => {

        var params = getAllUrlParams(),
            client = mqtt.connect('wss://' + params.url + ':' + params.port, {
                clientId: 'triviapage' + Math.random().toString(36).slice(2),
                username: params.username,
                password: params.password
            });


        client.on('connect', function () {
            client.subscribe('stream/trivia/current_question_setup'), function (err) { };
            client.subscribe('stream/trivia/current_question_data'), function (err) { }; //{'votes': {'1':1}, 'done':false}
        })

        client.on('message', function (topic, message) {
            // message is Buffer
            var data = JSON.parse(message);

            switch (topic) {
                case "stream/trivia/current_question_setup":
                    {   // {
                        //     "text": "When coding, should you use tabs or spaces for indentation?",
                        //     "total_duration": 59,
                        //     "choices": [
                        //         "A",
                        //         "B"
                        //     ],
                        //     "answers": {
                        //         "1": {
                        //             "is_answer": 0,
                        //             "text": "Tabs"
                        //         },
                        //         "2": {
                        //             "is_answer": 1,
                        //             "text": "Spaces"
                        //         }
                        //     },
                        //     "active": true
                        // }

                        let display_div = document.getElementById("display-div");
                        let timer = document.getElementById('timer');

                        if (!data.active) {
                            TriviaQuestion = "";
                            ChoiceCount = "";
                            SubMultiplier = "";
                            ActivePoll = "";
                            update_frequency = "1"
                            timer.innerHTML = "";
                            let root = document.documentElement;

                            setTimeout(function () {
                                display_div.innerHTML = '';
                            }, 1000);
                            root.style.setProperty('--fade', 0);

                            break;
                        }

                        TriviaQuestion = data.text;
                        ChoiceCount = data.choices.length;
                        SubMultiplier = data.sub_multiplier;
                        ActivePoll = data.active;
                        //Make BigBoiBox that holed the actual poll
                        let root = document.documentElement;
                        root.style.setProperty('--update-frequency', data.update_frequency + "s");
                        let big_boi = document.createElement("div");
                        big_boi.setAttribute("id", "poll");
                        big_boi.setAttribute("class", "big-boi-container");

                        display_div.appendChild(big_boi);

                        // Create Poll header
                        let title = document.createElement('div');
                        title.setAttribute('class', 'triviaQuestion');
                        title.innerHTML = TriviaQuestion;

                        let poll = document.getElementById("poll");
                        big_boi.appendChild(title);

                        let smolboi = document.createElement('div');
                        smolboi.setAttribute('class', 'smolboi');
                        big_boi.appendChild(smolboi);

                        let box = document.createElement('div');
                        box.setAttribute('class', 'questions');
                        smolboi.appendChild(box)

                        let picturebox = document.createElement('div');
                        picturebox.setAttribute('class', 'picturebox');
                        smolboi.appendChild(picturebox)

                        let picture = document.createElement('img');
                        picture.setAttribute('class', 'picture');
                        picture.setAttribute('src', "/trivia/images/" + data.image + "?key=" + params.key);

                        picturebox.appendChild(picture)

                        var audio = new Audio('/trivia/sounds/' + data.sound + '?key=' + params.key)
                        audio.play()


                        for (let i in data.answers) {
                            let container = document.createElement('div');   //Full container holds everything for a question
                            container.setAttribute('class', 'outer-div');
                            container.setAttribute('id', 'pollElement-' + i);
                            box.appendChild(container);

                            let elem = document.createElement('div'); //Floating container that holds question info above progressbar
                            elem.setAttribute('class', 'info-div');
                            elem.setAttribute('id', 'pollElement-' + i);
                            container.appendChild(elem);

                            let voteletters = data.choices
                            let choiceelem = document.createElement('div');  //Actual Question
                            //let votenum = parseInt(i) - 1
                            choiceelem.innerHTML = data.choices[i - 1] + " " + data.answers[i].text;
                            choiceelem.setAttribute('class', 'answer');
                            choiceelem.setAttribute('id', 'choice-' + i);
                            elem.appendChild(choiceelem);

                            let voteelem = document.createElement('div');  //Vote Count
                            voteelem.innerHTML = '';
                            voteelem.setAttribute('class', 'count');
                            voteelem.setAttribute('id', 'votes-' + i);
                            // voteelem.innerHTML = 0;  // Starting Answer Count
                            elem.appendChild(voteelem);

                            let progress = document.createElement('div');  //Progress bar
                            progress.innerHTML = '';
                            progress.setAttribute('class', 'bar-div');
                            progress.setAttribute('id', 'bar-div-' + i);
                            container.appendChild(progress);
                        }




                        let howtovote = document.createElement('div');
                        howtovote.setAttribute('class', 'footer-div');
                        howtovote.setAttribute('id', 'footer-div');
                        howtovote.innerHTML = "Vote with !vote &ltx&gt";
                        poll.appendChild(howtovote);

                        root.style.setProperty('--fade', 1);
                        break;
                    }
                case "stream/trivia/current_question_data":
                    {
                        if (ActivePoll) {

                            if (data.done) {
                                //Grey out all non winners
                                for (i in data.votes) {
                                    let vote = document.getElementById('bar-div-' + (i));
                                    vote.style.setProperty('filter', 'saturate(0)')
                                }
                                let vote = document.getElementById('bar-div-' + data.answer_id);
                                vote.style.setProperty('filter', 'saturate(1)');
                                let footer = document.getElementById('footer-div');
                                footer.innerHTML = data.explain;

                                break;
                            }
                            let timer = document.getElementById('timer');
                            timer.innerHTML = data.seconds_left;
                            for (i in data.votes) {
                                //TODO Figureout "better looking" scaling.
                                let choiceline = document.getElementById('bar-div-' + (i));
                                choiceline.style.setProperty('width', Math.round((data.votes[i] / data.total) * 100) + '%');
                            }


                        }
                        break;
                    }

            }

        })

        window.onunload = () => {
            client.end();
        };
    };
})();
