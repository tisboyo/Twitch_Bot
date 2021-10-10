function updateElements() {
    document.getElementById('irc_button').onclick = function () {
        location.href = "/twitch/oauth/start/irc"
    }

    document.getElementById('pubsub_button').onclick = function () {
        location.href = "/twitch/oauth/start/pubsub"
    }

    var cookie = getCookie('oauth_message');
    var message = cookie ? cookie : '';

    document.getElementById('message').innerText = message;
    eraseCookie('oauth_message');

}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function eraseCookie(name) {
    document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

window.onload = updateElements;
