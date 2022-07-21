function getCookie(name) {
var matches = document.cookie.match(new RegExp(
"(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
))
return matches ? decodeURIComponent(matches[1]) : undefined 
}
function setCookie(name, value, props) {
props = props || {}
var exp = props.expires
if (typeof exp == "number" && exp) {
var d = new Date()
d.setTime(d.getTime() + exp*1000)
exp = props.expires = d
}
if(exp && exp.toUTCString) { props.expires = exp.toUTCString() }

value = encodeURIComponent(value)
var updatedCookie = name + "=" + value
for(var propName in props){
updatedCookie += "; " + propName
var propValue = props[propName]
if(propValue !== true){ updatedCookie += "=" + propValue }
}
document.cookie = updatedCookie
}
function deleteCookie(name) {
setCookie(name, null, { expires: -1 })
}

///////////////////////////////////

if (!vkConnect.isEmbedded() && !vkConnect.isIframe() && !vkConnect.isStandalone() && vkConnect.isWebView()) {
    window.location.href="https://vk.com/app8218052";
}

/////////////////////////////

var api_url = "https://visionbot.ru/tod/api/settings"+window.location.search;

function got_settings(data) {
    $("#dch").checked = data.dch;
    $("#gg").checked = data.gg;
    $("#ul").checked = data.ul;
    if (data.locked) {
        Swal.fire("Ошибка", "Изменение настроек во время игры невозможно.<br> Дождитесь окончания игры в беседе.", "error");
    }
}

function request_settings(change) {
    var method = "GET";
    if(!!change) {
        method = "POST";
    }
    var fd = null;
    let f = $("#anketaform")[0];
    if(method == "POST") {
        fd = new FormData(f);
    }
    let x = new XMLHttpRequest();
    x.open(method, api_url);
    x.onreadystatechange = function() {
        if(x.readyState == 4 && x.status == 200) {
            got_settings(JSON.parse(x.responseText));
        }
    };
    x.send(fd);
}

$(request_settings);

function change_settings() {
    return request_settings(true);
}
$(function() {
    $("form#anketaform input").change(function(){
        change_settings();
    });
});
