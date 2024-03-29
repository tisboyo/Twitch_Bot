function sendKeyBackToServer() {
    var oauthHash = location.hash.substr(1);
    var accessToken = oauthHash.substr(oauthHash.indexOf('access_token=')).split('&')[0].split('=')[1];
    var state = oauthHash.substr(oauthHash.indexOf('state=')).split('&')[0].split('=')[1];
    var scope = oauthHash.substr(oauthHash.indexOf('scope=')).split('&')[0].split('=')[1];
    var token_type = oauthHash.substr(oauthHash.indexOf('token_type=')).split('&')[0].split('=')[1];

    var xhttp;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {

            var obj = JSON.parse(this.responseText);
            document.getElementById("message").innerHTML = obj.message;
            document.cookie = 'oauth_message=' + obj.message + ";path=/";
            location.href = obj.redirect;
        }
    };

    if (accessToken) {
        xhttp.open("POST", "/twitch/oauth/save", true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send("access_token=" + accessToken + "&type=" + state);

    } else {
        document.getElementById('message').innerText = "Access token not received."
        document.cookie = 'oauth_message=Access token not received.';
        location.href = '/twitch/oauth.html';
    }
}
window.onload = sendKeyBackToServer;
