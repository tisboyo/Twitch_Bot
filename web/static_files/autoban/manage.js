function updateRegExEnable(regex_id, enable) {
    var xhttp;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("status").innerHTML = this.responseText;
        }
    };
    xhttp.open("POST", "/autoban/manage/enable", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("regex_id=" + regex_id + "&enable=" + enable);
}

function deleteRegEx(regex_id, row_id) {
    var xhttp;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("regex_table").deleteRow(row_id);
            document.getElementById("status").innerHTML = this.responseText;
        }
    };

    var result = confirm("Do you really want to delete this pattern?")
    if (result == true) {
        xhttp.open("POST", "/autoban/manage/delete", true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send("regex_id=" + regex_id);
    }

}
