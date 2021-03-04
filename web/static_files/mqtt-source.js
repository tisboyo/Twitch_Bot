(function () {
    //Not a great coder look at all my globals
    var ActivePoll,
        PollTitle,
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
            client = mqtt.connect('wss://' +params.url +':'+params.port, {
            clientId: 'pollpage'+Math.random().toString(36).slice(2),
            username: params.username,
            password: params.password
        });


        client.on('connect', function () {
            client.subscribe('stream/poll/setup', function (err) {

            });
            client.subscribe('stream/poll/data', function (err) {

            });

        })

        client.on('message', function (topic, message) {
            // message is Buffer
            var data = JSON.parse(message);

            switch (topic) {
                case "stream/poll/setup":
                    { //{"title": "Poll Title 4", "total_duration": 28, "choices": ["Choice 1", "Choice 2", "Choice 3"], "active": false, "sub_multiplier": 0}
                        if(!data.active){
                            PollTitle = "";
                            ChoiceCount = "";
                            SubMultiplier = "";
                            ActivePoll = "";    
                            update_frequency = "1"
                            let root = document.documentElement;
                            root.style.setProperty('--fade',0);
                            setTimeout(function(){
                                document.body.innerHTML = '';
                            }, 1000);
                            
                            break;
                        }
                        PollTitle = data.title;
                        ChoiceCount = data.choices.length;
                        SubMultiplier = data.sub_multiplier;
                        ActivePoll = data.active;
                        //Make BigBoiBox that holed the actual poll
                        let root = document.documentElement;
                        root.style.setProperty('--update-frequency',data.update_frequency+"s");
                        let big_boi = document.createElement("div");
                        big_boi.setAttribute("id","poll");
                        big_boi.setAttribute("class","big-boi-container");
                        document.body.appendChild(big_boi);

                        // Create Poll header
                        let title = document.createElement( 'div' );
                        title.setAttribute('class','pollHeader');
                        title.innerHTML = PollTitle;
                        
                        let poll = document.getElementById("poll"); 
                        poll.appendChild(title);

                        for(let i in data.choices){
                            let container = document.createElement( 'div' );
                            container.setAttribute('class','outer-div');
                            container.setAttribute('id','pollElement-'+i);
                            poll.appendChild(container);                        
                            let elem = document.createElement( 'div' );
                            elem.setAttribute('class','info-div');
                            elem.setAttribute('id','pollElement-'+i);
                            container.appendChild(elem);
                            let choiceelem = document.createElement('div');
                            choiceelem.innerHTML = data.choices[i];
                            choiceelem.setAttribute('class','choice');
                            choiceelem.setAttribute('id','choice-'+i);
                            elem.appendChild(choiceelem);
                            let voteelem = document.createElement('div');
                            voteelem.innerHTML= '';
                            voteelem.setAttribute('class','count');
                            voteelem.setAttribute('id','votes-'+i);
                            voteelem.innerHTML = 0;
                            elem.appendChild(voteelem);       
                            let progress = document.createElement('div');
                            progress.innerHTML= '';
                            progress.setAttribute('class','bar-div');
                            progress.setAttribute('id','bar-div-'+i);
                            container.appendChild(progress);                         
                        }

                       root.style.setProperty('--fade',1);
                        break;
                    }
                case "stream/poll/data":
                    { //{"seconds_left": 4.5, "votes": {"1": 1, "2": 2, "3": 3}, "done": false}
                    if(ActivePoll){
                        let total = 0;
                        if(data.done){
                            //Grey out all non winners
                            for(i in data.votes){
                                let vote = document.getElementById('bar-div-'+(i-1));
                                vote.style.setProperty('filter','saturate(0)')
                            }
                            let winner = Object.keys(data.votes).reduce((a, b) => data.votes[a] > data.votes[b] ? a : b)-1;
                            let vote = document.getElementById('bar-div-'+winner);
                            vote.style.setProperty('filter','saturate(1)');
                            break;
                        }
                        for(i in data.votes){
                            total += data.votes[i];
                        }
                        for(i in data.votes)
                        {
                            //TODO Figureout "better looking" scaling. 
                            let vote = document.getElementById('votes-'+(i-1));
                            vote.innerHTML = data.votes[i];
                            let choiceline = document.getElementById('bar-div-'+(i-1));    
                            choiceline.style.setProperty('width', Math.round((data.votes[i]/total)*100) + '%');
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
