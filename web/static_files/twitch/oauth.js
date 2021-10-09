function updateElements() {
    document.getElementById('irc_button').onclick = function () {
        location.href = "/twitch/oauth/start_irc"
    }

    document.getElementById('pubsub_button').onclick = function () {
        location.href = "/twitch/oauth/start_pubsub"
    }
}

window.onload = updateElements;
