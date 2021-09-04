//Global Variables
setting_QuestionCountDown = 60;
setting_AnswerCountDown = 15;
setting_DelayBetweenQuestions = 10;
countDownSeconds = setting_QuestionCountDown;

var questionOBJ;

//Grab the API Key and build URL for requesting questions
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const api_key = urlParams.get('key')
yourUrl = "/trivia/get_question?key=" + api_key;

// Global Timers
var displayAnswerTimer;
var myTimer;

var endTriviaNotified = false
document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === 'hidden') {
        if (!endTriviaNotified) {
            endTriviaNotified = true;
            navigator.sendBeacon('/trivia/end?key=' + api_key);
        }
    }
});

function displayAnswer() {
    countDownSeconds--;
    document.getElementById("timer").innerHTML = "<h1>" + countDownSeconds + "</h1>";
    if (countDownSeconds <= 0) {
        clearInterval(displayAnswerTimer);
        console.log("time for the next question");
        document.getElementById("explain").style.visibility = "hidden";
        //document.getElementById("timer").style.visibility = "visible";
        delay_between_questions();

        //getAQuestion();
    }
}

function countDownTimer() {
    countDownSeconds--;
    //    console.log(countDownSeconds);
    document.getElementById("timer").innerHTML = "<h1>" + countDownSeconds + "</h1>";
    if (countDownSeconds <= 0) {
        console.log("Question timer expired");
        clearInterval(myTimer);

        // setup Answer
        countDownSeconds = setting_AnswerCountDown;
        displayAnswerTimer = setInterval(displayAnswer, 1000);
        document.getElementById("explain").style.visibility = "visible";
        // document.getElementById("timer").style.visibility = "hidden";
        document.getElementById("correct-answer").className = "correct-answer";
        // the_answer.id="correct-answer";
        //the_answer.className = "correct-answer";
    }
}

function Get(yourUrl) {
    var Httpreq = new XMLHttpRequest(); // a new request
    Httpreq.open("GET", yourUrl, false);
    Httpreq.send(null);
    return Httpreq.responseText;
}

function shuffle(array) {
    //Shuffling moved to python script.
    // var currentIndex = array.length, temporaryValue, randomIndex;

    // // While there remain elements to shuffle...
    // while (0 !== currentIndex) {

    //   // Pick a remaining element...
    //   randomIndex = Math.floor(Math.random() * currentIndex);
    //   currentIndex -= 1;

    //   // And swap it with the current element.
    //   temporaryValue = array[currentIndex];
    //   array[currentIndex] = array[randomIndex];
    //   array[randomIndex] = temporaryValue;
    // }

    return array;
}

function processResponse(obj) {

    var audio = new Audio('/trivia/play.wav?key=' + api_key)
    audio.play()

    // the question
    document.getElementById("question").innerHTML = "<h2>" + obj.text + "</h2>";

    // clear the questions
    document.getElementById("answers").innerHTML = "";

    // the explanation
    document.getElementById("explain").innerHTML = obj.explain;
    document.getElementById("explain").style.visibility = "hidden";

    // answers
    var answerOBJs = obj.answers;

    // generate an array of keys and then randomize them
    // so the answers come out "random"
    var answer_objs_key_count = Object.keys(answerOBJs).length;
    var answer_key_order = [];
    console.log("Length of answer objs: " + answer_objs_key_count);
    for (x = 0; x < answer_objs_key_count; x++)
        answer_key_order[x] = x;
    console.log("Going to check these: " + answer_key_order.toString());
    var random_key_order = shuffle(answer_key_order);
    console.log("Now we got: " + random_key_order.toString());

    //for (var answer_key of Object.keys(answerOBJs)) {
    var answer_letter_counter = 65;
    for (this_random_key = 0; this_random_key < answer_objs_key_count; this_random_key++) {
        var answer_key = random_key_order[this_random_key] + 1;
        var answer_text = answerOBJs[answer_key].text;
        if (answerOBJs[answer_key].is_answer == '1')
            var is_answer = 1;
        else
            var is_answer = 0;
        //console.log(answer_key);
        //console.log(answer_text);
        //console.log(is_answer);

        // convert 1-x to letters
        var answer_letter = String.fromCharCode(answer_letter_counter++);

        // generate the HTML
        var answer_section = document.createElement("div");
        var the_answer = document.createElement("h2");
        var answer_node = document.createTextNode(answer_letter + ": " + answer_text);
        answer_section.id = "answer";

        // need to re-think how to do this... maybe reload the text
        // and have a flag?
        if (is_answer)
            the_answer.id = "correct-answer";
        //the_answer.className = "correct-answer";

        answer_section.appendChild(the_answer).appendChild(answer_node);
        document.getElementById("answers").appendChild(answer_section);

    }
}

function questionTimerStart() {
    // reset the clock
    countDownSeconds = setting_QuestionCountDown;
    myTimer = setInterval(countDownTimer, 1000);
}

function getAQuestion() {
    if (document.visibilityState === 'visible') {
        console.log("Getting a question");
        //are we on the pi or are we local?
        if (yourUrl == "") {
            console.log("Looks like we are local...");
            //var exampleJSON = '{"text":"Who invented the transistor?", "answers": {"1": {"text": "William Shockley", "is_answer": 1}, "2": {"text": "Alexander Bell", "is_answer": 0}, "3": {"text": "Daniel Bernoulli", "is_answer": 0}, "4": {"text": "Michael Jacob", "is_answer": 0}}, "explain": "Shockley, Bardeen, and Brattain were scientists who discovered the transistor effect at Bell Labs.", "last_used_date": "", "created_date": "2019-11-24", "created_by": "baldengineer", "reference": "https://en.wikipedia.org/wiki/William_Shockley"}';
            var exampleJSON = '{"text": "Radio Direction Ranging is also known as:", "answers": {"1": {"text": "LiDAR", "is_answer": 0}, "2": {"text": "RADAR", "is_answer": 1}, "3": {"text": "Foxing", "is_answer": 0}, "4": {"text": "Futzing", "is_answer": 0}}, "explain": "The first range finding experiment occured in 1924.", "last_used_date": "", "created_date": "2019-11-24", "created_by": "baldengineer", "reference": "http://www.ob-ultrasound.net/radar.html"}';
            questionOBJ = JSON.parse(exampleJSON);
        } else {
            console.log("Looks like we are on the Pi... Mmmmm Pie...");
            var response = Get(yourUrl);
            console.log(response);
            questionOBJ = JSON.parse(response);
        }

        processResponse(questionOBJ);
        questionTimerStart();
    }

}

function delay_between_questions() {
    // the question
    document.getElementById("question").innerHTML = "<h2>Next question coming up..</h2>";

    // clear the questions
    document.getElementById("answers").innerHTML = '<div id="answer">To participate in trivia, respond in chat with A, B, C, D, etc..</div>';

    // the explanation
    document.getElementById("explain").innerHTML = "";
    document.getElementById("explain").style.visibility = "hidden";

    //the timer
    countDownSeconds = setting_DelayBetweenQuestions;
    myTimer = setInterval(next_question_timer, 1000);

}
function next_question_timer() {
    countDownSeconds--;
    //    console.log(countDownSeconds);
    document.getElementById("timer").innerHTML = "<h1>" + countDownSeconds + "</h1>";
    if (countDownSeconds <= 0) {
        console.log("Next question timer expired");
        clearInterval(myTimer);
        if (document.visibilityState === 'visible') {
            location.reload();
        }
    }

}
