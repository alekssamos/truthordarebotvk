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

function main(res) {
    console.log("OK");
    console.log(res);
}
function errorHandler(error) {
    console.log("error");
    console.log(error);
}
p=vkConnect.sendPromise("VKWebAppGetAuthToken", {
    "app_id": 8218052,
    "scope": ""
});

p.then(main).catch(errorHandler);
