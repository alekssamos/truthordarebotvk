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

if (!vkConnect.isEmbedded() && !vkConnect.isIframe() && !vkConnect.isStandalone() && !vkConnect.isWebView()) {
    window.location.href="https://vk.com/app8218052";
}

/////////////////////////////

var api_url = "https://visionbot.ru/tod/api/settings"+window.location.search;

function dummy(){}

function got_settings(data, changed) {
    $("#dch")[0].checked = data.dch;
    $("#gg")[0].checked = data.gg;
    $("#ul")[0].checked = data.ul;
    if($("#anketaform").hasClass("hide")) $("#anketaform").removeClass("hide");
    if(!$("div.loader").hasClass("hide")) $("div.loader").addClass("hide");
    if (!!changed && data.locked) {
        vkBridge.send("VKWebAppTapticNotificationOccurred", {"type": "error"}).then(dummy).catch(dummy);
        Swal.fire("Ошибка", "Изменение настроек во время игры невозможно.<br> Дождитесь окончания игры в беседе.", "error");
    }
}

function on_xhr_error(x) {
    resp_clean = x.responseText.replace('<', '&lt;').replace('>', '&gt;');
    vkBridge.send("VKWebAppTapticNotificationOccurred", {"type": "error"}).then(dummy).catch(dummy);
    Swal.fire("Ошибка запроса", "Не удалось выполнить запрос.<br> <code>status="+x.status+", readyState="+x.readyState+"</code><br>responseText:<pre>"+resp_clean+"</pre>", "error");
}

function request_settings(change) {
    var method = "GET";
    if(!!change) {
        method = "POST";
    }
    var fd = null;
    if(method == "POST") {
        fd = $("#anketaform").serialize();
    }
    if($("div.loader").hasClass("hide")) $("div.loader").removeClass("hide");
    let x = new XMLHttpRequest();
    x.open(method, api_url, true);
    x.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    x.onerror=function(){ on_xhr_error(x); };
    x.ontimeout=function(){ on_xhr_error(x); };
    x.onreadystatechange = function() {
        if(x.status > 399) { on_xhr_error(x); }
        if(x.readyState == 4 && x.status == 200) {
            got_settings(JSON.parse(x.responseText), (method == "POST"));
        }
    };
    x.send(fd);
}

/////////////////////

vkBridge.send('VKWebAppInit').then(function(){
    request_settings(false);
});

/////////////////////

function change_settings() {
    vkBridge.send("VKWebAppTapticSelectionChanged", {}).then(dummy).catch(dummy);
    return request_settings(true);
}

$(function() {
    $("form#anketaform input").change(function(){
        window.setTimeout(        change_settings, 10);
    });
});

vkBridge.subscribe(function(event){
    if (!event.detail) {
        return;
    }
    switch (event.type) {
        case "VKWebAppLocationChanged":
        case "VKWebAppChangeFragment":
            console.log("hash event");
            hash = event.data.location;
            if(hash.length < 2) { break; }
            $('a[href="#' + hash + '"]').trigger('click');
        break;
        case "VKWebAppViewRestore":
            console.log("restore event");
            request_settings(false);
        break;
    }
});

$('a[data-toggle="tab"]').click(function(event){
    console.log("change hash");
    hash = event.target.hash.replace("#", "");
    vkBridge.send("VKWebAppSetLocation", {"location": hash});
});
