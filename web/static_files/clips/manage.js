function updateClipEnable(clip_id, enable) {
    var xhttp;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("status").innerHTML = this.responseText;
        }
    };
    xhttp.open("POST", "/clips/enable", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("clip_id=" + clip_id + "&enable=" + enable);
}
