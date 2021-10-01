function editUrl(setting_name, url) {
    var setting = document.getElementById("url_" + setting_name);
    setting.onclick = "";
    setting.innerHTML = `
    <form>
        <input size=120 type="text" id="edit_${setting_name}" value="${url}">
    </form >
    `;
    //document.getElementById('edit_' + setting_name).onblur = saveUrlEdit(setting_name, function () { document.getElementById('edit_' + setting_name).value; });
}

function saveUrlEdit(setting_name, url) {
    document.getElementById('status').innerHTML = 'updated ' + setting_name;
    var setting = document.getElementById("url_" + setting_name);
    setting.onclick = `editUrl('${setting_name}', '${url}')`;
    setting.innerHTML = url
}
