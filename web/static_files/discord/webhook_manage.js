function editUrl(setting_name, url) {
    var setting = document.getElementById("url_" + setting_name);
    setting.onclick = "";
    setting.innerHTML = `
    <form action="">
        <input size=120 type="text" id="edit_${setting_name}" value="${url}"></input>
        <button type="button" onclick="saveUrlEdit('${setting_name}');">💾</button>
    </form >
    `;
}

function saveUrlEdit(setting_name) {
    //document.getElementById('status').innerHTML = 'updated ' + setting_name;
    var entry_div = document.getElementById('url_' + setting_name);
    var textbox = document.getElementById("edit_" + setting_name);

    //TODO Setting the onclick isn't actually working correctly here for some reason, but it's not a show stopper
    //entry_div.onclick = function () { editUrl(setting_name, textbox.value); }
    entry_div.innerText = textbox.value;

    var xhttp;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("status").innerHTML = this.responseText;
        }
    };
    xhttp.open("POST", "/discord/webhook_manage/save", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("webhook_name=" + setting_name + "&webhook_url=" + textbox.value);
}
